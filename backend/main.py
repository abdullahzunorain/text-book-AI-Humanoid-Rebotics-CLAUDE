"""
FastAPI backend for Physical AI Textbook RAG chatbot.
Endpoints: POST /api/chat, POST /api/translate, auth routes, personalization
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from routes.auth import router as auth_router
from routes.personalize import router as personalize_router
from routes.translate import router as translate_router

load_dotenv()

from db import close_pool, init_pool  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown: initialize and close the DB pool."""
    import os

    dsn = os.getenv("DATABASE_URL", "")
    if dsn:
        await init_pool(dsn)
    yield
    await close_pool()


app = FastAPI(
    title="Physical AI Textbook API",
    description="RAG-powered chatbot for the Physical AI & Humanoid Robotics textbook",
    version="2.0.0",
    lifespan=lifespan,
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
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=3600,
)

app.include_router(translate_router)
app.include_router(auth_router)
app.include_router(personalize_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Physical AI Textbook RAG API",
        "version": "2.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /api/chat",
            "translate": "POST /api/translate",
            "auth": "POST /api/auth/signup | /signin | /signout, GET /api/auth/me",
            "personalize": "POST /api/personalize",
            "background": "POST /api/user/background",
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
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            raise HTTPException(
                status_code=429,
                detail="AI service rate limit reached. Please wait a moment and try again.",
                headers={"Retry-After": "60"},
            )
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        )


@app.get("/health")
async def health():
    return {"status": "ok"}
