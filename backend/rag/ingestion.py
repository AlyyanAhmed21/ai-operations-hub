# backend/rag/ingestion.py
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Define where our database will live
CHROMA_PATH = "./chroma_db"

def process_uploaded_file(file_path: str, filename: str):
    """
    Loads a file, chunks it, and saves the embeddings to ChromaDB.
    """
    print(f"⚙️ Processing file: {filename}")
    
    # 1. Load the Document
    file_ext = filename.split(".")[-1].lower()
    if file_ext == "pdf":
        loader = PyPDFLoader(file_path)
    elif file_ext == "txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError("Unsupported file type")
    
    documents = loader.load()
    print(f"📄 Loaded {len(documents)} pages/sections.")

    # 2. Chunk the Document
    # We split the text into chunks of 1000 characters, with a 200-character overlap 
    # so we don't cut sentences in half.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks.")

    # 3. Add Metadata (so we know where the info came from)
    for chunk in chunks:
        chunk.metadata["source"] = filename

    # 4. Initialize Embeddings (Free, Local)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Store in ChromaDB
    print("💾 Saving to ChromaDB...")
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    
    # Add the chunks to the database
    vector_store.add_documents(chunks)
    print("✅ Ingestion complete!")
    
    return len(chunks)