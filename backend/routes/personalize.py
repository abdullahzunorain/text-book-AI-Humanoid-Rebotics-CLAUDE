"""
POST /api/personalize — Personalise chapter content for authenticated users.

Requires a valid JWT cookie. Fetches user background from DB and calls the
personalization service. Falls back to beginner defaults when no background exists.
"""

from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from jose import ExpiredSignatureError, JWTError
from pydantic import BaseModel, Field

import openai
from auth_utils import decode_token
from services.personalization_service import personalize_chapter

router: APIRouter = APIRouter()

_SLUG_RE: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9/_-]+$")
_COOKIE_NAME: str = "token"


def _get_user_id_from_cookie(request: Request) -> int:
    """Extract user_id from JWT cookie. Raises 401 with distinct detail codes."""
    token: str | None = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="not_authenticated")
    try:
        payload: dict[str, Any] = decode_token(token)
        return payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="session_expired")
    except (JWTError, Exception):
        raise HTTPException(status_code=401, detail="invalid_token")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class PersonalizeRequest(BaseModel):
    chapter_slug: str = Field(..., min_length=1, max_length=200)


class PersonalizeResponse(BaseModel):
    personalized_content: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/api/personalize", response_model=PersonalizeResponse)
async def personalize_endpoint(
    body: PersonalizeRequest,
    request: Request,
) -> dict[str, Any]:
    """Personalise a chapter for the authenticated user."""
    # 1. Auth — require JWT
    user_id: int = _get_user_id_from_cookie(request)

    # 2. Validate slug
    if not _SLUG_RE.match(body.chapter_slug):
        raise HTTPException(status_code=400, detail="Invalid chapter_slug format")

    # 3. Call personalization service
    try:
        result: dict[str, str] = await personalize_chapter(
            chapter_slug=body.chapter_slug,
            user_id=user_id,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chapter not found")
    except openai.APIError:
        raise HTTPException(
            status_code=503,
            detail="All AI providers are temporarily unavailable. Please try again later.",
        )
    except Exception as exc:
        err_str = str(exc)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            raise HTTPException(
                status_code=429,
                detail="AI service rate limit reached. Please wait a moment and try again.",
                headers={"Retry-After": "60"},
            )
        raise HTTPException(
            status_code=500,
            detail="Personalization service temporarily unavailable",
        )

    return result
