# backend/api/routes.py
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import QueryRequest, QueryResponse, WebhookPayload
from rag.ingestion import process_uploaded_file
from rag.retriever import ask_knowledge_base
from agents.workflow import agent_app
from utils.logger import logger
from services.n8n_client import trigger_n8n_workflow

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@router.post("/upload", tags=["Knowledge Base"])
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT file to be ingested into the RAG system."""
    allowed_extensions = ["pdf", "txt"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    
    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # 1. Save the uploaded file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Process the file (Parse -> Chunk -> Embed -> Store)
        num_chunks = process_uploaded_file(file_path, file.filename)
        
        # 3. Clean up (Delete the temp file)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "status": "success",
            "message": f"Successfully ingested {num_chunks} chunks into the knowledge base."
        }
        
    except Exception as e:
        # Clean up on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/query", response_model=QueryResponse, tags=["AI Operations"])
async def process_query(request: QueryRequest):
    """Send a query to the AI Operations Hub Multi-Agent System."""
    try:
        logger.info(f"🚀 Incoming Query: '{request.query}'")
        
        # 1. Prepare the initial state for LangGraph
        initial_state = {
            "query": request.query,
            "session_id": request.session_id,
            "route": "",
            "answer": "",
            "sources": [],
            "requires_approval": False,
            "extracted_data": {}
        }
        
        # 2. Run the Multi-Agent Workflow!
        final_state = agent_app.invoke(initial_state)
        
                # Prepare the payload for n8n
        n8n_payload = {
            "session_id": request.session_id,
            "route_taken": final_state.get("route", "unknown"),
            "requires_approval": final_state.get("requires_approval", False),
            "extracted_data": final_state.get("extracted_data", {}),
            "ai_answer": final_state.get("answer", "")
        }
        
        # Trigger n8n in the background!
        await trigger_n8n_workflow(n8n_payload)
        
        # 3. Return the final result to the user
        return QueryResponse(
            answer=final_state.get("answer", ""),
            sources=final_state.get("sources", []),
            route_taken=final_state.get("route", "unknown"),
            requires_approval=final_state.get("requires_approval", False),
            extracted_data=final_state.get("extracted_data", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/webhook", tags=["Automations"])
async def receive_webhook(payload: WebhookPayload):
    return {"status": "success", "received_from": payload.source}