import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import OpenAI

# Load environment variables
load_dotenv()

# Azure Cognitive Search setup
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")

# OpenAI setup
openai_api_key = os.getenv("OPENAI_API_KEY")

def create_clients(index_name):
    search_client = SearchClient(search_endpoint, index_name, AzureKeyCredential(search_key))
    openai_client = OpenAI(api_key=openai_api_key)
    return search_client, openai_client

def load_system_prompt():
    with open("prompts/system_prompt.md", "r") as f:
        return f.read().strip()

def search_documents(search_client, query):
    results = search_client.search(query)
    return [result['content'] for result in results]

def answer_question(search_client, openai_client, question, system_prompt, model_name):
    relevant_docs = search_documents(search_client, question)
    
    if not relevant_docs:
        return "I don't have enough information to answer that question. Could you please provide more specific details?"
    
    context = relevant_docs[0]  # Use the first document as context

    prompt = f"""
    Context: {context}

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

    return response.choices[0].message.content.strip()
