"""
Auth routes: signup, signin, signout, me, and user background.

JWT tokens are stored in httpOnly cookies only — never in response body.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field

from auth_utils import create_token, decode_token, hash_password, verify_password
from db import get_pool

router: APIRouter = APIRouter()

_COOKIE_NAME: str = "token"
_COOKIE_MAX_AGE: int = 7 * 24 * 60 * 60  # 7 days


def _set_token_cookie(response: Response, token: str) -> None:
    """Set JWT token in an httpOnly cookie."""
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=_COOKIE_MAX_AGE,
    )


def _clear_token_cookie(response: Response) -> None:
    """Clear the JWT cookie."""
    response.set_cookie(
        key=_COOKIE_NAME,
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=0,
    )


def _get_user_id_from_cookie(request: Request) -> int:
    """Extract user_id from JWT cookie. Raises 401 if missing/invalid."""
    token: str | None = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload: dict = decode_token(token)
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Not authenticated")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class BackgroundRequest(BaseModel):
    python_level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    robotics_experience: str = Field(..., pattern="^(none|hobbyist|student|professional)$")
    math_level: str = Field(..., pattern="^(high_school|undergraduate|graduate)$")
    hardware_access: bool
    learning_goal: str = Field(default="", max_length=200)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/api/auth/signup", status_code=201)
async def signup(body: SignupRequest, response: Response) -> dict[str, Any]:
    """Create a new user account."""
    pool = get_pool()

    # Check if email is already taken
    existing = await pool.fetchrow(
        "SELECT id, email FROM users WHERE email = $1", body.email
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and insert user
    hashed: str = hash_password(body.password)
    user = await pool.fetchrow(
        "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email",
        body.email,
        hashed,
    )

    # Generate JWT and set cookie
    token: str = create_token(user_id=user["id"], email=user["email"])
    _set_token_cookie(response, token)

    return {
        "user_id": user["id"],
        "email": user["email"],
        "show_questionnaire": True,
    }


@router.post("/api/auth/signin")
async def signin(body: SigninRequest, response: Response) -> dict[str, Any]:
    """Authenticate an existing user."""
    pool = get_pool()

    # Find user
    user = await pool.fetchrow(
        "SELECT id, email, password_hash FROM users WHERE email = $1", body.email
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check if background exists
    bg = await pool.fetchrow(
        "SELECT user_id FROM user_backgrounds WHERE user_id = $1", user["id"]
    )

    # Generate JWT and set cookie
    token: str = create_token(user_id=user["id"], email=user["email"])
    _set_token_cookie(response, token)

    return {
        "user_id": user["id"],
        "email": user["email"],
        "has_background": bg is not None,
    }


@router.post("/api/auth/signout")
async def signout(response: Response) -> dict[str, str]:
    """Sign out by clearing the JWT cookie."""
    _clear_token_cookie(response)
    return {"message": "Signed out"}


@router.get("/api/auth/me")
async def me(request: Request) -> dict[str, Any]:
    """Return current user info from JWT cookie."""
    user_id: int = _get_user_id_from_cookie(request)

    # Decode token to get email
    token: str = request.cookies.get(_COOKIE_NAME, "")
    payload: dict = decode_token(token)

    pool = get_pool()
    bg = await pool.fetchrow(
        "SELECT user_id FROM user_backgrounds WHERE user_id = $1", user_id
    )

    return {
        "user_id": user_id,
        "email": payload["email"],
        "has_background": bg is not None,
    }


@router.post("/api/user/background")
async def save_background(
    body: BackgroundRequest,
    request: Request,
) -> dict[str, Any]:
    """Upsert user background (5 fields). Requires JWT cookie."""
    user_id: int = _get_user_id_from_cookie(request)
    pool = get_pool()

    # UPSERT: insert or update on conflict
    row = await pool.fetchrow(
        """
        INSERT INTO user_backgrounds (user_id, python_level, robotics_experience, math_level, hardware_access, learning_goal)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (user_id) DO UPDATE SET
            python_level = EXCLUDED.python_level,
            robotics_experience = EXCLUDED.robotics_experience,
            math_level = EXCLUDED.math_level,
            hardware_access = EXCLUDED.hardware_access,
            learning_goal = EXCLUDED.learning_goal,
            updated_at = CURRENT_TIMESTAMP
        RETURNING user_id, python_level, robotics_experience, math_level, hardware_access, learning_goal, updated_at
        """,
        user_id,
        body.python_level,
        body.robotics_experience,
        body.math_level,
        body.hardware_access,
        body.learning_goal,
    )

    return dict(row)
