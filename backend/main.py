"""
FastAPI backend for Physical AI Textbook RAG chatbot.
Endpoints: POST /api/chat, POST /api/translate, auth routes, personalization
"""

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from dotenv import load_dotenv

# Load .env BEFORE any service imports so that GOOGLE_API_KEY (and other
# env vars) are visible when agent_config.py is first imported.
load_dotenv()

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from routes.auth import router as auth_router  # noqa: E402
from routes.chat import router as chat_router  # noqa: E402
from routes.personalize import router as personalize_router  # noqa: E402
from routes.translate import router as translate_router  # noqa: E402
from db import close_pool, init_pool  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown: initialize and close the DB pool."""
    dsn = os.getenv("DATABASE_URL", "")
    if dsn:
        try:
            await init_pool(dsn)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "Could not connect to Postgres — auth, history, and cache will be unavailable: %s",
                exc,
            )
    yield
    await close_pool()


app = FastAPI(
    title="Physical AI Textbook API",
    description="RAG-powered chatbot for the Physical AI & Humanoid Robotics textbook",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — read origins from env var (comma-separated), default to local dev
_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]

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
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Physical AI Textbook RAG API",
        "version": "2.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /api/chat",
            "chat_history": "GET /api/chat/history",
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
async def chat(request_body: ChatRequest, request: Request):
    """Answer a question using RAG over textbook content."""
    question = request_body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Extract optional user_id from JWT cookie (non-failing: unauthenticated users get None)
    user_id: int | None = None
    token = request.cookies.get("token")
    if token:
        try:
            from auth_utils import decode_token
            payload = decode_token(token)
            user_id = payload.get("sub")
        except Exception:
            pass  # Unauthenticated — proceed without saving history

    try:
        from rag_service import generate_answer

        result = await generate_answer(
            question=question,
            selected_text=request_body.selected_text,
            user_id=user_id,
        )
        return ChatResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        import openai
        if isinstance(e, openai.RateLimitError):
            raise HTTPException(
                status_code=429,
                detail="AI service rate limit reached. Please wait a moment and try again.",
                headers={"Retry-After": "60"},
            )
        if isinstance(e, openai.APIError):
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Please try again later.",
            )
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
