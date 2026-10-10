import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Load environment variables (your Groq API key)
load_dotenv()

print("--- 1. Testing Groq LLM (Llama 3) ---")
# Initialize the LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b", # Fast, free, and highly capable
    temperature=0           # 0 means factual and deterministic (good for business)
)

# Test the LLM
response = llm.invoke("In one sentence, what is an AI Agent?")
print(f"🤖 Llama-3 says: {response.content}\n")


print("--- 2. Testing Local Embeddings & ChromaDB ---")
# Initialize HuggingFace Embeddings (Runs 100% locally on your CPU, free!)
# The first time you run this, it will download a ~90MB model.
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Let's create some fake business knowledge
business_docs = [
    Document(
        page_content="Refund Policy: Customers can request a full refund within 30 days of purchase. After 30 days, no refunds are allowed.", 
        metadata={"source": "policy_v1.pdf"}
    ),
    Document(
        page_content="Tech Support: If the software crashes on startup, ask the user to clear their cache and restart their PC.", 
        metadata={"source": "troubleshooting_guide.txt"}
    )
]

# Store the documents in a local ChromaDB vector database
print("💾 Saving documents to ChromaDB...")
vector_store = Chroma.from_documents(
    documents=business_docs,
    embedding=embeddings,
    persist_directory="./chroma_db_experiment" # Saves to a local folder
)

print("--- 3. Testing Semantic Search (RAG) ---")
# Pretend a user asks a question
user_query = "A customer bought the app 45 days ago and wants their money back. What do I do?"
print(f"👤 User asks: {user_query}")

# Search the vector database for the most relevant document (k=1 means top 1 result)
results = vector_store.similarity_search(user_query, k=1)

print(f"📄 Retrieved Context: {results[0].page_content}")
print(f"🔗 Source Document: {results[0].metadata['source']}")