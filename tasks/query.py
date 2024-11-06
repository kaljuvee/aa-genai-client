import os
import json
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from utils.telemetry_util import load_and_filter_data, get_treshold_violations
# Load environment variables
load_dotenv()

# Global variables
TOP_N = 10  # Number of top documents to retrieve for context

# Azure Cognitive Search setup
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
#index_name = "apc-j141-lic-005c"
index_name = "apc-j140-bin-005c"  # Specify the index name here
# index_name = "sishen-jig-separator-tertiary-crushing-pwo"  # Specify the index name here
apc = 'APC-J140_BIN_005C'
datasource = 'data/ADX_Export_APC_Tag_Values.csv'

# Azure OpenAI setup
openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_key = os.getenv("AZURE_OPENAI_KEY")
openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Create clients
search_client = SearchClient(search_endpoint, index_name, AzureKeyCredential(search_key))
openai_client = AzureOpenAI(
    api_key=openai_key,
    api_version="2023-05-15",
    azure_endpoint=openai_endpoint
)

# Load system prompt from file
with open("prompts/system_prompt.md", "r") as f:
    system_prompt = f.read().strip()

def search_documents(query):
    results = search_client.search(query, top=TOP_N)
    return [result['content'] for result in results]

def answer_question(question):
    relevant_docs = search_documents(question)
    
    if not relevant_docs:
        return "I don't have enough information to answer that question. Could you please provide more specific details?"
    
    context = "\n".join(relevant_docs)  # Use all retrieved documents as context

    prompt = f"""
    Context: {context}

    Question: {question}

    Answer the question based on the context provided. If the answer is not in the context, ask the user to provide more specific details.
    """

    response = openai_client.chat.completions.create(
        model=openai_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

def main():
    logging.info("Starting the main function")

    # 1. Load filtered data
    logging.info(f"Loading filtered data from {datasource}")
    filtered_df = load_and_filter_data(datasource, apc)

    # 2. Get threshold violations
    logging.info("Calculating threshold violations")
    violations_df = get_treshold_violations(filtered_df)

    # 3. Iterate through violations and form questions
    enriched_alerts = []
    for _, row in violations_df.iterrows():
        violation_message = row['message']
        logging.info(f"Processing violation: {violation_message}")

        # Form a new question for further details
        follow_up_question = f"{violation_message} Please give reasoning what could be done or describe the situation in further detail."
        follow_up_answer = answer_question(follow_up_question)

        # Create a dictionary for the current violation
        alert_info = {
            "original_message": violation_message,
            "follow_up_question": follow_up_question,
            "follow_up_answer": follow_up_answer
        }
        enriched_alerts.append(alert_info)

    # 4. Write enriched alerts to a JSON file
    output_file = "reports/system_alerts_enriched.json"
    logging.info(f"Writing enriched alerts to {output_file}")
    with open(output_file, 'w') as f:
        json.dump(enriched_alerts, f, indent=2)

    logging.info("Main function completed successfully")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
