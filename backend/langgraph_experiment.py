import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

load_dotenv()

# Initialize our LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# 1. Define the State (The memory that gets passed between nodes)
class AgentState(TypedDict):
    user_input: str
    classification: str
    final_response: str

# 2. Define the Nodes (The actual workers)
def router_node(state: AgentState):
    """Analyzes the input and classifies it."""
    print(f"🧭 [Router Node] Analyzing: '{state['user_input']}'")
    prompt = f"Classify this message as 'greeting' or 'question'. Message: '{state['user_input']}'. Output ONLY the word 'greeting' or 'question'."
    response = llm.invoke(prompt)
    return {"classification": response.content.strip().lower()}

def greeting_node(state: AgentState):
    """Handles greetings."""
    print("👋 [Greeting Node] Handling greeting...")
    return {"final_response": "Hello there! How can I assist you with your business operations today?"}

def answer_node(state: AgentState):
    """Handles actual questions."""
    print("🧠 [Answer Node] Generating answer...")
    response = llm.invoke(f"Answer this question briefly: {state['user_input']}")
    return {"final_response": response.content}

# 3. Define the Routing Logic (The conditional edge)
def route_decision(state: AgentState):
    """Decides which node to go to next based on the classification."""
    if "greeting" in state["classification"]:
        return "greeting_node"
    else:
        return "answer_node"

# 4. Build the Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("greeting_node", greeting_node)
workflow.add_node("answer_node", answer_node)

# Add edges (The flow)
workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router", 
    route_decision # The function that decides the next step
)
workflow.add_edge("greeting_node", END)
workflow.add_edge("answer_node", END)

# Compile the graph
app = workflow.compile()

# 5. Test the Graph
print("\n--- Test 1: A Greeting ---")
result_1 = app.invoke({"user_input": "Hey, good morning!"})
print(f"✅ Final Output: {result_1['final_response']}\n")

print("--- Test 2: A Question ---")
result_2 = app.invoke({"user_input": "What is the capital of Japan?"})
print(f"✅ Final Output: {result_2['final_response']}\n")