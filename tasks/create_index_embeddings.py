import os
import json
import logging
import numpy as np
from typing import List, Dict
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    HnswVectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
    VectorSearchField,
)
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Add new constants
CHUNK_SIZE = 1000  # Approximate number of characters per chunk
CHUNK_OVERLAP = 100  # Number of characters to overlap between chunks
EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI embedding model to use
EMBEDDING_DIMENSION = 1536  # OpenAI ada-002 embedding dimension
MAX_TOKENS_PER_CHUNK = 8191  # OpenAI's token limit for text-embedding-ada-002

def create_search_index(index_name: str):
    """Create search index with vector search capability."""
    try:
        # Define vector search configuration
        vector_search = VectorSearch(
            algorithms=[
                HnswVectorSearchAlgorithmConfiguration(
                    name="hnsw-config",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-config",
                )
            ]
        )

        # Define fields including vector field for embeddings
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="sourcefile", type=SearchFieldDataType.String),
            SimpleField(name="chunk_id", type=SearchFieldDataType.Int32),
            VectorSearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                dimension=EMBEDDING_DIMENSION,
                vector_search_profile_name="vector-profile"
            )
        ]
        
        index = SearchIndex(
            name=index_name,
            fields=fields,
            vector_search=vector_search
        )
        
        result = search_index_client.create_or_update_index(index)
        logging.info(f"Search index '{index_name}' created successfully")
        return result
    except Exception as e:
        logging.error(f"Error creating search index: {str(e)}")
        raise

def chunk_text(text: str) -> List[str]:
    """Split text into smaller chunks with overlap."""
    chunks = []
    start = 0
    
    while start < len(text):
        # Find the end of the chunk
        end = start + CHUNK_SIZE
        
        # If we're not at the end of the text, try to break at a sentence
        if end < len(text):
            # Look for sentence endings (.!?) within the last 100 characters of the chunk
            last_period = text.rfind('.', end - 100, end)
            last_exclaim = text.rfind('!', end - 100, end)
            last_question = text.rfind('?', end - 100, end)
            
            # Find the latest sentence ending
            break_point = max(last_period, last_exclaim, last_question)
            
            if break_point != -1:
                end = break_point + 1
        else:
            end = len(text)
        
        # Extract the chunk
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move the start pointer, accounting for overlap
        start = end - CHUNK_OVERLAP
    
    return chunks

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_embedding(text: str) -> List[float]:
    """Get embedding from OpenAI API with retry logic."""
    response = openai.Embedding.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response['data'][0]['embedding']

def read_and_index_document(index_name: str, document_file: str, document_content: str):
    """Read document, chunk it, get embeddings, and index in Azure Search."""
    try:
        # Split content into chunks
        chunks = chunk_text(document_content)
        logging.info(f"Split document into {len(chunks)} chunks")
        
        # Initialize SearchClient for this specific index
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=search_credential,
            api_version="2023-10-01-Preview"
        )
        
        # Process and upload chunks in batches
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            documents = []
            
            for chunk_id, chunk in enumerate(batch_chunks, start=i):
                # Get embedding for the chunk
                embedding = get_embedding(chunk)
                
                # Create document
                document = {
                    "id": f"{encode_filename(document_file)}_{chunk_id}",
                    "content": chunk,
                    "sourcefile": document_file,
                    "chunk_id": chunk_id,
                    "content_vector": embedding
                }
                documents.append(document)
            
            # Upload batch
            result = search_client.upload_documents(documents)
            succeeded = sum(1 for r in result if r.succeeded)
            failed = sum(1 for r in result if not r.succeeded)
            logging.info(f"Batch indexing complete. Succeeded: {succeeded}, Failed: {failed}")
        
        return search_client
    except Exception as e:
        logging.error(f"Error in read_and_index_document for {index_name}: {str(e)}")
        raise

async def semantic_search(index_name: str, query: str, top_k: int = 3):
    """Perform semantic search using embeddings."""
    try:
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=search_credential,
            api_version="2023-10-01-Preview"
        )
        
        # Get query embedding
        query_embedding = get_embedding(query)
        
        # Perform vector search
        results = search_client.search(
            search_text=None,
            vector=query_embedding,
            vector_fields="content_vector",
            select=["content", "sourcefile", "chunk_id"],
            top=top_k
        )
        
        return [{"content": doc["content"], 
                "score": doc["@search.score"],
                "source": doc["sourcefile"],
                "chunk_id": doc["chunk_id"]} 
                for doc in results]
    except Exception as e:
        logging.error(f"Error in semantic search: {str(e)}")
        raise

def main():
    logging.info("Starting the enhanced index creation and document upload process")
    
    try:
        # Initialize OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Read the configuration file
        with open(CONFIG_FILE, 'r') as config_file:
            index_config = json.load(config_file)
        
        for _, index_data in index_config.items():
            index_name = f"{index_data['index_name']}_embeddings"
            document_list = [doc.strip() for doc in index_data['document_list'].split(',')]
            
            # Delete existing index if it exists
            delete_index_if_exists(index_name)
            
            # Create enhanced search index with vector search
            create_search_index(index_name)
            
            # Process each document
            for document_file in document_list:
                content = read_document(document_file)  # Your existing document reading function
                read_and_index_document(index_name, document_file, content)
        
        logging.info("Enhanced index creation and document upload complete.")
    except Exception as e:
        logging.error(f"An error occurred during the main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
