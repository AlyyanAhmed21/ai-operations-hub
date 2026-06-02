# backend/api/routes.py
import os
import shutil
import zlib
import uuid
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import QueryRequest, QueryResponse, WebhookPayload
from rag.ingestion import process_uploaded_file
from rag.retriever import ask_knowledge_base
from agents.workflow import agent_app
from utils.logger import logger
from services.automation_client import trigger_automation_workflow
from services.memory import save_message

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

def generate_doc_id(filename: str) -> str:
    h = zlib.adler32(filename.encode('utf-8')) & 0xffffffff
    return f"DOC-{(h % 9000) + 1000}"

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

@router.post("/upload", tags=["Knowledge Base"])
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT file to be ingested into the RAG system."""
    allowed_extensions = ["pdf", "txt"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    
    # Save the file permanently into backend/docs/
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    file_path = os.path.join(docs_dir, file.filename)
    
    try:
        # 1. Save the uploaded file permanently
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Process the file (Parse -> Chunk -> Embed -> Store)
        num_chunks = process_uploaded_file(file_path, file.filename)
        
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


@router.get("/documents", tags=["Knowledge Base"])
async def list_documents():
    """List all permanently saved files in backend/docs/ directory."""
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    if not os.path.exists(docs_dir):
        return []
    
    documents = []
    for filename in os.listdir(docs_dir):
        file_path = os.path.join(docs_dir, filename)
        if os.path.isfile(file_path):
            file_ext = filename.split(".")[-1].lower()
            if file_ext in ["pdf", "txt"]:
                size_bytes = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                ingested_date = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                
                documents.append({
                    "id": generate_doc_id(filename),
                    "filename": filename,
                    "type": file_ext.upper(),
                    "size": format_size(size_bytes),
                    "ingested_date": ingested_date
                })
    return documents


@router.get("/system/status", tags=["System"])
async def system_status():
    """Return active agent count and status details."""
    return {
        "active_agents_count": 5,
        "agents": [
            {"name": "Router Agent", "role": "Primary Traffic Controller", "status": "online", "latency": "12ms"},
            {"name": "Support Agent", "role": "Policy & Knowledge", "status": "online", "latency": "45ms"},
            {"name": "Sales Agent", "role": "Pricing & Enterprise", "status": "online", "latency": "38ms"},
            {"name": "Escalation Agent", "role": "Human Handoff", "status": "standby", "latency": "—"},
            {"name": "General Agent", "role": "Greetings & Navigation", "status": "online", "latency": "15ms"}
        ]
    }


@router.post("/query", response_model=QueryResponse, tags=["AI Operations"])
async def process_query(request: QueryRequest):
    """Send a query to the AI Operations Hub Multi-Agent System."""
    try:
        logger.info(f"🚀 Incoming Query: '{request.query}'")
        
        # 1. SAVE USER MESSAGE TO GLOBAL MEMORY
        save_message(request.session_id, "user", request.query)
        
        # 2. Prepare the initial state for LangGraph
        initial_state = {
            "query": request.query,
            "session_id": request.session_id,
            "route": "",
            "answer": "",
            "sources": [],
            "requires_approval": False,
            "extracted_data": {}
        }
        
        # 3. Run the Multi-Agent Workflow!
        final_state = agent_app.invoke(initial_state)
        
        # 4. SAVE AI ANSWER TO GLOBAL MEMORY
        save_message(request.session_id, "assistant", final_state.get("answer", ""))
        
        # 5. Prepare the payload for Make.com
        route_taken = final_state.get("route", "unknown")
        
        # Generate a unique Escalation ID if the route is escalation
        escalation_id = None
        if route_taken == "escalation":
            # Creates an ID like: esc-20260531-a1b2
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            unique_hash = uuid.uuid4().hex[:4]
            escalation_id = f"esc-{date_str}-{unique_hash}"

        # Prepare the payload for Make.com
        automation_payload = {
            "session_id": request.session_id,
            "route_taken": route_taken,
            "requires_approval": final_state.get("requires_approval", False),
            "extracted_data": final_state.get("extracted_data", {}),
            "ai_answer": final_state.get("answer", ""),
            "escalation_id": escalation_id
        }
        
        # Trigger Make.com in the background!
        await trigger_automation_workflow(automation_payload)
        
        # 6. Return the final result
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