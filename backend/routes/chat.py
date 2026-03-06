"""
GET /api/chat/history — Retrieve paginated chat history for authenticated users.

Requires JWT cookie authentication.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from jose import ExpiredSignatureError, JWTError
from pydantic import BaseModel

from auth_utils import decode_token
from services.chat_history_service import get_history, get_total_count

router: APIRouter = APIRouter()

_COOKIE_NAME: str = "token"


def _get_user_id_from_cookie(request: Request) -> int:
    """Extract user_id from JWT cookie. Raises 401 with distinct detail codes."""
    token: str | None = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="not_authenticated")
    try:
        payload: dict = decode_token(token)
        return payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="session_expired")
    except (JWTError, Exception):
        raise HTTPException(status_code=401, detail="invalid_token")


# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------


class ChatHistoryMessage(BaseModel):
    id: int
    question: str
    answer: str
    selected_text: str | None = None
    sources: list[str] = []
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryMessage]
    total: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get("/api/chat/history", response_model=ChatHistoryResponse)
async def chat_history(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """Retrieve chat history for the authenticated user.

    Returns paginated messages ordered newest-first.
    """
    user_id: int = _get_user_id_from_cookie(request)

    messages = await get_history(user_id=user_id, limit=limit, offset=offset)
    total = await get_total_count(user_id=user_id)

    return {
        "messages": messages,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
