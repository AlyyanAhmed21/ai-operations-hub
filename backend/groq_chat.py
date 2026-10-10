import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

def chat_with_llama():
    """Chat with Llama-3 via Groq API"""
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.7,
        groq_api_key=groq_api_key
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant."),
        ("human", "{input}")
    ])
    
    chain = prompt_template | llm
    
    print("Chat with Llama-3 (type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        
        response = chain.invoke({"input": user_input})
        print(f"Llama: {response.content}\n")

if __name__ == "__main__":
    chat_with_llama()
