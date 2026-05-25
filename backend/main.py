# backend/main.py
from dotenv import load_dotenv
# LOAD ENV VARS FIRST BEFORE IMPORTING ANYTHING ELSE!
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from utils.logger import logger

logger.info("Starting AI Operations Hub API...")

app = FastAPI(
    title="AI Operations Hub API",
    description="Backend for the Agentic AI Operations System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    logger.info("Initializing Uvicorn server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)