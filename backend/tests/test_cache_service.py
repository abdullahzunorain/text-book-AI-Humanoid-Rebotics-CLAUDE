"""
Tests for cache service (content_cache CRUD + invalidation).

Tests use mocked asyncpg pool to verify SQL calls.

Tests:
- Cache miss returns None
- set + get returns content
- UPSERT overwrites existing entry
- invalidate deletes only personalization rows
- Translation rows survive invalidation
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services import cache_service


def _mock_pool():
    """Create a mock asyncpg pool."""
    pool = MagicMock()
    pool.fetchrow = AsyncMock()
    pool.execute = AsyncMock()
    return pool


class TestCacheServiceGetCached:
    """Tests for get_cached()."""

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_cache_miss_returns_none(self, mock_get_pool):
        """Cache miss → returns None."""
        pool = _mock_pool()
        pool.fetchrow.return_value = None
        mock_get_pool.return_value = pool

        result = await cache_service.get_cached(1, "module1-ros2/architecture", "personalization")
        assert result is None
        pool.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_cache_hit_returns_content(self, mock_get_pool):
        """Cache hit → returns content string."""
        pool = _mock_pool()
        pool.fetchrow.return_value = {"content": "Personalized chapter content"}
        mock_get_pool.return_value = pool

        result = await cache_service.get_cached(1, "module1-ros2/architecture", "personalization")
        assert result == "Personalized chapter content"


class TestCacheServiceSetCached:
    """Tests for set_cached()."""

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_set_cached_executes_upsert(self, mock_get_pool):
        """set_cached calls UPSERT on content_cache."""
        pool = _mock_pool()
        mock_get_pool.return_value = pool

        await cache_service.set_cached(
            user_id=1,
            chapter_slug="module1-ros2/architecture",
            cache_type="personalization",
            content="New personalized content",
            metadata={"provider": "gemini"},
        )

        pool.execute.assert_called_once()
        call_args = pool.execute.call_args
        sql = call_args[0][0]
        assert "INSERT INTO content_cache" in sql
        assert "ON CONFLICT" in sql

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_set_cached_overwrites_existing(self, mock_get_pool):
        """UPSERT semantics: second set overwrites first."""
        pool = _mock_pool()
        mock_get_pool.return_value = pool

        # First call
        await cache_service.set_cached(1, "slug", "personalization", "v1")
        # Second call (same key)
        await cache_service.set_cached(1, "slug", "personalization", "v2")

        assert pool.execute.call_count == 2

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_set_cached_default_metadata(self, mock_get_pool):
        """No metadata → defaults to empty JSON object."""
        pool = _mock_pool()
        mock_get_pool.return_value = pool

        await cache_service.set_cached(1, "slug", "translation", "content")

        call_args = pool.execute.call_args[0]
        # metadata arg should be '{}'
        assert call_args[5] == "{}"


class TestCacheServiceInvalidation:
    """Tests for invalidate_personalization()."""

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_invalidate_deletes_personalization_rows(self, mock_get_pool):
        """invalidate_personalization deletes only personalization cache."""
        pool = _mock_pool()
        pool.execute.return_value = "DELETE 3"
        mock_get_pool.return_value = pool

        await cache_service.invalidate_personalization(user_id=42)

        pool.execute.assert_called_once()
        sql = pool.execute.call_args[0][0]
        assert "DELETE FROM content_cache" in sql
        assert "cache_type = 'personalization'" in sql
        # Verify user_id is passed
        assert pool.execute.call_args[0][1] == 42

    @pytest.mark.asyncio
    @patch("services.cache_service.get_pool")
    async def test_invalidate_does_not_affect_translation(self, mock_get_pool):
        """Translation rows should NOT be deleted by invalidation."""
        pool = _mock_pool()
        mock_get_pool.return_value = pool

        await cache_service.invalidate_personalization(user_id=1)

        sql = pool.execute.call_args[0][0]
        # SQL should specifically target personalization only
        assert "personalization" in sql
        assert "translation" not in sql
