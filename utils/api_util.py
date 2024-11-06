import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_api_response(
    endpoint: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    use_form_data: bool = False
) -> Dict[str, Any]:
    """
    Send a request to the API and get the response.
    
    Args:
        endpoint (str): The API endpoint (e.g., "/chat", "/schema")
        method (str): HTTP method ("GET" or "POST")
        payload (Dict[str, Any], optional): The request payload for POST requests
        use_form_data (bool): Whether to send payload as form data instead of JSON
        
    Returns:
        Dict[str, Any]: The API response
    """
    # Ensure endpoint starts with /api/
    if not endpoint.startswith('/api/'):
        endpoint = f'/api{endpoint}' if endpoint.startswith('/') else f'/api/{endpoint}'
        
    api_url = f"{os.getenv('API_BASE_URL')}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(api_url)
        else:
            if use_form_data:
                response = requests.post(api_url, data=payload)
            else:
                response = requests.post(api_url, json=payload)
            
        response.raise_for_status()
        return {"data": response.json(), "error": False}
    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"Error calling API: {str(e)}",
            "data": None
        }

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