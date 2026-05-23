# backend/agents/state.py
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    query: str
    session_id: str
    route: str           
    answer: str
    sources: List[str]
    
    # NEW: For Phase 4 Automation & Human-in-the-loop
    requires_approval: bool      
    extracted_data: Dict[str, Any]