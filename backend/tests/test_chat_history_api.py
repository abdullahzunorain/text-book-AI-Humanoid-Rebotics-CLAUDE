"""
Contract tests for chat history endpoints.

T026 — GET /api/chat/history:
  - 401 without auth
  - 200 with valid token returns messages array + pagination
  - Empty history returns []
  - Pagination params honoured

T027 — POST /api/chat history saving:
  - Authenticated request saves to DB
  - Unauthenticated request does NOT save
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app

client: TestClient = TestClient(app)
_JWT_ENV = {"JWT_SECRET": "test-secret-key-for-unit-tests"}

_SAMPLE_MESSAGES = [
    {
        "id": 2,
        "question": "What is ROS 2?",
        "answer": "ROS 2 is a robotics framework.",
        "selected_text": None,
        "sources": ["Introduction — What is Physical AI"],
        "created_at": "2025-01-15T10:30:00",
    },
    {
        "id": 1,
        "question": "Explain DDS",
        "answer": "DDS is the middleware used by ROS 2.",
        "selected_text": "DDS middleware",
        "sources": ["Module 1 — ROS 2 Architecture"],
        "created_at": "2025-01-15T10:25:00",
    },
]


# ---------------------------------------------------------------------------
# T026 — GET /api/chat/history
# ---------------------------------------------------------------------------


class TestChatHistoryEndpoint:
    """Contract tests for GET /api/chat/history."""

    def test_no_auth_returns_401(self) -> None:
        """GET /api/chat/history without JWT → 401."""
        client.cookies.clear()
        response = client.get("/api/chat/history")
        assert response.status_code == 401

    @patch("routes.chat.get_total_count", new_callable=AsyncMock, return_value=2)
    @patch("routes.chat.get_history", new_callable=AsyncMock, return_value=_SAMPLE_MESSAGES)
    @patch.dict(os.environ, _JWT_ENV)
    def test_valid_auth_returns_200_with_messages(
        self,
        mock_get_history: AsyncMock,
        mock_get_count: AsyncMock,
    ) -> None:
        """GET /api/chat/history with valid JWT → 200 with messages."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.get("/api/chat/history")
        client.cookies.clear()

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == 2
        assert data["total"] == 2
        assert data["limit"] == 50
        assert data["offset"] == 0

        # Verify message structure
        msg = data["messages"][0]
        assert "id" in msg
        assert "question" in msg
        assert "answer" in msg
        assert "sources" in msg
        assert "created_at" in msg

    @patch("routes.chat.get_total_count", new_callable=AsyncMock, return_value=0)
    @patch("routes.chat.get_history", new_callable=AsyncMock, return_value=[])
    @patch.dict(os.environ, _JWT_ENV)
    def test_empty_history_returns_empty_list(
        self,
        mock_get_history: AsyncMock,
        mock_get_count: AsyncMock,
    ) -> None:
        """GET /api/chat/history with no messages → 200 with empty messages."""
        from auth_utils import create_token

        token: str = create_token(user_id=99, email="new@example.com")
        client.cookies.set("token", token)
        response = client.get("/api/chat/history")
        client.cookies.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        assert data["total"] == 0

    @patch("routes.chat.get_total_count", new_callable=AsyncMock, return_value=50)
    @patch("routes.chat.get_history", new_callable=AsyncMock, return_value=_SAMPLE_MESSAGES[:1])
    @patch.dict(os.environ, _JWT_ENV)
    def test_pagination_params_honoured(
        self,
        mock_get_history: AsyncMock,
        mock_get_count: AsyncMock,
    ) -> None:
        """GET /api/chat/history?limit=10&offset=5 passes params through."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.get("/api/chat/history?limit=10&offset=5")
        client.cookies.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 5

        # Verify service was called with correct pagination
        mock_get_history.assert_called_once_with(user_id=1, limit=10, offset=5)

    @patch.dict(os.environ, _JWT_ENV)
    def test_limit_exceeds_max_returns_422(self) -> None:
        """GET /api/chat/history?limit=200 → 422 (max is 100)."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.get("/api/chat/history?limit=200")
        client.cookies.clear()

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# T027 — POST /api/chat history saving
# ---------------------------------------------------------------------------


async def _mock_generate_answer_with_save(
    question: str,
    selected_text: str | None = None,
    user_id: int | None = None,
) -> dict:
    """Mock that tracks whether user_id was passed."""
    return {
        "answer": f"Mock answer for: {question}",
        "sources": ["Introduction — What is Physical AI"],
        "_user_id_received": user_id,
    }


class TestChatHistorySaving:
    """Tests verifying that POST /api/chat passes user_id for history saving."""

    @patch(
        "rag_service.generate_answer",
        new_callable=AsyncMock,
        side_effect=_mock_generate_answer_with_save,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_authenticated_request_passes_user_id(
        self,
        mock_generate: AsyncMock,
    ) -> None:
        """POST /api/chat with valid JWT passes user_id to generate_answer."""
        from auth_utils import create_token

        token: str = create_token(user_id=42, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post("/api/chat", json={"question": "What is ROS 2?"})
        client.cookies.clear()

        assert response.status_code == 200
        # Verify generate_answer was called with user_id=42
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs.get("user_id") == 42 or (
            len(call_kwargs.args) >= 3 and call_kwargs.args[2] == 42
        )

    @patch(
        "rag_service.generate_answer",
        new_callable=AsyncMock,
        side_effect=_mock_generate_answer_with_save,
    )
    def test_unauthenticated_request_passes_none_user_id(
        self,
        mock_generate: AsyncMock,
    ) -> None:
        """POST /api/chat without JWT passes user_id=None (no history saved)."""
        client.cookies.clear()
        response = client.post("/api/chat", json={"question": "What is ROS 2?"})

        assert response.status_code == 200
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        # user_id should be None for unauthenticated users
        assert call_kwargs.kwargs.get("user_id") is None or (
            len(call_kwargs.args) >= 3 and call_kwargs.args[2] is None
        )


# ---------------------------------------------------------------------------
# T046 — POST /api/chat with selected_text scoping
# ---------------------------------------------------------------------------


class TestSelectedTextChat:
    """Tests verifying POST /api/chat passes selected_text to RAG."""

    @patch(
        "rag_service.generate_answer",
        new_callable=AsyncMock,
    )
    def test_selected_text_passed_to_generate(
        self,
        mock_generate: AsyncMock,
    ) -> None:
        """POST /api/chat with selected_text passes it to generate_answer."""
        mock_generate.return_value = {
            "answer": "Based on the selected passage, ROS 2 uses DDS.",
            "sources": ["Module 1 — Architecture"],
        }

        client.cookies.clear()
        response = client.post(
            "/api/chat",
            json={
                "question": "Explain this",
                "selected_text": "ROS 2 uses DDS middleware for communication",
            },
        )

        assert response.status_code == 200
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs.get("selected_text") == "ROS 2 uses DDS middleware for communication"

    @patch(
        "rag_service.generate_answer",
        new_callable=AsyncMock,
    )
    def test_no_selected_text_passes_none(
        self,
        mock_generate: AsyncMock,
    ) -> None:
        """POST /api/chat without selected_text passes None."""
        mock_generate.return_value = {
            "answer": "ROS 2 is a framework.",
            "sources": ["Introduction"],
        }

        client.cookies.clear()
        response = client.post(
            "/api/chat",
            json={"question": "What is ROS 2?"},
        )

        assert response.status_code == 200
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs.get("selected_text") is None
