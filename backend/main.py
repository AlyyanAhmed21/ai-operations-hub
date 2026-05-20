from fastapi import FastAPI
from pydantic import BaseModel

# Initialize the FastAPI app
app = FastAPI(title="AI Operations Hub", version="1.0")

# Define the data structure we expect for the webhook
class WebhookPayload(BaseModel):
    source: str
    message: str
    customer_id: str | None = None  # Optional field

@app.get("/health")
async def health_check():
    """Simple endpoint to check if the server is alive."""
    return {"status": "healthy", "system": "AI Operations Hub v1"}

@app.post("/webhook")
async def receive_webhook(payload: WebhookPayload):
    """Endpoint to receive data from n8n or external services."""
    print(f"🔔 Webhook received from {payload.source}: {payload.message}")
    
    # Later, this is where we will trigger our LangGraph AI agents!
    
    return {
        "status": "success", 
        "received_message": payload.message,
        "action": "logged"
    }