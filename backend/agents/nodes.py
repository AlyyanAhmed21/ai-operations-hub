import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.state import AgentState
from rag.retriever import ask_knowledge_base
from utils.logger import logger
from services.memory import get_chat_history

# Load env vars before initializing Groq
load_dotenv()

# Initialize the LLM
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def router_node(state: AgentState) -> AgentState:
    """Analyzes the query and routes it to the correct agent."""
    logger.info(f"🧭 [Router Agent] Analyzing query: '{state['query']}'")
    
    # Fetch the recent conversation history
    history = get_chat_history(state["session_id"])
    
    prompt = f"""
    You are the Master Routing Agent. 
    
    Recent Conversation History:
    {history}
    
    Latest User Query: "{state['query']}"
    
    Based on the context, classify the LATEST query into EXACTLY ONE of these four categories:
    1. "support" - For questions about company policies, documents, employees, specific people, troubleshooting, or factual information.
    2. "sales" - For questions about pricing, buying, or upgrading.
    3. "escalation" - For angry customers, legal threats, or refund demands.
    4. "general" - For simple greetings (hi, hello) or asking what you can do.
    
    Output ONLY the category word in lowercase. Nothing else.
    """
    
    response = llm.invoke(prompt)
    route = response.content.strip().lower()
    
    if route not in ["support", "sales", "escalation", "general"]:
        route = "general"
        
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


def general_node(state: AgentState) -> AgentState:
    """Handles greetings and general conversation with memory."""
    logger.info("👋 [General Agent] Handling general query...")
    
    history = get_chat_history(state["session_id"])
    
    prompt = f"""
        You are the professional, courteous AI Operations Assistant (acting with the professionalism of an HR representative).
        
        Recent Conversation History:
        {history}
        
        Latest User Query: "{state['query']}"
        
        Tone & Behavior Guidelines:
        - Be polite, concise, and highly professional.
        - DO NOT use overly casual phrases (e.g., "hum of activity", "what have you been up to", "catching up").
        - If the user asks for factual information about a person, employee, or company data, DO NOT guess. State that you are the greeting agent and ask them to specify their question so you can search the company records.
        
        Respond to the user's latest query following these guidelines.
        """
    response = llm.invoke(prompt)
    
    return {
        "answer": response.content,
        "extracted_data": {},
        "requires_approval": False,
        "sources": []
    }