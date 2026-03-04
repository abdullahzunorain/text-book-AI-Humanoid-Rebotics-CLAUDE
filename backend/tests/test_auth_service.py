"""
Unit tests for auth_utils — password hashing and JWT token operations.

TDD: These tests are written first and MUST FAIL until auth_utils is implemented (D4).

Tests cover:
- hash_password() returns bcrypt hash
- verify_password() validates correctly
- create_token() returns valid JWT with sub, email, exp claims
- decode_token() extracts user_id and email, raises on expired/invalid
"""

from __future__ import annotations

import os
import time
from unittest.mock import patch

import pytest


class TestPasswordHashing:
    """Tests for bcrypt password hashing."""

    def test_hash_password_returns_string(self) -> None:
        """hash_password() returns a non-empty string."""
        from auth_utils import hash_password

        hashed: str = hash_password("TestPassword123!")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_is_bcrypt(self) -> None:
        """hash_password() returns a bcrypt hash (starts with $2b$)."""
        from auth_utils import hash_password

        hashed: str = hash_password("TestPassword123!")
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self) -> None:
        """verify_password() returns True for correct password."""
        from auth_utils import hash_password, verify_password

        password: str = "SecurePass123!"
        hashed: str = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self) -> None:
        """verify_password() returns False for wrong password."""
        from auth_utils import hash_password, verify_password

        hashed: str = hash_password("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False


class TestJWT:
    """Tests for JWT token creation and decoding."""

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_create_token_returns_string(self) -> None:
        """create_token() returns a non-empty JWT string."""
        from auth_utils import create_token

        token: str = create_token(user_id=42, email="test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_decode_token_extracts_claims(self) -> None:
        """decode_token() returns dict with user_id and email."""
        from auth_utils import create_token, decode_token

        token: str = create_token(user_id=42, email="test@example.com")
        payload: dict = decode_token(token)

        assert payload["sub"] == 42
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_decode_token_invalid_raises(self) -> None:
        """decode_token() raises on invalid token."""
        from auth_utils import decode_token

        with pytest.raises(Exception):
            decode_token("this.is.not.a.valid.jwt")

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key-for-unit-tests"})
    def test_decode_token_expired_raises(self) -> None:
        """decode_token() raises on expired token."""
        from auth_utils import decode_token

        # Create a token that's already expired (mock time)
        from jose import jwt

        expired_payload: dict = {
            "sub": 42,
            "email": "test@example.com",
            "exp": int(time.time()) - 10,  # 10 seconds ago
        }
        expired_token: str = jwt.encode(
            expired_payload,
            "test-secret-key-for-unit-tests",
            algorithm="HS256",
        )

        with pytest.raises(Exception):
            decode_token(expired_token)
