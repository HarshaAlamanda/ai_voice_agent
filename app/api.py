from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import ask_agent
from app.conversation import ConversationManager

app = FastAPI(
    title="Agentic AI Solutions - AI Receptionist",
    description="AI receptionist API for conversations and appointment management.",
    version="1.0.0",
)

# Temporary in-memory session for initial API testing.
# Production phone calls will need separate sessions per caller.
manager = ConversationManager()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Agentic AI Solutions - AI Receptionist",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = ask_agent(request.message, manager)
    return ChatResponse(response=response)


@app.post("/session/reset")
def reset_session():
    manager.reset()
    return {"status": "success", "message": "Conversation reset."}