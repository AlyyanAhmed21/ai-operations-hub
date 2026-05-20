import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

def create_embeddings_and_search():
    """Create embeddings and store/search in ChromaDB"""
    
    # Initialize HuggingFace embeddings (runs locally, free)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Sample documents
    documents = [
        Document(page_content="FastAPI is a modern, fast web framework for building APIs with Python."),
        Document(page_content="LangChain is a framework for developing applications powered by language models."),
        Document(page_content="ChromaDB is a vector database for AI applications."),
        Document(page_content="HuggingFace provides pre-trained models for NLP tasks."),
        Document(page_content="LLMs like Llama-3 can be accessed through various APIs and services.")
    ]
    
    # Create ChromaDB vector store
    persist_directory = "./chroma_db"
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="my_collection"
    )
    
    print("✓ Embeddings created and stored in ChromaDB")
    print("-" * 50)
    
    # Search examples
    queries = [
        "What is FastAPI?",
        "Tell me about vector databases",
        "LLM frameworks"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = vectorstore.similarity_search(query, k=2)
        print("Top results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.page_content}")
    
    print("\n✓ Embeddings saved to ./chroma_db (persistent)")

if __name__ == "__main__":
    create_embeddings_and_search()
