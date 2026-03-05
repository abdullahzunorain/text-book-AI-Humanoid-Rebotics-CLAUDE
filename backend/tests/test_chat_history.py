"""
Tests for chat history service (chat_messages persistence).

Tests use mocked asyncpg pool to verify SQL calls.

Tests:
- save + retrieve returns message
- Ordering is newest-first
- Pagination with limit/offset
- selected_text nullable
- Sources stored as JSONB
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services import chat_history_service


def _mock_pool():
    """Create a mock asyncpg pool."""
    pool = MagicMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock()
    pool.execute = AsyncMock()
    return pool


def _make_message_row(
    msg_id: int = 1,
    question: str = "What is ROS 2?",
    answer: str = "ROS 2 is...",
    selected_text: str | None = None,
    sources: list | None = None,
    created_at: datetime | None = None,
) -> dict:
    """Create a mock message row (dict-like)."""
    return {
        "id": msg_id,
        "question": question,
        "answer": answer,
        "selected_text": selected_text,
        "sources": sources or [],
        "created_at": created_at or datetime(2026, 3, 6, 14, 30, 0),
    }


class TestSaveMessage:
    """Tests for save_message()."""

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_save_message_returns_id(self, mock_get_pool):
        """save_message inserts and returns the new message ID."""
        pool = _mock_pool()
        pool.fetchrow.return_value = {"id": 42}
        mock_get_pool.return_value = pool

        msg_id = await chat_history_service.save_message(
            user_id=1,
            question="What is ROS 2?",
            answer="ROS 2 is a middleware...",
            selected_text=None,
            sources=["Intro — What is ROS"],
        )

        assert msg_id == 42
        pool.fetchrow.assert_called_once()
        sql = pool.fetchrow.call_args[0][0]
        assert "INSERT INTO chat_messages" in sql
        assert "RETURNING id" in sql

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_save_message_with_selected_text(self, mock_get_pool):
        """save_message handles selected_text parameter."""
        pool = _mock_pool()
        pool.fetchrow.return_value = {"id": 1}
        mock_get_pool.return_value = pool

        await chat_history_service.save_message(
            user_id=1,
            question="Explain",
            answer="This means...",
            selected_text="ROS 2 uses DDS",
            sources=[],
        )

        call_args = pool.fetchrow.call_args[0]
        assert call_args[4] == "ROS 2 uses DDS"  # selected_text param

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_save_message_sources_as_json(self, mock_get_pool):
        """Sources are serialized as JSONB."""
        pool = _mock_pool()
        pool.fetchrow.return_value = {"id": 1}
        mock_get_pool.return_value = pool

        sources = ["Chapter 1 — Intro", "Chapter 2 — Architecture"]
        await chat_history_service.save_message(
            user_id=1,
            question="Q",
            answer="A",
            sources=sources,
        )

        call_args = pool.fetchrow.call_args[0]
        assert call_args[5] == json.dumps(sources)  # sources JSON param


class TestGetHistory:
    """Tests for get_history()."""

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_returns_messages(self, mock_get_pool):
        """get_history returns list of message dicts."""
        pool = _mock_pool()
        pool.fetch.return_value = [
            _make_message_row(msg_id=2, question="Q2"),
            _make_message_row(msg_id=1, question="Q1"),
        ]
        mock_get_pool.return_value = pool

        messages = await chat_history_service.get_history(user_id=1)

        assert len(messages) == 2
        assert messages[0]["id"] == 2  # newest first
        assert messages[1]["id"] == 1

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_sql_orders_by_created_at_desc(self, mock_get_pool):
        """SQL query should ORDER BY created_at DESC."""
        pool = _mock_pool()
        pool.fetch.return_value = []
        mock_get_pool.return_value = pool

        await chat_history_service.get_history(user_id=1)

        sql = pool.fetch.call_args[0][0]
        assert "ORDER BY created_at DESC" in sql

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_respects_limit_offset(self, mock_get_pool):
        """Pagination params are passed to SQL."""
        pool = _mock_pool()
        pool.fetch.return_value = []
        mock_get_pool.return_value = pool

        await chat_history_service.get_history(user_id=1, limit=10, offset=20)

        call_args = pool.fetch.call_args[0]
        assert call_args[2] == 10  # limit
        assert call_args[3] == 20  # offset

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_clamps_limit_to_100(self, mock_get_pool):
        """Limit should be clamped to max 100."""
        pool = _mock_pool()
        pool.fetch.return_value = []
        mock_get_pool.return_value = pool

        await chat_history_service.get_history(user_id=1, limit=999)

        call_args = pool.fetch.call_args[0]
        assert call_args[2] == 100  # clamped

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_empty_returns_empty_list(self, mock_get_pool):
        """No messages → empty list."""
        pool = _mock_pool()
        pool.fetch.return_value = []
        mock_get_pool.return_value = pool

        messages = await chat_history_service.get_history(user_id=99)
        assert messages == []

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_selected_text_nullable(self, mock_get_pool):
        """Messages with null selected_text are handled."""
        pool = _mock_pool()
        pool.fetch.return_value = [
            _make_message_row(selected_text=None),
        ]
        mock_get_pool.return_value = pool

        messages = await chat_history_service.get_history(user_id=1)
        assert messages[0]["selected_text"] is None

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_history_created_at_iso_format(self, mock_get_pool):
        """created_at should be converted to ISO format string."""
        pool = _mock_pool()
        pool.fetch.return_value = [
            _make_message_row(created_at=datetime(2026, 3, 6, 14, 30, 0)),
        ]
        mock_get_pool.return_value = pool

        messages = await chat_history_service.get_history(user_id=1)
        assert messages[0]["created_at"] == "2026-03-06T14:30:00"


class TestGetTotalCount:
    """Tests for get_total_count()."""

    @pytest.mark.asyncio
    @patch("services.chat_history_service.get_pool")
    async def test_get_total_count(self, mock_get_pool):
        """get_total_count returns the total number of messages."""
        pool = _mock_pool()
        pool.fetchrow.return_value = {"count": 15}
        mock_get_pool.return_value = pool

        count = await chat_history_service.get_total_count(user_id=1)
        assert count == 15
