"""
Contract tests for POST /api/chat endpoint.

Tests:
- Valid request → 200 with answer field
- Empty question → 400
- Malformed body → 422
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _mock_generate_answer(question: str, selected_text: str | None = None) -> dict:
    """Mock RAG response for testing."""
    return {
        "answer": f"Mock answer for: {question}",
        "sources": ["Introduction — What is Physical AI"],
    }


class TestChatEndpoint:
    """Contract tests for POST /api/chat."""

    @patch("rag_service.generate_answer", side_effect=_mock_generate_answer)
    def test_valid_request_returns_200(self, mock_rag):
        """Valid request → 200 with answer field."""
        response = client.post(
            "/api/chat",
            json={"question": "What is ROS 2?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert "sources" in data
        assert isinstance(data["sources"], list)

    @patch("rag_service.generate_answer", side_effect=_mock_generate_answer)
    def test_valid_request_with_selected_text(self, mock_rag):
        """Valid request with selected_text → 200."""
        response = client.post(
            "/api/chat",
            json={
                "question": "Explain this",
                "selected_text": "ROS 2 uses DDS middleware",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_empty_question_returns_400(self):
        """Empty question → 400."""
        response = client.post(
            "/api/chat",
            json={"question": "   "},
        )
        assert response.status_code == 400

    def test_missing_question_returns_422(self):
        """Missing question field → 422."""
        response = client.post(
            "/api/chat",
            json={},
        )
        assert response.status_code == 422

    def test_malformed_body_returns_422(self):
        """Malformed body (not JSON) → 422."""
        response = client.post(
            "/api/chat",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_health_endpoint(self):
        """GET /health → 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
