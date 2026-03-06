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
        assert data["has_background"] is False  # new user always has no background
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


# ---------------------------------------------------------------------------
# T014 — Signup sets cookie with development attributes
# ---------------------------------------------------------------------------


class TestSignupCookieAttrs:
    """US1: Signup must set cookie with dev attrs (no Secure, SameSite=Lax)."""

    @patch("routes.auth.get_pool")
    @patch.dict(
        os.environ,
        {"JWT_SECRET": "test-secret-key-for-unit-tests", "APP_ENV": "development"},
        clear=False,
    )
    def test_signup_sets_cookie_with_dev_attrs(self, mock_get_pool: MagicMock) -> None:
        """POST /api/auth/signup → Set-Cookie with HttpOnly, SameSite=Lax, Path=/, Max-Age=604800, NO Secure."""
        os.environ.pop("CORS_ORIGINS", None)
        pool = _mock_pool()
        pool.fetchrow = AsyncMock(
            side_effect=[
                None,  # email not taken
                {"id": 42, "email": "dev@test.com"},  # created user
            ]
        )
        mock_get_pool.return_value = pool

        response = client.post(
            "/api/auth/signup",
            json={"email": "dev@test.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 201

        # Parse Set-Cookie header
        set_cookie: str = response.headers.get("set-cookie", "")
        assert "token=" in set_cookie, f"No token cookie in: {set_cookie}"
        set_cookie_lower = set_cookie.lower()
        assert "httponly" in set_cookie_lower
        assert "samesite=lax" in set_cookie_lower
        assert "path=/" in set_cookie_lower
        assert "max-age=604800" in set_cookie_lower
        # In development, Secure flag must NOT be present
        assert "secure" not in set_cookie_lower, f"Secure flag found in dev: {set_cookie}"


# ---------------------------------------------------------------------------
# T015 — 401 with no cookie returns "not_authenticated"
# ---------------------------------------------------------------------------


class TestNotAuthenticatedDetail:
    """US1: Missing cookie should return detail='not_authenticated' (not generic)."""

    def test_401_no_cookie_returns_not_authenticated(self) -> None:
        """GET /api/auth/me without cookie → 401, detail='not_authenticated'."""
        client.cookies.clear()
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "not_authenticated"


# ---------------------------------------------------------------------------
# T019 — Signout clears cookie with matching attributes
# ---------------------------------------------------------------------------


class TestSignoutClearsCookieAttrs:
    """US2: Signout must clear cookie with matching attrs (SameSite, Secure) + Max-Age=0."""

    @patch.dict(
        os.environ,
        {"APP_ENV": "development"},
        clear=False,
    )
    def test_signout_clears_cookie_matching_attrs(self) -> None:
        """POST /api/auth/signout → Set-Cookie with token=; Max-Age=0; matching SameSite/Secure."""
        os.environ.pop("CORS_ORIGINS", None)
        response = client.post("/api/auth/signout")
        assert response.status_code == 200

        set_cookie: str = response.headers.get("set-cookie", "")
        set_cookie_lower = set_cookie.lower()
        # Cookie value must be empty (cleared)
        assert 'token=""' in set_cookie_lower or "token=;" in set_cookie_lower or 'token= ;' in set_cookie_lower, (
            f"Cookie not cleared: {set_cookie}"
        )
        assert "max-age=0" in set_cookie_lower, f"Max-Age=0 missing: {set_cookie}"
        assert "httponly" in set_cookie_lower
        assert "samesite=lax" in set_cookie_lower
        # In dev, Secure should NOT be present
        assert "secure" not in set_cookie_lower, f"Secure found in dev clear: {set_cookie}"


# ---------------------------------------------------------------------------
# T020 — Signin sets cookie with dev attributes
# ---------------------------------------------------------------------------


class TestSigninCookieAttrs:
    """US2: Signin must set cookie with same dev attrs as signup."""

    @patch("routes.auth.get_pool")
    @patch.dict(
        os.environ,
        {"JWT_SECRET": "test-secret-key-for-unit-tests", "APP_ENV": "development"},
        clear=False,
    )
    def test_signin_sets_cookie_with_dev_attrs(self, mock_get_pool: MagicMock) -> None:
        """POST /api/auth/signin → Set-Cookie with HttpOnly, SameSite=Lax, Path=/, Max-Age=604800, NO Secure."""
        os.environ.pop("CORS_ORIGINS", None)
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

        set_cookie: str = response.headers.get("set-cookie", "")
        set_cookie_lower = set_cookie.lower()
        assert "token=" in set_cookie_lower
        assert "httponly" in set_cookie_lower
        assert "samesite=lax" in set_cookie_lower
        assert "path=/" in set_cookie_lower
        assert "max-age=604800" in set_cookie_lower
        assert "secure" not in set_cookie_lower, f"Secure flag found in dev: {set_cookie}"


# ---------------------------------------------------------------------------
# T023 — Expired JWT returns "session_expired"
# ---------------------------------------------------------------------------


class TestSessionExpired:
    """US3: Expired JWT must return detail='session_expired'."""

    @patch("routes.auth.get_pool")
    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_401_expired_returns_session_expired(self, mock_get_pool: MagicMock) -> None:
        """GET /api/auth/me with expired JWT → 401, detail='session_expired'."""
        import time

        from jose import jwt

        # Create a token that expired 10 seconds ago
        payload = {
            "sub": "1",
            "email": "user@example.com",
            "exp": int(time.time()) - 10,
        }
        expired_token = jwt.encode(
            payload, "test-secret-key-for-unit-tests", algorithm="HS256"
        )

        client.cookies.set("token", expired_token)
        response = client.get("/api/auth/me")
        client.cookies.clear()
        assert response.status_code == 401
        assert response.json()["detail"] == "session_expired"


# ---------------------------------------------------------------------------
# T024 — Malformed JWT returns "invalid_token"
# ---------------------------------------------------------------------------


class TestInvalidToken:
    """US3: Malformed/corrupted JWT must return detail='invalid_token'."""

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_401_malformed_returns_invalid_token(self) -> None:
        """GET /api/auth/me with garbage token → 401, detail='invalid_token'."""
        client.cookies.set("token", "this.is.not.a.valid.jwt")
        response = client.get("/api/auth/me")
        client.cookies.clear()
        assert response.status_code == 401
        assert response.json()["detail"] == "invalid_token"