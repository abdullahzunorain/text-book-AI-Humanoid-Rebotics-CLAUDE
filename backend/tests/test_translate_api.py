"""
Contract tests for POST /api/translate endpoint.

Tests cover:
- POST /api/translate with valid slug + JWT → 200 + translated_content and original_code_blocks
- POST without JWT → 401
- POST with invalid slug → 400
- POST with nonexistent chapter → 404
- Rate limit exceeded → 429 with Retry-After header
- AllProvidersExhaustedError → 503
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app
from routes.translate import _ip_requests

client: TestClient = TestClient(app)
_JWT_ENV = {"JWT_SECRET": "test-secret-key-for-unit-tests"}

_MOCK_TRANSLATION: dict[str, str | list[str]] = {
    "translated_content": "# ٹیسٹ\n\nیہ ترجمہ ہے۔\n\n```python\nimport rclpy\n```",
    "original_code_blocks": ["```python\nimport rclpy\n```"],
}


def _get_auth_token() -> str:
    """Create a test JWT token."""
    from auth_utils import create_token
    return create_token(user_id=1, email="user@example.com")


class TestTranslateEndpointContract:
    """Contract tests for POST /api/translate."""

    def setup_method(self) -> None:
        """Reset rate limiter state before each test."""
        _ip_requests.clear()
        client.cookies.clear()

    @patch(
        "routes.translate.translate_to_urdu",
        new_callable=AsyncMock,
        return_value=_MOCK_TRANSLATION,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_valid_slug_returns_200(self, mock_translate: AsyncMock) -> None:
        """POST /api/translate with valid slug + JWT → 200 + translated_content."""
        client.cookies.set("token", _get_auth_token())
        response = client.post(
            "/api/translate",
            json={"chapter_slug": "module2-simulation/chapter1-gazebo-basics"},
        )
        client.cookies.clear()
        assert response.status_code == 200
        data: dict = response.json()
        assert "translated_content" in data
        assert "original_code_blocks" in data
        assert isinstance(data["translated_content"], str)
        assert isinstance(data["original_code_blocks"], list)

    def test_no_auth_returns_401(self) -> None:
        """POST /api/translate without JWT → 401."""
        response = client.post(
            "/api/translate",
            json={"chapter_slug": "module2-simulation/chapter1-gazebo-basics"},
        )
        assert response.status_code == 401

    @patch.dict(os.environ, _JWT_ENV)
    def test_invalid_slug_returns_400(self) -> None:
        """POST /api/translate with '..' in slug → 400."""
        client.cookies.set("token", _get_auth_token())
        response = client.post(
            "/api/translate",
            json={"chapter_slug": "../../../etc/passwd"},
        )
        client.cookies.clear()
        assert response.status_code == 400
        assert "Invalid chapter_slug format" in response.json()["detail"]

    @patch.dict(os.environ, _JWT_ENV)
    def test_invalid_slug_special_chars_returns_400(self) -> None:
        """POST /api/translate with special chars → 400."""
        client.cookies.set("token", _get_auth_token())
        response = client.post(
            "/api/translate",
            json={"chapter_slug": "module<script>alert(1)</script>"},
        )
        client.cookies.clear()
        assert response.status_code == 400

    @patch(
        "routes.translate.translate_to_urdu",
        new_callable=AsyncMock,
        return_value=_MOCK_TRANSLATION,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_nonexistent_chapter_returns_404(self, mock_translate: AsyncMock) -> None:
        """POST /api/translate with nonexistent slug → 404."""
        client.cookies.set("token", _get_auth_token())
        response = client.post(
            "/api/translate",
            json={"chapter_slug": "module99-fake/chapter1-nonexistent"},
        )
        client.cookies.clear()
        assert response.status_code == 404
        assert "Chapter not found" in response.json()["detail"]

    @patch.dict(os.environ, _JWT_ENV)
    def test_rate_limit_returns_429(self) -> None:
        """Sending >10 requests in <60s from same IP → 429 with Retry-After."""
        with patch(
            "routes.translate.translate_to_urdu",
            new_callable=AsyncMock,
            return_value=_MOCK_TRANSLATION,
        ):
            client.cookies.set("token", _get_auth_token())
            # Send 10 valid requests (should all succeed)
            for i in range(10):
                resp = client.post(
                    "/api/translate",
                    json={
                        "chapter_slug": "module2-simulation/chapter1-gazebo-basics",
                    },
                )
                assert resp.status_code == 200, f"Request {i + 1} failed: {resp.status_code}"

            # The 11th request should be rate-limited
            resp = client.post(
                "/api/translate",
                json={
                    "chapter_slug": "module2-simulation/chapter1-gazebo-basics",
                },
            )
            client.cookies.clear()
            assert resp.status_code == 429
            assert "Rate limit exceeded" in resp.json()["detail"]
            assert "Retry-After" in resp.headers

    @patch.dict(os.environ, _JWT_ENV)
    def test_rate_limit_resets_after_window(self) -> None:
        """After clearing ip_requests (simulating 60s cooldown), requests succeed again."""
        with patch(
            "routes.translate.translate_to_urdu",
            new_callable=AsyncMock,
            return_value=_MOCK_TRANSLATION,
        ):
            client.cookies.set("token", _get_auth_token())
            # Exhaust rate limit
            for _ in range(10):
                client.post(
                    "/api/translate",
                    json={"chapter_slug": "module2-simulation/chapter1-gazebo-basics"},
                )

            # 11th is blocked
            resp = client.post(
                "/api/translate",
                json={"chapter_slug": "module2-simulation/chapter1-gazebo-basics"},
            )
            assert resp.status_code == 429

            # Simulate cooldown by clearing the rate limiter
            _ip_requests.clear()

            # Now requests should succeed again
            resp = client.post(
                "/api/translate",
                json={"chapter_slug": "module2-simulation/chapter1-gazebo-basics"},
            )
            client.cookies.clear()
            assert resp.status_code == 200

    @patch(
        "routes.translate.translate_to_urdu",
        new_callable=AsyncMock,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_all_providers_exhausted_returns_503(self, mock_translate: AsyncMock) -> None:
        """POST /api/translate when all LLM providers fail → 503."""
        import httpx
        import openai

        mock_translate.side_effect = openai.APIError(
            message="All providers exhausted",
            request=httpx.Request("POST", "https://example.com"),
            body=None,
        )

        client.cookies.set("token", _get_auth_token())
        response = client.post(
            "/api/translate",
            json={"chapter_slug": "module2-simulation/chapter1-gazebo-basics"},
        )
        client.cookies.clear()

        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()
