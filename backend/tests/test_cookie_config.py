"""
Unit tests for cookie_config module.

TDD RED phase: These tests define the expected behaviour of get_cookie_config()
before the implementation exists. All tests MUST FAIL initially.
"""

from __future__ import annotations

import logging
import os
from unittest.mock import patch

from cookie_config import get_cookie_config


# ---------------------------------------------------------------------------
# T004 — Development defaults (no CORS_ORIGINS set)
# ---------------------------------------------------------------------------


class TestDevDefaults:
    """APP_ENV=development with no explicit CORS_ORIGINS → insecure dev cookies."""

    @patch.dict(os.environ, {"APP_ENV": "development"}, clear=False)
    def test_dev_defaults_secure_false(self) -> None:
        # Remove CORS_ORIGINS if it leaked from .env
        os.environ.pop("CORS_ORIGINS", None)
        cfg = get_cookie_config()
        assert cfg["secure"] is False

    @patch.dict(os.environ, {"APP_ENV": "development"}, clear=False)
    def test_dev_defaults_samesite_lax(self) -> None:
        os.environ.pop("CORS_ORIGINS", None)
        cfg = get_cookie_config()
        assert cfg["samesite"] == "lax"


# ---------------------------------------------------------------------------
# T005 — Development with explicit HTTP CORS origin
# ---------------------------------------------------------------------------


class TestDevExplicitCors:
    """APP_ENV=development + explicit HTTP CORS_ORIGINS → still insecure."""

    @patch.dict(
        os.environ,
        {"APP_ENV": "development", "CORS_ORIGINS": "http://localhost:3000"},
        clear=False,
    )
    def test_dev_explicit_cors_secure_false(self) -> None:
        cfg = get_cookie_config()
        assert cfg["secure"] is False

    @patch.dict(
        os.environ,
        {"APP_ENV": "development", "CORS_ORIGINS": "http://localhost:3000"},
        clear=False,
    )
    def test_dev_explicit_cors_samesite_lax(self) -> None:
        cfg = get_cookie_config()
        assert cfg["samesite"] == "lax"


# ---------------------------------------------------------------------------
# T006 — Production environment
# ---------------------------------------------------------------------------


class TestProdEnv:
    """APP_ENV=production + HTTPS CORS_ORIGINS → secure cookies."""

    @patch.dict(
        os.environ,
        {"APP_ENV": "production", "CORS_ORIGINS": "https://example.com"},
        clear=False,
    )
    def test_prod_env_secure_true(self) -> None:
        cfg = get_cookie_config()
        assert cfg["secure"] is True

    @patch.dict(
        os.environ,
        {"APP_ENV": "production", "CORS_ORIGINS": "https://example.com"},
        clear=False,
    )
    def test_prod_env_samesite_none(self) -> None:
        cfg = get_cookie_config()
        assert cfg["samesite"] == "none"


# ---------------------------------------------------------------------------
# T007 — HTTPS auto-detect overrides development
# ---------------------------------------------------------------------------


class TestHttpsAutodetectOverridesDev:
    """APP_ENV=development but CORS has HTTPS → force secure + warn."""

    @patch.dict(
        os.environ,
        {"APP_ENV": "development", "CORS_ORIGINS": "https://example.com"},
        clear=False,
    )
    def test_https_autodetect_secure_true(self) -> None:
        cfg = get_cookie_config()
        assert cfg["secure"] is True

    @patch.dict(
        os.environ,
        {"APP_ENV": "development", "CORS_ORIGINS": "https://example.com"},
        clear=False,
    )
    def test_https_autodetect_samesite_none(self) -> None:
        cfg = get_cookie_config()
        assert cfg["samesite"] == "none"

    @patch.dict(
        os.environ,
        {"APP_ENV": "development", "CORS_ORIGINS": "https://example.com"},
        clear=False,
    )
    def test_https_autodetect_logs_warning(self, caplog) -> None:  # type: ignore[no-untyped-def]
        with caplog.at_level(logging.WARNING):
            get_cookie_config()
        assert any("HTTPS origin detected" in msg for msg in caplog.messages)


# ---------------------------------------------------------------------------
# T008 — Mixed origins (HTTP + HTTPS) — HTTPS wins
# ---------------------------------------------------------------------------


class TestMixedOriginsHttpsWins:
    """Mixed HTTP + HTTPS origins → secure cookies (HTTPS wins)."""

    @patch.dict(
        os.environ,
        {
            "APP_ENV": "development",
            "CORS_ORIGINS": "http://localhost:3000,https://example.com",
        },
        clear=False,
    )
    def test_mixed_origins_secure_true(self) -> None:
        cfg = get_cookie_config()
        assert cfg["secure"] is True

    @patch.dict(
        os.environ,
        {
            "APP_ENV": "development",
            "CORS_ORIGINS": "http://localhost:3000,https://example.com",
        },
        clear=False,
    )
    def test_mixed_origins_samesite_none(self) -> None:
        cfg = get_cookie_config()
        assert cfg["samesite"] == "none"


# ---------------------------------------------------------------------------
# T009 — Invariant values (httponly, path, max_age)
# ---------------------------------------------------------------------------


class TestInvariants:
    """httponly, path, and max_age are constant regardless of environment."""

    @patch.dict(os.environ, {"APP_ENV": "development"}, clear=False)
    def test_httponly_always_true(self) -> None:
        os.environ.pop("CORS_ORIGINS", None)
        cfg = get_cookie_config()
        assert cfg["httponly"] is True

    @patch.dict(os.environ, {"APP_ENV": "production", "CORS_ORIGINS": "https://x.com"}, clear=False)
    def test_httponly_true_in_prod(self) -> None:
        cfg = get_cookie_config()
        assert cfg["httponly"] is True

    @patch.dict(os.environ, {"APP_ENV": "development"}, clear=False)
    def test_path_always_root(self) -> None:
        os.environ.pop("CORS_ORIGINS", None)
        cfg = get_cookie_config()
        assert cfg["path"] == "/"

    @patch.dict(os.environ, {"APP_ENV": "development"}, clear=False)
    def test_max_age_7_days(self) -> None:
        os.environ.pop("CORS_ORIGINS", None)
        cfg = get_cookie_config()
        assert cfg["max_age"] == 604800
