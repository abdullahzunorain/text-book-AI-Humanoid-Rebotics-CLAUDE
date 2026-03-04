"""
POST /api/translate — Translate a chapter to Urdu with code-block preservation.

Rate limiting: 10 requests/minute per IP address.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field

from services.translation_service import translate_to_urdu

router: APIRouter = APIRouter()

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-IP)
# ---------------------------------------------------------------------------

_RATE_LIMIT: int = 10
_RATE_WINDOW: int = 60  # seconds
_ip_requests: dict[str, list[float]] = {}

_SLUG_RE: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9/_-]+$")

# Resolve the docs directory relative to this file
_DOCS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "website" / "docs"


def _check_rate_limit(client_ip: str) -> None:
    """Raise 429 if the client IP has exceeded 10 req/min."""
    now: float = time.time()
    timestamps: list[float] = _ip_requests.get(client_ip, [])

    # Prune timestamps older than the window
    timestamps = [t for t in timestamps if now - t < _RATE_WINDOW]
    _ip_requests[client_ip] = timestamps

    if len(timestamps) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again in 60 seconds.",
            headers={"Retry-After": "60"},
        )

    timestamps.append(now)
    _ip_requests[client_ip] = timestamps


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class TranslateRequest(BaseModel):
    chapter_slug: str = Field(..., min_length=1, max_length=200)


class TranslateResponse(BaseModel):
    translated_content: str
    original_code_blocks: list[str]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/api/translate", response_model=TranslateResponse)
async def translate_chapter(
    body: TranslateRequest,
    request: Request,
    response: Response,
) -> dict[str, Any]:
    """Translate a chapter from English to Urdu."""
    slug: str = body.chapter_slug

    # Validate slug format
    if not _SLUG_RE.match(slug) or ".." in slug:
        raise HTTPException(status_code=400, detail="Invalid chapter_slug format")

    # Rate limit check
    client_ip: str = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    # Read chapter file — 3-step resolution to handle Docusaurus numeric-prefix stripping:
    #   1. Exact:  docs/{slug}.md
    #   2. Index:  docs/{slug}/index.md
    #   3. Prefix: docs/parent/*-{basename}.md  (e.g. 01-architecture.md when slug='architecture')
    chapter_path: Path = _DOCS_DIR / f"{slug}.md"
    if not chapter_path.is_file():
        chapter_path = _DOCS_DIR / slug / "index.md"
    if not chapter_path.is_file():
        # Docusaurus strips numeric prefixes ("01-") from URLs but the actual file has them
        _parent = _DOCS_DIR / Path(slug).parent
        _basename = Path(slug).name
        _candidates = sorted(_parent.glob(f"*-{_basename}.md"))
        if _candidates:
            chapter_path = _candidates[0]
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter not found: {slug}",
            )

    chapter_markdown: str = chapter_path.read_text(encoding="utf-8")

    # Translate
    try:
        result: dict[str, str | list[str]] = await translate_to_urdu(chapter_markdown)
    except Exception as exc:
        logger.exception("Translation failed for slug=%s: %s", slug, exc)
        err_str = str(exc)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            raise HTTPException(
                status_code=429,
                detail="AI service rate limit reached. Please wait a moment and try again.",
                headers={"Retry-After": "60"},
            )
        raise HTTPException(
            status_code=500,
            detail="Translation service temporarily unavailable",
        )

    return result
