"""
Contract tests for POST /api/personalize endpoint.

TDD: These tests are written first and MUST FAIL until the route is implemented (E4).

Tests cover:
- POST /api/personalize with valid JWT → 200 + personalized_content
- POST /api/personalize without JWT → 401
- POST /api/personalize with invalid slug → 400
- POST /api/personalize when background missing → 200 (uses defaults, personalization_applied=false)
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from main import app

client: TestClient = TestClient(app)


def _mock_pool() -> MagicMock:
    """Create a mock asyncpg pool."""
    pool = MagicMock()
    pool.fetchrow = AsyncMock()
    return pool


_MOCK_PERSONALIZED: dict[str, str] = {
    "personalized_content": (
        "# Forward Kinematics\n\n"
        "Since you have student-level robotics experience, "
        "here is an adapted explanation.\n\n"
        "```python\nimport numpy as np\n```"
    ),
}


class TestPersonalizeEndpointContract:
    """Contract tests for POST /api/personalize."""

    @patch("routes.personalize.personalize_chapter", new_callable=AsyncMock, return_value=_MOCK_PERSONALIZED)
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_valid_jwt_returns_200(
        self,
        mock_personalize: AsyncMock,
    ) -> None:
        """POST /api/personalize with valid JWT → 200 + personalized_content."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "module-1/forward-kinematics"},
        )
        client.cookies.clear()
        assert response.status_code == 200
        data: dict = response.json()
        assert "personalized_content" in data

    def test_no_jwt_returns_401(self) -> None:
        """POST /api/personalize without JWT cookie → 401."""
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "module-1/forward-kinematics"},
        )
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_invalid_slug_returns_400(self) -> None:
        """POST /api/personalize with invalid slug → 400."""
        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "../../../etc/passwd"},
        )
        client.cookies.clear()
        assert response.status_code == 400
        assert "Invalid chapter_slug format" in response.json()["detail"]

    @patch("routes.personalize.personalize_chapter", new_callable=AsyncMock, return_value=_MOCK_PERSONALIZED)
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_missing_background_returns_200_with_defaults(
        self,
        mock_personalize: AsyncMock,
    ) -> None:
        """POST /api/personalize when user has no background → 200 (service uses defaults)."""
        from auth_utils import create_token

        token: str = create_token(user_id=99, email="nobackground@example.com")
        client.cookies.set("token", token)
        response = client.post(
            "/api/personalize",
            json={"chapter_slug": "module-1/forward-kinematics"},
        )
        client.cookies.clear()
        assert response.status_code == 200
        data: dict = response.json()
        assert "personalized_content" in data
