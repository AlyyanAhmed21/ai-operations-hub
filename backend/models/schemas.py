# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question or input")
    session_id: Optional[str] = Field(default="default_session", description="For tracking conversation history")

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []
    route_taken: str = "unknown"
    requires_approval: bool = False
    extracted_data: Dict[str, Any] = {}

class WebhookPayload(BaseModel):
    source: str
    message: str
    customer_id: Optional[str] = None