# backend/agents/nodes.py
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.state import AgentState
from rag.retriever import ask_knowledge_base
from utils.logger import logger
import json

# Initialize the LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

def router_node(state: AgentState) -> AgentState:
    """Analyzes the query and routes it to the correct agent."""
    logger.info(f"🧭 [Router Agent] Analyzing query: '{state['query']}'")
    
    prompt = """
    You are the Master Routing Agent. Classify the user's query into EXACTLY ONE of these three categories:
    1. "support" - For questions about policies, knowledge, troubleshooting, or general info.
    2. "sales" - For questions about pricing, buying, or upgrading.
    3. "escalation" - For angry customers, legal threats, or refund demands.
    
    Query: {query}
    
    Output ONLY the category word in lowercase. Nothing else.
    """
    
    chain = PromptTemplate.from_template(prompt) | llm
    response = chain.invoke({"query": state["query"]})
    
    route = response.content.strip().lower()
    
    # Fallback just in case the LLM hallucinates
    if route not in ["support", "sales", "escalation"]:
        route = "escalation"
        
    logger.info(f"🧭 [Router Agent] Decision: Route to -> {route.upper()}")
    return {"route": route}

def support_node(state: AgentState) -> AgentState:
    """Handles knowledge base queries using our RAG engine."""
    logger.info("🛠️ [Support Agent] Processing via RAG...")
    
    # Pass BOTH the query and the session_id to the RAG engine!
    rag_result = ask_knowledge_base(
        query=state["query"], 
        session_id=state["session_id"]
    )
    
    return {
        "answer": rag_result["answer"],
        "sources": rag_result["sources"]
    }


def sales_node(state: AgentState) -> AgentState:
    """Handles sales inquiries, qualifies the lead, and extracts data."""
    logger.info("💰 [Sales Agent] Qualifying lead and drafting response...")
    
    prompt = f"""
    You are an expert Sales Representative. 
    Analyze the user's query. 
    1. Summarize what they want.
    2. Give them a qualification score from 1 to 10 (10 being highly ready to buy).
    3. Draft a polite response inviting them to a demo.
    
    User Query: {state['query']}
    
    You MUST output ONLY a valid JSON object with exactly these keys:
    "summary", "qualification_score", "draft_response"
    Do not include markdown formatting like ```json. Just the raw JSON.
    """
    
    response = llm.invoke(prompt)
    
    try:
        # Parse the JSON output from the LLM
        parsed_data = json.loads(response.content.strip())
        
        return {
            "answer": parsed_data.get("draft_response", "Let's schedule a call!"),
            "extracted_data": {
                "summary": parsed_data.get("summary"),
                "lead_score": parsed_data.get("qualification_score")
            },
            "requires_approval": False,
            "sources": ["Sales Department"]
        }
    except json.JSONDecodeError:
        logger.error("Failed to parse Sales Agent JSON.")
        return {
            "answer": response.content, # Fallback
            "extracted_data": {},
            "requires_approval": False,
            "sources": ["Sales Department"]
        }

def escalation_node(state: AgentState) -> AgentState:
    """Handles sensitive queries and flags them for human approval."""
    logger.info("🚨 [Escalation Agent] Handling sensitive query. Flagging for approval.")
    
    prompt = f"""
    You are an Escalation Manager. 
    The user is upset, asking for a refund, or threatening legal action.
    Draft a highly empathetic, professional response apologizing for the inconvenience 
    and stating that a human senior manager will contact them within 24 hours.
    
    User Query: {state['query']}
    """
    response = llm.invoke(prompt)
    
    return {
        "answer": response.content,
        "extracted_data": {"escalation_reason": "High risk / Angry customer"},
        "requires_approval": True, # THIS IS CRITICAL FOR PHASE 4
        "sources": ["Escalation Team"]
    }