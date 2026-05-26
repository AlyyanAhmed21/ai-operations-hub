# backend/rag/retriever.py
import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from utils.logger import logger
from services.memory import get_chat_history

CHROMA_PATH = "./chroma_db"

def ask_knowledge_base(query: str, session_id: str = "default", document_filter: Optional[str] = None):
    logger.info(f"Searching knowledge base for query: '{query}' (Session: {session_id})")
    
    
    # 2. Retrieve past conversation history
    chat_history = get_chat_history(session_id)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if not os.path.exists(CHROMA_PATH):
        return {"answer": "The knowledge base is empty.", "sources": []}
        
    vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # 3. METADATA FILTERING: Only search specific documents if a filter is provided
    search_kwargs = {"k": 3}
    if document_filter:
        logger.info(f"Applying metadata filter: source == {document_filter}")
        search_kwargs["filter"] = {"source": document_filter}
        
    results = vector_store.similarity_search(query, **search_kwargs)
    
    if not results:
        return {"answer": "I couldn't find any relevant information.", "sources": []}
        
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    sources = list(set([doc.metadata.get("source", "Unknown") for doc in results]))

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    # 4. Update Prompt to include Chat History
    prompt_template = """
    You are a professional AI Operations Assistant. 
    Answer the user's question based ONLY on the provided context and the conversation history.
    If the answer is not in the context, say "I do not have enough information."
    
    Conversation History:
    {chat_history}

    Context from Documents:
    {context}

    Current Question:
    {question}
    
    Answer:
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["chat_history", "context", "question"]
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "chat_history": chat_history,
        "context": context_text, 
        "question": query
    })
    
    
    return {
        "answer": response.content,
        "sources": sources
    }