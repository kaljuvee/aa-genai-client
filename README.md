# Angle American Gen AI POC - Data Science Module

This project is an Gen AI focuses on document indexing and querying using Azure AI Search and Azure OpenAI.

## 1. Setting up the environment and dependencies

To set up the environment and install the necessary dependencies, follow these steps:

1. Ensure you have Python 3.7+ installed on your system.
2. Clone this repository:
   ```
   git clone https://<username>@dev.azure.com/AngloDevOps/APC%20GenAI%20PoC/_git/APC-GenAI-Appt
   cd apc
   ```
3. Create a virtual environment:
   ```
   cd datascience
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## 2. Configuring environment variables

Before running the scripts, you need to configure the following environment variables:

1. Create a `.env` file in the root directory of the project.
2. Add the following variables to the `.env` file:

   ```
   AZURE_SEARCH_ENDPOINT=your_azure_search_endpoint
   AZURE_SEARCH_KEY=your_azure_search_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_KEY=your_azure_openai_key
   AZURE_OPENAI_DEPLOYMENT=your_azure_openai_deployment
   ```

   Replace the placeholder values with your actual Azure AI Search and Azure OpenAI credentials.

These environment variables are accessed in the scripts using `os.getenv()` after loading them with `load_dotenv()`.

## 3. Description of tasks/create_index.py

The `tasks/create_index.py` script is responsible for creating and managing the search index using Azure AI Search. Here's what it does:

1. Connects to Azure AI Search using the configured endpoint and key.
2. Creates a new search index with custom analyzers for improved text processing.
3. Reads PDF files from the `docs` directory as specified in `config/index_metadata.json`.
4. Extracts text content from the PDF files.
5. Indexes the extracted content in the Azure AI Search index.
6. Provides feedback on the number of documents successfully indexed.

To run the script, use the following command:

```
python tasks/create_index.py
```

## 4. Description of tasks/query.py

The `tasks/query.py` script allows you to query the indexed documents and get answers using Azure OpenAI. Here's what it does:

1. Connects to Azure AI Search and Azure OpenAI using the configured credentials.
2. Provides an interactive interface to ask questions.
3. Searches the indexed documents for relevant content based on the question.
4. Uses Azure OpenAI to generate an answer based on the retrieved content.

To run the script, use the following command:

```
python tasks/query.py
```

## 5. Configuration

The `config/index_metadata.json` file contains the mapping between index names and the PDF files to be indexed. You can modify this file to add or remove documents from the indexing process.

## Requirements

The project dependencies are listed in the `requirements.txt` file. The main libraries used are:

- openai
- python-dotenv
- azure-search-documents
- azure-ai-textanalytics
- PyPDF2

Make sure to install these dependencies using the instructions in the "Setting up the environment and dependencies" section.
