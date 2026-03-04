"""
Authentication utilities: bcrypt password hashing and JWT token management.

Public API:
    hash_password(password) -> str
    verify_password(plain, hashed) -> bool
    create_token(user_id, email) -> str
    decode_token(token) -> dict
"""

from __future__ import annotations

import os
import time

import bcrypt
from jose import JWTError, jwt

_ALGORITHM: str = "HS256"
_TOKEN_EXPIRE_SECONDS: int = 7 * 24 * 60 * 60  # 7 days
_BCRYPT_ROUNDS: int = 12


def _get_secret() -> str:
    """Get JWT secret from environment. Never hardcoded."""
    secret: str = os.getenv("JWT_SECRET", "")
    if not secret:
        raise ValueError("JWT_SECRET environment variable is required")
    return secret


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with cost 12.

    Args:
        password: Plain text password.

    Returns:
        Bcrypt hash string.
    """
    salt: bytes = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed: bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash.

    Args:
        plain: Plain text password to verify.
        hashed: Bcrypt hash to compare against.

    Returns:
        True if the password matches.
    """
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, email: str) -> str:
    """Create an HS256 JWT token with 7-day expiry.

    Args:
        user_id: User's database ID (stored as 'sub' claim).
        email: User's email address.

    Returns:
        Encoded JWT string.
    """
    payload: dict = {
        "sub": str(user_id),
        "email": email,
        "exp": int(time.time()) + _TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, _get_secret(), algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.

    Returns:
        Dict with claims: sub (user_id as int), email, exp.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload: dict = jwt.decode(token, _get_secret(), algorithms=[_ALGORITHM])
        # Convert sub back to int for convenience
        payload["sub"] = int(payload["sub"])
        return payload
    except JWTError:
        raise
