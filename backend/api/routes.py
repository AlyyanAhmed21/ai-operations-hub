# backend/api/routes.py
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import QueryRequest, QueryResponse, WebhookPayload
from rag.ingestion import process_uploaded_file
from rag.retriever import ask_knowledge_base

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
    """Send a query to the AI Operations Hub."""
    
    try:
        # Call our RAG system
        rag_result = ask_knowledge_base(request.query)
        
        return QueryResponse(
            answer=rag_result["answer"],
            sources=rag_result["sources"],
            route_taken="rag_direct" # We will update this in Phase 3 with LangGraph
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/webhook", tags=["Automations"])
async def receive_webhook(payload: WebhookPayload):
    return {"status": "success", "received_from": payload.source}