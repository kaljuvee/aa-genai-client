import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def get_chat_response(
    question: str,
    controller_id: str,
    user_id: str = None,
    session_id: str = None
) -> Dict[str, Any]:
    """
    Send a question to the chat API and get the response.
    
    Args:
        question (str): The user's question
        controller_id (str): The ID of the controller/document context
        user_id (str, optional): User identifier
        session_id (str, optional): Session identifier
        
    Returns:
        Dict[str, Any]: The API response containing the answer and metadata
    """
    api_url = f"{os.getenv('API_BASE_URL')}/chat"
    
    payload = {
        "question": question,
        "controller_id": controller_id,
        "user_id": user_id,
        "session_id": session_id
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"answer": f"Error calling API: {str(e)}", "error": True} 