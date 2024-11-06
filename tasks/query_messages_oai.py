import os
import sys
import json
import logging
import pandas as pd
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import OpenAI

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.telemetry_util import load_and_filter_data, get_treshold_violations, format_gains_map

# Load environment variables
load_dotenv()

# Global variables
TOP_N = 10  # Number of top documents to retrieve for context
MODEL_NAME = "gpt-4o"  # Specify the model name here

# Azure Cognitive Search setup
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
index_name = "apc-j140-bin-005c"  # Specify the index name here
apc = 'APC-J140_BIN_005C'
datasource = os.path.join(parent_dir, 'data', 'ADX_Export_APC_Tag_Values.csv')
gainsmap = os.path.join(parent_dir, 'data', 'SIS-JIG T-Crushing PWO gain map.csv')

# OpenAI setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create clients
search_client = SearchClient(search_endpoint, index_name, AzureKeyCredential(search_key))

# Load system prompt from file
with open(os.path.join(parent_dir, "prompts", "system_prompt.md"), "r") as f:
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

    response = client.chat.completions.create(
        model=MODEL_NAME,  # Use the global MODEL_NAME variable
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500  # Increased from 150 to 500
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

    # 3. Load and format gains map
    logging.info(f"Loading gains map from {gainsmap}")
    gains_df = pd.read_csv(gainsmap)
    logging.info("Formatting gains map")
    formatted_gains_df = format_gains_map(gains_df)

    # 4. Iterate through violations and form questions
    output_file = "reports/system_alerts_enriched.json"
    logging.info(f"Processing violations and writing to {output_file}")
    
    # Initialize the file with an empty list
    with open(output_file, 'w') as f:
        json.dump([], f)

    for index, row in violations_df.iterrows():
        violation_message = row['message']
        logging.info(f"Processing violation {index + 1}/{len(violations_df)}: {violation_message}")

        # Get the corresponding gains information
        tag_name = row['IDX_TagName']
        #gains_info = formatted_gains_df[formatted_gains_df['Variable Name'] == tag_name].to_dict('records')
        gains_info = formatted_gains_df.head(1).to_dict('records')
        print("GAINS INFO:", gains_info)
        # Format gains information as a string if available
        gains_context = ""
        if gains_info:
            gains_context = "\n".join([f"{k}: {v}" for item in gains_info for k, v in item.items()])
            follow_up_question = f"{violation_message}\n\nAdditional context:\n{gains_context}\n\nPlease give reasoning what could be done or describe the situation in further detail, considering the additional context provided."
        else:
            follow_up_question = f"{violation_message}\n\nPlease give reasoning what could be done or describe the situation in further detail."

        follow_up_answer = answer_question(follow_up_question)

        # Create a dictionary for the current violation
        alert_info = {
            "original_message": violation_message,
            "gains_context": gains_context if gains_context else "No additional context available",
            "follow_up_question": follow_up_question,
            "follow_up_answer": follow_up_answer
        }

        # Append the current alert_info to the JSON file
        with open(output_file, 'r+') as f:
            data = json.load(f)
            data.append(alert_info)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

        logging.info(f"Processed and appended violation {index + 1}/{len(violations_df)}")

    logging.info("Main function completed successfully")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
