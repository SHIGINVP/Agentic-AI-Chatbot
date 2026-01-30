# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()


import uvicorn
from typing import List, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from ai_agent import get_response_from_ai_agent

#Step1: Setup Pydantic Model (Schema Validation)



class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[Dict[str,str]]   
    allow_search: bool


#Step2: Setup AI Agent from FrontEnd Request


ALLOWED_MODEL_NAMES=["llama3-70b-8192", "mixtral-8x7b-32768", "llama-3.3-70b-versatile", "gpt-4o-mini"]

app=FastAPI(title="LangGraph AI Agent")

@app.post("/chat")
def chat_endpoint(request: RequestState): 
    """
    Chat endpoint to interact with the Agentic AI system.

    This API receives a structured chat request from the frontend,
    validates the selected AI model, extracts user messages from
    the conversation history, and routes the request to the
    AI agent for response generation.

    Args:
        request (RequestState):
            Pydantic model containing all input data required
            to process a chat request.

            Fields inside RequestState:
            - model_name (str): 
                Name of the LLM to be used (must be in ALLOWED_MODEL_NAMES).
            - model_provider (str): 
                Provider of the model (e.g., OpenAI, Groq, etc.).
            - system_prompt (str): 
                System-level instructions that guide the AI's behavior.
            - messages (List[dict]): 
                List of chat messages in role-content format.
                Example:
                {
                    "role": "user",
                    "content": "What is Pandas?"
                }
            - allow_search (bool): 
                Flag to enable or disable external search tools.

    Returns:
        dict:
            A JSON response containing the AI-generated answer.

            Success response format:
            {
                "response": "<AI generated text>"
            }

            Error response format:
            {
                "error": "Invalid model name. Kindly select a valid AI model"
            }

    Raises:
        HTTPException (implicitly by FastAPI):
            Triggered if request validation fails or malformed input is sent.
    """
    if request.model_name not in ALLOWED_MODEL_NAMES:
        return {"error": "Invalid model name. Kindly select a valid AI model"}
    
    llm_id = request.model_name

    
    # Convert chat history format to simple messages for the agent
    query = [
    msg["content"]
    for msg in request.messages
    if msg.get("role") == "user"
    ]

    allow_search = request.allow_search
    system_prompt = request.system_prompt
    provider = request.model_provider

    # Create AI Agent and get response from it! 
    response = get_response_from_ai_agent(llm_id, query, allow_search, system_prompt, provider)
    return {"response": response}




#Step3: Run app & Explore Swagger UI Docs
if __name__ == "__main__":
    """
    Application entry point.

    This block is executed only when the module is run directly.
    It starts the Uvicorn ASGI server to serve the FastAPI application
    for local development and testing purposes.

    The server binds to the local host (127.0.0.1) on port 9999.
    In production environments, the application should be started
    using a process manager or the Uvicorn CLI with multiple workers.
    """
    
    uvicorn.run(app, host="127.0.0.1", port=9999)
