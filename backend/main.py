"""
FastAPI backend for Physical AI Textbook RAG chatbot.
Single endpoint: POST /api/chat
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="Physical AI Textbook API",
    description="RAG-powered chatbot for the Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
)

# CORS — allow GitHub Pages origin + local dev
origins = [
    "https://abdullahzunorain.github.io",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=3600,
)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Physical AI Textbook RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /api/chat",
        },
    }


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    selected_text: str | None = Field(default=None, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Answer a question using RAG over textbook content."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        from rag_service import generate_answer

        result = generate_answer(
            question=question,
            selected_text=request.selected_text,
        )
        return ChatResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable: {str(e)}",
        )


@app.get("/health")
async def health():
    return {"status": "ok"}
