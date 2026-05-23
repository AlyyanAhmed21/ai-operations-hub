# backend/rag/memory.py
from typing import List, Dict
from utils.logger import logger

# In-memory store for session history. 
# Keys are session_ids, values are lists of message dictionaries.
session_store: Dict[str, List[Dict[str, str]]] = {}

def get_chat_history(session_id: str, limit: int = 4) -> str:
    """
    Retrieves the short-term memory for a specific session.
    We limit it to the last few messages to save tokens and prevent context bloat.
    """
    if session_id not in session_store:
        return "No previous conversation history."
    
    history = session_store[session_id]
    
    # Get only the last 'limit' messages (Short-term memory)
    recent_history = history[-limit:]
    
    formatted_history = ""
    for msg in recent_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['content']}\n"
        
    return formatted_history.strip()

def save_message(session_id: str, role: str, content: str):
    """Saves a message to the session history."""
    if session_id not in session_store:
        session_store[session_id] = []
        logger.info(f"Created new memory session: {session_id}")
        
    session_store[session_id].append({"role": role, "content": content})