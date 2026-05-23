# backend/rag/retriever.py
import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from utils.logger import logger # Import our logger

CHROMA_PATH = "./chroma_db"

def ask_knowledge_base(query: str):
    logger.info(f"Searching knowledge base for query: '{query}'")
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if not os.path.exists(CHROMA_PATH):
        logger.warning("ChromaDB path does not exist. Knowledge base is empty.")
        return {
            "answer": "The knowledge base is empty. Please upload some documents first.",
            "sources": []
        }
        
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    
    results = vector_store.similarity_search(query, k=3)
    
    if not results:
        logger.info("No relevant documents found in ChromaDB.")
        return {
            "answer": "I couldn't find any relevant information in the knowledge base.",
            "sources": []
        }
        
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    sources = list(set([doc.metadata.get("source", "Unknown") for doc in results]))
    
    logger.info(f"Found {len(results)} relevant chunks from sources: {sources}")

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    prompt_template = """
    You are a professional AI Operations Assistant. 
    Answer the user's question based ONLY on the following context. 
    If the answer is not in the context, say "I do not have enough information to answer this based on the provided documents."
    Do not guess or hallucinate.

    Context:
    {context}

    Question:
    {question}
    
    Answer:
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    logger.info("Generating answer with Llama-3.1...")
    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": query})
    
    logger.info("Answer generated successfully.")
    
    return {
        "answer": response.content,
        "sources": sources
    }