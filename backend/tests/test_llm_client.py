"""
Unit tests for LLMClient: multi-model failover with exponential backoff.

Tests:
- Gemini success → returns result on first try
- Gemini 429 → Groq called as failover
- Groq 429 → OpenAI called as failover
- All providers exhausted → AllProvidersExhaustedError
- Backoff delays verified (within jitter bounds)
- Rate-limit cooldown tracking
- Jitter within ±20% bounds
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.llm_client import (
    AllProvidersExhaustedError,
    GeminiProvider,
    GroqProvider,
    LLMClient,
    OpenAIProvider,
    RateLimitTracker,
    TransientLLMError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_provider(name: str, response: str = "mock response") -> MagicMock:
    """Create a mock provider that returns a fixed response."""
    provider = MagicMock()
    provider.name = name
    provider.is_available.return_value = True
    provider.generate = AsyncMock(return_value=response)
    provider.mark_rate_limited = MagicMock()
    provider._tracker = RateLimitTracker()
    return provider


def _make_failing_provider(name: str, error: Exception | None = None) -> MagicMock:
    """Create a mock provider that always raises TransientLLMError."""
    provider = MagicMock()
    provider.name = name
    provider.is_available.return_value = True
    provider.generate = AsyncMock(
        side_effect=error or TransientLLMError(f"{name} rate limited", retry_after=60)
    )
    provider.mark_rate_limited = MagicMock()
    provider._tracker = RateLimitTracker()
    return provider


def _make_rate_limited_provider(name: str) -> MagicMock:
    """Create a mock provider that reports as unavailable (rate-limited)."""
    provider = MagicMock()
    provider.name = name
    provider.is_available.return_value = False
    provider.generate = AsyncMock()
    provider.mark_rate_limited = MagicMock()
    tracker = RateLimitTracker()
    tracker.mark_limited("rpm", 3600)  # limited for 1 hour
    provider._tracker = tracker
    return provider


# ---------------------------------------------------------------------------
# Tests: Basic Success
# ---------------------------------------------------------------------------


class TestLLMClientSuccess:
    """Test successful generation paths."""

    @pytest.mark.asyncio
    async def test_gemini_success_returns_result(self):
        """Gemini succeeds on first try → returns result directly."""
        gemini = _make_mock_provider("gemini", "Gemini answer")
        groq = _make_mock_provider("groq", "Groq answer")
        openai = _make_mock_provider("openai", "OpenAI answer")

        client = LLMClient(providers=[gemini, groq, openai], max_retries=1)
        result = await client.generate("test prompt")

        assert result == "Gemini answer"
        gemini.generate.assert_called_once()
        groq.generate.assert_not_called()
        openai.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_system_prompt_passed_through(self):
        """System prompt is forwarded to the provider."""
        gemini = _make_mock_provider("gemini", "answer")
        client = LLMClient(providers=[gemini], max_retries=1)

        await client.generate("prompt", system="You are a tutor")
        gemini.generate.assert_called_once_with(
            prompt="prompt",
            system="You are a tutor",
            max_tokens=1024,
            temperature=0.3,
        )


# ---------------------------------------------------------------------------
# Tests: Failover
# ---------------------------------------------------------------------------


class TestLLMClientFailover:
    """Test failover between providers."""

    @pytest.mark.asyncio
    async def test_gemini_429_falls_back_to_groq(self):
        """Gemini 429 → Groq called as failover."""
        gemini = _make_failing_provider("gemini")
        groq = _make_mock_provider("groq", "Groq answer")
        openai = _make_mock_provider("openai")

        client = LLMClient(providers=[gemini, groq, openai], max_retries=1)
        result = await client.generate("test")

        assert result == "Groq answer"
        groq.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_gemini_groq_429_falls_back_to_openai(self):
        """Gemini + Groq 429 → OpenAI called as last resort."""
        gemini = _make_failing_provider("gemini")
        groq = _make_failing_provider("groq")
        openai = _make_mock_provider("openai", "OpenAI answer")

        client = LLMClient(providers=[gemini, groq, openai], max_retries=1)
        result = await client.generate("test")

        assert result == "OpenAI answer"
        openai.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_all_providers_exhausted_raises_error(self):
        """All 3 providers fail → AllProvidersExhaustedError."""
        gemini = _make_failing_provider("gemini")
        groq = _make_failing_provider("groq")
        openai = _make_failing_provider("openai")

        client = LLMClient(providers=[gemini, groq, openai], max_retries=1)

        with pytest.raises(AllProvidersExhaustedError) as exc_info:
            await client.generate("test")

        assert "All LLM providers exhausted" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_skip_rate_limited_provider(self):
        """Provider marked as rate-limited is skipped entirely."""
        gemini = _make_rate_limited_provider("gemini")
        groq = _make_mock_provider("groq", "Groq answer")
        openai = _make_mock_provider("openai")

        client = LLMClient(providers=[gemini, groq, openai], max_retries=1)
        result = await client.generate("test")

        assert result == "Groq answer"
        gemini.generate.assert_not_called()
        groq.generate.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: Backoff & Jitter
# ---------------------------------------------------------------------------


class TestLLMClientBackoff:
    """Test exponential backoff and jitter."""

    @pytest.mark.asyncio
    async def test_backoff_delays_increase_exponentially(self):
        """Verify that retry delays follow exponential pattern."""
        call_count = 0

        async def failing_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientLLMError("rate limited")
            return "success after retries"

        provider = _make_mock_provider("test", "")
        provider.generate = AsyncMock(side_effect=failing_then_success)

        # Use small delays for fast test
        client = LLMClient(
            providers=[provider],
            max_retries=3,
            backoff_base=2,
            backoff_initial=0.01,
            backoff_max=1,
        )

        with patch("services.llm_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await client.generate("test")

        assert result == "success after retries"
        assert mock_sleep.call_count == 2  # 2 retries before success

        # Check delays are in expected range (with jitter ±20%)
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        # attempt 0: 0.01 * 2^0 = 0.01 ± 20% → [0.008, 0.012]
        assert 0.006 <= delays[0] <= 0.014
        # attempt 1: 0.01 * 2^1 = 0.02 ± 20% → [0.016, 0.024]
        assert 0.014 <= delays[1] <= 0.026

    @pytest.mark.asyncio
    async def test_backoff_capped_at_max(self):
        """Backoff delay should never exceed max_delay."""
        call_count = 0

        async def always_fail(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise TransientLLMError("rate limited")

        provider = _make_mock_provider("test", "")
        provider.generate = AsyncMock(side_effect=always_fail)

        client = LLMClient(
            providers=[provider],
            max_retries=5,
            backoff_base=10,       # aggressive base
            backoff_initial=1,
            backoff_max=2,         # cap at 2s
        )

        with patch("services.llm_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(AllProvidersExhaustedError):
                await client.generate("test")

        # All delays should be ≤ max_delay + 20% jitter = 2.4
        for call in mock_sleep.call_args_list:
            assert call.args[0] <= 2.5  # 2.0 * 1.2 = 2.4, with margin

    @pytest.mark.asyncio
    async def test_jitter_within_bounds(self):
        """Jitter should be within ±20% of the base delay."""
        call_count = 0

        async def fail_once(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TransientLLMError("rate limited")
            return "ok"

        provider = _make_mock_provider("test", "")
        provider.generate = AsyncMock(side_effect=fail_once)

        # Run multiple times to verify jitter
        for _ in range(10):
            call_count = 0
            provider.generate.side_effect = fail_once

            client = LLMClient(
                providers=[provider],
                max_retries=2,
                backoff_base=2,
                backoff_initial=1.0,
                backoff_max=60,
            )

            with patch("services.llm_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await client.generate("test")

            if mock_sleep.call_count > 0:
                delay = mock_sleep.call_args_list[0].args[0]
                # base delay = 1.0 * 2^0 = 1.0; jitter ±20% → [0.8, 1.2]
                assert 0.8 <= delay <= 1.2, f"Jitter out of bounds: {delay}"


# ---------------------------------------------------------------------------
# Tests: Rate-limit Tracker
# ---------------------------------------------------------------------------


class TestRateLimitTracker:
    """Test rate-limit cooldown tracking."""

    def test_not_limited_by_default(self):
        tracker = RateLimitTracker()
        assert not tracker.is_limited()

    def test_mark_limited_and_check(self):
        tracker = RateLimitTracker()
        tracker.mark_limited("rpm", 60)
        assert tracker.is_limited()

    def test_cooldown_expires(self):
        tracker = RateLimitTracker()
        tracker.mark_limited("rpm", 0)  # expires immediately
        assert not tracker.is_limited()

    def test_get_remaining(self):
        tracker = RateLimitTracker()
        tracker.mark_limited("rpm", 120)
        remaining = tracker.get_remaining()
        assert 119 <= remaining <= 120

    def test_multiple_limits(self):
        tracker = RateLimitTracker()
        tracker.mark_limited("rpm", 60)
        tracker.mark_limited("rpd", 3600)
        assert tracker.is_limited()
        remaining = tracker.get_remaining()
        assert remaining > 60  # rpd limit is longer


# ---------------------------------------------------------------------------
# Tests: Unexpected errors
# ---------------------------------------------------------------------------


class TestLLMClientUnexpectedErrors:
    """Test handling of non-transient errors."""

    @pytest.mark.asyncio
    async def test_unexpected_error_falls_through_to_next_provider(self):
        """Non-transient error in one provider → try next."""
        gemini = _make_mock_provider("gemini", "")
        gemini.generate = AsyncMock(side_effect=ValueError("API key invalid"))

        groq = _make_mock_provider("groq", "Groq answer")

        client = LLMClient(providers=[gemini, groq], max_retries=1)
        result = await client.generate("test")

        assert result == "Groq answer"

    @pytest.mark.asyncio
    async def test_all_unexpected_errors_raise_exhausted(self):
        """All providers raise unexpected errors → AllProvidersExhaustedError."""
        gemini = _make_mock_provider("gemini", "")
        gemini.generate = AsyncMock(side_effect=ValueError("bad"))
        groq = _make_mock_provider("groq", "")
        groq.generate = AsyncMock(side_effect=RuntimeError("bad"))

        client = LLMClient(providers=[gemini, groq], max_retries=1)
        with pytest.raises(AllProvidersExhaustedError):
            await client.generate("test")
