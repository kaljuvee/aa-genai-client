import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import OpenAI
import tiktoken

# Load environment variables
load_dotenv()

# Azure Cognitive Search setup
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")

# OpenAI setup
openai_api_key = os.getenv("OPENAI_API_KEY")

# Search and chunking configuration
TOP_N = 3
MAX_TOKENS = 12000  # Safe limit below model's context length
CHUNK_OVERLAP = 100  # Number of tokens to overlap between chunks

def create_clients(index_name):
    search_client = SearchClient(search_endpoint, index_name, AzureKeyCredential(search_key))
    openai_client = OpenAI(api_key=openai_api_key)
    return search_client, openai_client

def load_system_prompt():
    with open("prompts/system_prompt.md", "r") as f:
        return f.read().strip()

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def chunk_context(context, max_tokens):
    """Split context into chunks that fit within token limit."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(context)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for token in tokens:
        current_chunk.append(token)
        current_length += 1
        
        if current_length >= max_tokens:
            chunks.append(encoding.decode(current_chunk))
            # Keep last CHUNK_OVERLAP tokens for context continuity
            current_chunk = current_chunk[-CHUNK_OVERLAP:]
            current_length = len(current_chunk)
    
    if current_chunk:
        chunks.append(encoding.decode(current_chunk))
    
    return chunks

def search_documents(search_client, query):
    results = search_client.search(query, top=TOP_N)
    return [result['content'] for result in results]

def answer_question(search_client, openai_client, question, system_prompt, model_name):
    relevant_docs = search_documents(search_client, question)
    
    if not relevant_docs:
        return "I don't have enough information to answer that question. Could you please provide more specific details?"
    
    # Combine all retrieved documents into context
    full_context = "\n\n".join(relevant_docs)
    
    # Calculate available tokens (accounting for system prompt, question, and response)
    system_tokens = count_tokens(system_prompt)
    question_tokens = count_tokens(question)
    buffer_tokens = 1000  # Reserve tokens for response and formatting
    available_tokens = MAX_TOKENS - system_tokens - question_tokens - buffer_tokens
    
    # Split context into manageable chunks
    context_chunks = chunk_context(full_context, available_tokens)
    
    # Process each chunk and accumulate responses
    all_responses = []
    
    for chunk in context_chunks:
        prompt = f"""
        Context: {chunk}

        Question: {question}

        Answer the question based on the context provided. If the answer is not in the context, ask the user to provide more specific details.
        """

        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        
        all_responses.append(response.choices[0].message.content.strip())
    
    # Combine all responses
    if len(all_responses) == 1:
        return all_responses[0]
    else:
        # If multiple chunks were processed, summarize the responses
        summary_prompt = f"""
        I have received multiple responses to the question: {question}

        Responses:
        {'\n'.join(all_responses)}

        Please provide a coherent summary of these responses.
        """
        
        final_response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=150
        )
        
        return final_response.choices[0].message.content.strip()
