"""
Cache service: DB-backed cache for AI-generated personalized/translated content.

Uses the `content_cache` table in Neon DB with UPSERT semantics.

Public API:
    get_cached(user_id, chapter_slug, cache_type) -> str | None
    set_cached(user_id, chapter_slug, cache_type, content, metadata) -> None
    invalidate_personalization(user_id) -> None
"""

from __future__ import annotations

import json
import logging

from db import get_pool

logger = logging.getLogger(__name__)


async def get_cached(
    user_id: int,
    chapter_slug: str,
    cache_type: str,
) -> str | None:
    """Retrieve cached AI-generated content.

    Args:
        user_id: The owning user's ID.
        chapter_slug: Chapter path (e.g. 'module1-ros2/architecture').
        cache_type: Either 'personalization' or 'translation'.

    Returns:
        Cached content string, or None on cache miss.
    """
    pool = get_pool()
    row = await pool.fetchrow(
        """
        SELECT content FROM content_cache
        WHERE user_id = $1 AND chapter_slug = $2 AND cache_type = $3
        """,
        user_id,
        chapter_slug,
        cache_type,
    )
    if row:
        logger.debug("Cache HIT: user=%d slug=%s type=%s", user_id, chapter_slug, cache_type)
        return row["content"]
    logger.debug("Cache MISS: user=%d slug=%s type=%s", user_id, chapter_slug, cache_type)
    return None


async def set_cached(
    user_id: int,
    chapter_slug: str,
    cache_type: str,
    content: str,
    metadata: dict | None = None,
) -> None:
    """Store AI-generated content in the cache (UPSERT).

    Args:
        user_id: The owning user's ID.
        chapter_slug: Chapter path.
        cache_type: 'personalization' or 'translation'.
        content: Full AI-generated markdown content.
        metadata: Optional dict (provider used, generation time, etc.).
    """
    pool = get_pool()
    meta_json = json.dumps(metadata or {})
    await pool.execute(
        """
        INSERT INTO content_cache (user_id, chapter_slug, cache_type, content, metadata)
        VALUES ($1, $2, $3, $4, $5::jsonb)
        ON CONFLICT (user_id, chapter_slug, cache_type) DO UPDATE SET
            content = EXCLUDED.content,
            metadata = EXCLUDED.metadata,
            updated_at = CURRENT_TIMESTAMP
        """,
        user_id,
        chapter_slug,
        cache_type,
        content,
        meta_json,
    )
    logger.info("Cache SET: user=%d slug=%s type=%s", user_id, chapter_slug, cache_type)


async def invalidate_personalization(user_id: int) -> None:
    """Delete all personalization cache entries for a user.

    Called when the user updates their background profile.
    Translation cache is NOT affected.

    Args:
        user_id: The user whose personalization cache should be cleared.
    """
    pool = get_pool()
    result = await pool.execute(
        """
        DELETE FROM content_cache
        WHERE user_id = $1 AND cache_type = 'personalization'
        """,
        user_id,
    )
    logger.info("Cache INVALIDATED personalization: user=%d result=%s", user_id, result)
