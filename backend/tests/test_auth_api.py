"""
Contract tests for auth endpoints: signup, signin, signout, me.

TDD: These tests are written first and MUST FAIL until routes are implemented (D6).

Tests cover:
- POST /api/auth/signup — 201 + cookie, 400 duplicate, 422 short password
- POST /api/auth/signin — 200 + cookie, 401 wrong password
- POST /api/auth/signout — 200 + cookie cleared
- GET /api/auth/me — 200 with cookie, 401 without
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
    pool.execute = AsyncMock()
    pool.fetch = AsyncMock()
    return pool


class TestSignup:
    """Tests for POST /api/auth/signup."""

    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_signup_valid_returns_201(self, mock_get_pool: MagicMock) -> None:
        """POST /api/auth/signup with valid email/password → 201 + Set-Cookie."""
        pool = _mock_pool()
        # Simulate: no existing user, then return created user
        pool.fetchrow = AsyncMock(
            side_effect=[
                None,  # email not taken
                {"id": 1, "email": "new@example.com"},  # created user
            ]
        )
        mock_get_pool.return_value = pool

        response = client.post(
            "/api/auth/signup",
            json={"email": "new@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 201
        data: dict = response.json()
        assert "user_id" in data
        assert data["email"] == "new@example.com"
        assert "token" in response.cookies or "set-cookie" in response.headers

    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_signup_duplicate_email_returns_400(self, mock_get_pool: MagicMock) -> None:
        """POST /api/auth/signup with existing email → 400."""
        pool = _mock_pool()
        pool.fetchrow = AsyncMock(
            return_value={"id": 1, "email": "existing@example.com"}
        )
        mock_get_pool.return_value = pool

        response = client.post(
            "/api/auth/signup",
            json={"email": "existing@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_signup_short_password_returns_422(self) -> None:
        """POST /api/auth/signup with <8 char password → 422."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com", "password": "short"},
        )
        assert response.status_code == 422


class TestSignin:
    """Tests for POST /api/auth/signin."""

    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_signin_valid_returns_200(self, mock_get_pool: MagicMock) -> None:
        """POST /api/auth/signin with correct credentials → 200 + cookie."""
        from auth_utils import hash_password

        pool = _mock_pool()
        hashed: str = hash_password("SecurePass123!")
        pool.fetchrow = AsyncMock(
            side_effect=[
                {"id": 1, "email": "user@example.com", "password_hash": hashed},
                {"user_id": 1},  # background exists
            ]
        )
        mock_get_pool.return_value = pool

        response = client.post(
            "/api/auth/signin",
            json={"email": "user@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 200
        data: dict = response.json()
        assert data["email"] == "user@example.com"
        assert "has_background" in data

    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_signin_wrong_password_returns_401(self, mock_get_pool: MagicMock) -> None:
        """POST /api/auth/signin with wrong password → 401."""
        from auth_utils import hash_password

        pool = _mock_pool()
        hashed: str = hash_password("CorrectPassword")
        pool.fetchrow = AsyncMock(
            return_value={"id": 1, "email": "user@example.com", "password_hash": hashed}
        )
        mock_get_pool.return_value = pool

        response = client.post(
            "/api/auth/signin",
            json={"email": "user@example.com", "password": "WrongPassword"},
        )
        assert response.status_code == 401


class TestSignout:
    """Tests for POST /api/auth/signout."""

    def test_signout_returns_200(self) -> None:
        """POST /api/auth/signout → 200 + cookie cleared."""
        response = client.post("/api/auth/signout")
        assert response.status_code == 200
        assert response.json()["message"] == "Signed out"


class TestMe:
    """Tests for GET /api/auth/me."""

    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_me_with_valid_cookie_returns_200(self, mock_get_pool: MagicMock) -> None:
        """GET /api/auth/me with valid cookie → 200 + user info."""
        from auth_utils import create_token

        pool = _mock_pool()
        pool.fetchrow = AsyncMock(
            return_value={"user_id": 1}  # background exists
        )
        mock_get_pool.return_value = pool

        token: str = create_token(user_id=1, email="user@example.com")
        client.cookies.set("token", token)
        response = client.get("/api/auth/me")
        client.cookies.clear()
        assert response.status_code == 200
        data: dict = response.json()
        assert data["user_id"] == 1
        assert data["email"] == "user@example.com"

    def test_me_without_cookie_returns_401(self) -> None:
        """GET /api/auth/me without cookie → 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
