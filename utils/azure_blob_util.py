from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

def get_blob_client():
    """
    Creates a BlobServiceClient using environment variables.
    Supports both connection string and account key methods.
    """
    # Load environment variables
    load_dotenv()
    
    # Option 1: Using Connection String
    if os.getenv('AZURE_STORAGE_CONNECTION_STRING'):
        return BlobServiceClient.from_connection_string(
            os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        )
    
    # Option 2: Using Account Name and Key
    elif os.getenv('AZURE_STORAGE_ACCOUNT') and os.getenv('AZURE_STORAGE_KEY'):
        account_url = f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net"
        return BlobServiceClient(
            account_url=account_url,
            credential=os.getenv('AZURE_STORAGE_KEY')
        )
    
    else:
        raise ValueError("Azure Storage credentials not found in environment variables")

def get_default_container_client():
    """
    Returns a ContainerClient for the default container specified in .env
    """
    blob_service_client = get_blob_client()
    default_container = os.getenv('AZURE_STORAGE_CONTAINER')
    if not default_container:
        raise ValueError("AZURE_STORAGE_CONTAINER not set in .env file")
    return blob_service_client.get_container_client(default_container)

def verify_blob_configuration():
    """
    Verifies the blob configuration by listing containers
    """
    try:
        client = get_blob_client()
        containers = client.list_containers()
        print("Successfully connected to Azure Blob Storage")
        print("Available containers:")
        for container in containers:
            print(f"- {container.name}")
        return True
    except Exception as e:
        print(f"Configuration error: {str(e)}")
        return False
