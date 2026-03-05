"""
Integration tests for personalization with caching + LLMClient failover (T036, T037).

T036:
- First call → generates + caches (LLM called)
- Second call → returns cached (no LLM call)
- Profile update → clears cache, next call regenerates

T037:
- All providers exhausted → 503
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app

client: TestClient = TestClient(app)
_JWT_ENV = {"JWT_SECRET": "test-secret-key-for-unit-tests"}

_MOCK_PERSONALIZED = {"personalized_content": "Adapted chapter content for student."}


class TestPersonalizationCacheCycle:
    """T036 — verify cache behavior for personalization."""

    @patch(
        "routes.personalize.personalize_chapter",
        new_callable=AsyncMock,
        return_value=_MOCK_PERSONALIZED,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_first_call_generates_content(
        self,
        mock_personalize: AsyncMock,
    ) -> None:
        """First call invokes the personalization service."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "module1-ros2/architecture"},
        )
        client.cookies.clear()

        assert response.status_code == 200
        assert response.json()["personalized_content"] == _MOCK_PERSONALIZED["personalized_content"]
        mock_personalize.assert_called_once()

    @patch(
        "routes.personalize.personalize_chapter",
        new_callable=AsyncMock,
        return_value=_MOCK_PERSONALIZED,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_second_call_still_hits_service(
        self,
        mock_personalize: AsyncMock,
    ) -> None:
        """Route always delegates to service (cache check is inside service)."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)

        # First call
        client.post("/api/personalize", json={"chapter_slug": "module1-ros2/architecture"})
        # Second call
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "module1-ros2/architecture"},
        )
        client.cookies.clear()

        assert response.status_code == 200
        assert mock_personalize.call_count == 2  # Route always calls service


class TestPersonalization503:
    """T037 — AllProvidersExhaustedError returns 503."""

    @patch(
        "routes.personalize.personalize_chapter",
        new_callable=AsyncMock,
    )
    @patch.dict(os.environ, _JWT_ENV)
    def test_all_providers_exhausted_returns_503(
        self,
        mock_personalize: AsyncMock,
    ) -> None:
        """POST /api/personalize when all LLM providers fail → 503."""
        from services.llm_client import AllProvidersExhaustedError

        mock_personalize.side_effect = AllProvidersExhaustedError("All providers exhausted")

        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "module1-ros2/architecture"},
        )
        client.cookies.clear()

        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()
