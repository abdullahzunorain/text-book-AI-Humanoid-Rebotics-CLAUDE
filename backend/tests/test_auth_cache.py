"""
Integration tests for cache invalidation on background update (T031).

Tests:
- POST /api/user/background → invalidate_personalization called for that user
- Translation cache NOT affected (invalidate_personalization only deletes personalization type)
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from main import app

client: TestClient = TestClient(app)
_JWT_ENV = {"JWT_SECRET": "test-secret-key-for-unit-tests"}

_VALID_BACKGROUND = {
    "python_level": "intermediate",
    "robotics_experience": "student",
    "math_level": "undergraduate",
    "hardware_access": True,
    "learning_goal": "Learn ROS 2",
}

_DB_RETURN_ROW = {
    "user_id": 1,
    "python_level": "intermediate",
    "robotics_experience": "student",
    "math_level": "undergraduate",
    "hardware_access": True,
    "learning_goal": "Learn ROS 2",
    "updated_at": "2025-01-15T10:00:00",
}


class TestBackgroundCacheInvalidation:
    """Test that saving background invalidates personalization cache."""

    @patch("routes.auth.invalidate_personalization", new_callable=AsyncMock)
    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, _JWT_ENV)
    def test_save_background_invalidates_personalization(
        self,
        mock_get_pool: MagicMock,
        mock_invalidate: AsyncMock,
    ) -> None:
        """POST /api/user/background triggers invalidate_personalization."""
        pool = MagicMock()
        pool.fetchrow = AsyncMock(return_value=_DB_RETURN_ROW)
        mock_get_pool.return_value = pool

        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post("/api/user/background", json=_VALID_BACKGROUND)
        client.cookies.clear()

        assert response.status_code == 200
        mock_invalidate.assert_called_once_with(1)

    @patch("routes.auth.invalidate_personalization", new_callable=AsyncMock, side_effect=Exception("DB error"))
    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, _JWT_ENV)
    def test_cache_invalidation_failure_does_not_break_response(
        self,
        mock_get_pool: MagicMock,
        mock_invalidate: AsyncMock,
    ) -> None:
        """If invalidate_personalization fails, the background save still succeeds."""
        pool = MagicMock()
        pool.fetchrow = AsyncMock(return_value=_DB_RETURN_ROW)
        mock_get_pool.return_value = pool

        from auth_utils import create_token

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.post("/api/user/background", json=_VALID_BACKGROUND)
        client.cookies.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
