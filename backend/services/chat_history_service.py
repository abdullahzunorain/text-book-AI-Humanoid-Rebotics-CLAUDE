"""
Chat history service: persistent chat Q&A storage per user.

Uses the `chat_messages` table in Neon DB, ordered by created_at DESC.

Public API:
    save_message(user_id, question, answer, selected_text, sources) -> int
    get_history(user_id, limit, offset) -> list[dict]
"""

from __future__ import annotations

import json
import logging

from db import get_pool

logger = logging.getLogger(__name__)


async def save_message(
    user_id: int,
    question: str,
    answer: str,
    selected_text: str | None = None,
    sources: list[str] | None = None,
) -> int:
    """Save a chat message to the database.

    Args:
        user_id: The authenticated user's ID.
        question: The user's question.
        answer: The AI-generated answer.
        selected_text: Optional highlighted text context.
        sources: Optional list of source references.

    Returns:
        The ID of the newly created message.
    """
    pool = get_pool()
    sources_json = json.dumps(sources or [])
    row = await pool.fetchrow(
        """
        INSERT INTO chat_messages (user_id, question, answer, selected_text, sources)
        VALUES ($1, $2, $3, $4, $5::jsonb)
        RETURNING id
        """,
        user_id,
        question,
        answer,
        selected_text,
        sources_json,
    )
    msg_id = row["id"]
    logger.info("Chat message saved: id=%d user=%d", msg_id, user_id)
    return msg_id


async def get_history(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Retrieve chat history for a user, newest first.

    Args:
        user_id: The authenticated user's ID.
        limit: Max messages to return (default 50, max 100).
        offset: Pagination offset.

    Returns:
        List of message dicts with id, question, answer, selected_text, sources, created_at.
    """
    pool = get_pool()

    # Clamp limit to 100
    limit = min(limit, 100)

    rows = await pool.fetch(
        """
        SELECT id, question, answer, selected_text, sources, created_at
        FROM chat_messages
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
        """,
        user_id,
        limit,
        offset,
    )

    messages = []
    for row in rows:
        msg = dict(row)
        # Convert datetime to ISO string for JSON serialization
        if msg.get("created_at"):
            msg["created_at"] = msg["created_at"].isoformat()
        # sources is already JSONB → Python list
        if isinstance(msg.get("sources"), str):
            msg["sources"] = json.loads(msg["sources"])
        messages.append(msg)

    return messages


async def get_total_count(user_id: int) -> int:
    """Return the total number of chat messages for a user.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        Total message count.
    """
    pool = get_pool()
    row = await pool.fetchrow(
        "SELECT COUNT(*) as count FROM chat_messages WHERE user_id = $1",
        user_id,
    )
    return row["count"]
