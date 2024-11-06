import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.azure_blob_util import get_blob_client, verify_blob_configuration

def list_blobs_in_container(container_name):
    """
    Lists all blobs in a specific container.
    """
    blob_service_client = get_blob_client()
    container_client = blob_service_client.get_container_client(container_name)
    
    print(f"Blobs in container '{container_name}':")
    for blob in container_client.list_blobs():
        print(f"- {blob.name}")

def main():
    load_dotenv()
    
    # Verify the blob configuration
    if not verify_blob_configuration():
        print("Failed to verify blob configuration. Please check your settings.")
        return

    # List blobs in specific containers
    containers = ['$logs', 'angloamerican-apc-docs']
    for container in containers:
        list_blobs_in_container(container)

if __name__ == "__main__":
    main()
