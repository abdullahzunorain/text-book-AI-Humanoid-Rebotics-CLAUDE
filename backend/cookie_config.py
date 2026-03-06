"""
Centralised cookie-attribute resolver.

Public API:
    get_cookie_config() -> dict
        Returns {secure, samesite, httponly, path, max_age} based on
        APP_ENV and CORS_ORIGINS environment variables.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

_COOKIE_MAX_AGE: int = 7 * 24 * 60 * 60  # 604 800 seconds = 7 days


def get_cookie_config() -> dict:
    """Return environment-aware cookie attributes.

    Decision matrix:
        - production  OR  any HTTPS origin detected → secure=True, samesite="none"
        - development AND only HTTP origins           → secure=False, samesite="lax"

    Invariants (always):
        httponly=True, path="/", max_age=604800

    Side-effect:
        Logs a WARNING when HTTPS origins are detected but APP_ENV != "production".
    """
    app_env: str = os.getenv("APP_ENV", "development")
    cors_raw: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    )
    origins: list[str] = [o.strip() for o in cors_raw.split(",") if o.strip()]

    has_https: bool = any(o.startswith("https://") for o in origins)

    if app_env == "production" or has_https:
        secure = True
        samesite = "none"
    else:
        secure = False
        samesite = "lax"

    # FR-011: auto-detect guard — warn when HTTPS origin found in non-production
    if has_https and app_env != "production":
        logger.warning(
            "HTTPS origin detected with APP_ENV=%s — forcing Secure cookies",
            app_env,
        )

    return {
        "secure": secure,
        "samesite": samesite,
        "httponly": True,
        "path": "/",
        "max_age": _COOKIE_MAX_AGE,
    }
