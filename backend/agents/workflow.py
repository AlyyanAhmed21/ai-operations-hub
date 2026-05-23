# backend/agents/workflow.py
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import router_node, support_node, sales_node, escalation_node
from utils.logger import logger

def route_decision(state: AgentState) -> str:
    """The conditional logic that tells LangGraph where to go next."""
    return state["route"]

def build_agentic_workflow():
    """Compiles the LangGraph multi-agent system."""
    logger.info("🏗️ Building LangGraph Multi-Agent Workflow...")
    
    workflow = StateGraph(AgentState)
    
    # 1. Add all our nodes (Agents)
    workflow.add_node("router", router_node)
    workflow.add_node("support", support_node)
    workflow.add_node("sales", sales_node)
    workflow.add_node("escalation", escalation_node)
    
    # 2. Set the entry point (Every query hits the router first)
    workflow.set_entry_point("router")
    
    # 3. Add conditional edges from the router
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "support": "support",
            "sales": "sales",
            "escalation": "escalation"
        }
    )
    
    # 4. All agent nodes end the workflow after they do their job
    workflow.add_edge("support", END)
    workflow.add_edge("sales", END)
    workflow.add_edge("escalation", END)
    
    # Compile the graph
    return workflow.compile()

# Create a global instance of the app to use in our API
agent_app = build_agentic_workflow()