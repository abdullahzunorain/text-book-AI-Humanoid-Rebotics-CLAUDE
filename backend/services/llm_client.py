"""
Multi-model LLM client with chain-of-responsibility failover and exponential backoff.

Providers: Gemini 2.5 Flash → Groq (llama-3.3-70b-versatile) → OpenAI (gpt-4o-mini)

Public API:
    llm_client = LLMClient()
    result = await llm_client.generate(prompt, system="...", max_tokens=1024, temperature=0.3)
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import time
from typing import Protocol, runtime_checkable

from google import genai
from google.genai import types as genai_types
from groq import AsyncGroq
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TransientLLMError(Exception):
    """Raised when a provider hits a transient error (429, 500, 503, 504)."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class AllProvidersExhaustedError(Exception):
    """Raised when all LLM providers are exhausted after retries."""

    pass


# ---------------------------------------------------------------------------
# Provider Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol that all LLM providers must implement."""

    name: str

    def is_available(self) -> bool: ...

    async def generate(
        self,
        prompt: str,
        system: str,
        max_tokens: int,
        temperature: float,
    ) -> str: ...

    def mark_rate_limited(self, limit_type: str, retry_after: int) -> None: ...


# ---------------------------------------------------------------------------
# Rate-limit tracker (shared logic)
# ---------------------------------------------------------------------------


class RateLimitTracker:
    """Tracks per-provider rate-limit cooldowns."""

    def __init__(self) -> None:
        self._cooldowns: dict[str, float] = {}  # limit_type -> expiry timestamp

    def mark_limited(self, limit_type: str, retry_after: int) -> None:
        """Mark a rate-limit cooldown for the given limit type."""
        self._cooldowns[limit_type] = time.time() + retry_after

    def is_limited(self) -> bool:
        """Return True if any cooldown is still active."""
        now = time.time()
        return any(expiry > now for expiry in self._cooldowns.values())

    def get_remaining(self) -> float:
        """Return seconds remaining on the longest active cooldown."""
        now = time.time()
        remaining = [expiry - now for expiry in self._cooldowns.values() if expiry > now]
        return max(remaining) if remaining else 0.0


# ---------------------------------------------------------------------------
# Gemini Provider
# ---------------------------------------------------------------------------


class GeminiProvider:
    """Wraps Google GenAI async API for Gemini 2.5 Flash."""

    name: str = "gemini"

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        self._client = genai.Client(api_key=api_key)
        self._tracker = RateLimitTracker()

    def is_available(self) -> bool:
        return not self._tracker.is_limited()

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        try:
            response = await self._client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system if system else None,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text or ""
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                raise TransientLLMError(f"Gemini rate limited: {err_str}", retry_after=60)
            if any(code in err_str for code in ("500", "503", "504")):
                raise TransientLLMError(f"Gemini server error: {err_str}")
            raise

    def mark_rate_limited(self, limit_type: str = "rpm", retry_after: int = 60) -> None:
        self._tracker.mark_limited(limit_type, retry_after)


# ---------------------------------------------------------------------------
# Groq Provider
# ---------------------------------------------------------------------------


class GroqProvider:
    """Wraps Groq AsyncGroq client for llama-3.3-70b-versatile."""

    name: str = "groq"

    def __init__(self) -> None:
        self._client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", "not-set"))
        self._tracker = RateLimitTracker()

    def is_available(self) -> bool:
        return not self._tracker.is_limited()

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await self._client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            # groq.RateLimitError or similar
            err_str = str(e)
            err_type = type(e).__name__
            if "RateLimitError" in err_type or "429" in err_str:
                raise TransientLLMError(f"Groq rate limited: {err_str}", retry_after=60)
            if any(code in err_str for code in ("500", "503", "504")):
                raise TransientLLMError(f"Groq server error: {err_str}")
            raise

    def mark_rate_limited(self, limit_type: str = "rpm", retry_after: int = 60) -> None:
        self._tracker.mark_limited(limit_type, retry_after)


# ---------------------------------------------------------------------------
# OpenAI Provider
# ---------------------------------------------------------------------------


class OpenAIProvider:
    """Wraps OpenAI AsyncOpenAI client for gpt-4o-mini."""

    name: str = "openai"

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "not-set"))
        self._tracker = RateLimitTracker()

    def is_available(self) -> bool:
        return not self._tracker.is_limited()

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            err_str = str(e)
            err_type = type(e).__name__
            if "RateLimitError" in err_type or "429" in err_str:
                raise TransientLLMError(f"OpenAI rate limited: {err_str}", retry_after=60)
            if any(code in err_str for code in ("500", "503", "504")):
                raise TransientLLMError(f"OpenAI server error: {err_str}")
            raise

    def mark_rate_limited(self, limit_type: str = "rpm", retry_after: int = 60) -> None:
        self._tracker.mark_limited(limit_type, retry_after)


# ---------------------------------------------------------------------------
# LLM Client (chain-of-responsibility failover)
# ---------------------------------------------------------------------------


class LLMClient:
    """Multi-provider LLM client with failover and exponential backoff.

    Chain: Gemini 2.5 Flash → Groq (llama-3.3-70b-versatile) → OpenAI (gpt-4o-mini)

    Retry: exponential backoff per provider
        delay = min(initial * base^attempt, max_delay) ± 20% jitter
        Default: 5 attempts, base 7, 1s initial, capped 60s
    """

    def __init__(
        self,
        providers: list | None = None,
        max_retries: int | None = None,
        backoff_base: float | None = None,
        backoff_initial: float | None = None,
        backoff_max: float | None = None,
    ) -> None:
        self.providers: list = providers or [
            GeminiProvider(),
            GroqProvider(),
            OpenAIProvider(),
        ]
        self.max_retries = max_retries or int(os.getenv("LLM_MAX_RETRIES", "5"))
        self.backoff_base = backoff_base or float(os.getenv("LLM_BACKOFF_BASE", "7"))
        self.backoff_initial = backoff_initial or float(os.getenv("LLM_BACKOFF_INITIAL", "1"))
        self.backoff_max = backoff_max or float(os.getenv("LLM_BACKOFF_MAX", "60"))

    async def _retry_with_backoff(
        self,
        provider,
        prompt: str,
        system: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Retry a single provider with exponential backoff on transient errors."""
        for attempt in range(self.max_retries):
            try:
                return await provider.generate(
                    prompt=prompt,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            except TransientLLMError as e:
                if attempt == self.max_retries - 1:
                    # Exhausted retries for this provider
                    logger.warning(
                        "Provider %s exhausted after %d retries: %s",
                        provider.name,
                        self.max_retries,
                        e,
                    )
                    # Mark the provider as rate-limited
                    retry_after = e.retry_after or 60
                    provider.mark_rate_limited("rpm", retry_after)
                    raise
                delay = min(
                    self.backoff_initial * (self.backoff_base ** attempt),
                    self.backoff_max,
                )
                jitter = delay * random.uniform(-0.2, 0.2)
                actual_delay = delay + jitter
                logger.info(
                    "Provider %s attempt %d/%d failed, retrying in %.1fs: %s",
                    provider.name,
                    attempt + 1,
                    self.max_retries,
                    actual_delay,
                    e,
                )
                await asyncio.sleep(actual_delay)

        # Should not reach here, but just in case
        raise TransientLLMError(f"Provider {provider.name} exhausted retries")

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        """Generate content using the first available provider with failover.

        Tries each provider in order. On transient errors, retries with backoff.
        If all providers are exhausted, raises AllProvidersExhaustedError.

        Args:
            prompt: The user prompt / content to generate from.
            system: Optional system instruction.
            max_tokens: Maximum output tokens.
            temperature: Sampling temperature.

        Returns:
            Generated text string.

        Raises:
            AllProvidersExhaustedError: All providers are rate-limited or failed.
        """
        errors: list[str] = []

        for provider in self.providers:
            if not provider.is_available():
                logger.info(
                    "Skipping provider %s (rate-limited, cooldown %.0fs)",
                    provider.name,
                    provider._tracker.get_remaining() if hasattr(provider, "_tracker") else 0,
                )
                errors.append(f"{provider.name}: rate-limited (cooldown)")
                continue

            try:
                result = await self._retry_with_backoff(
                    provider=provider,
                    prompt=prompt,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                if provider != self.providers[0]:
                    logger.info(
                        "Failover success: %s handled request (primary unavailable)",
                        provider.name,
                    )
                return result
            except TransientLLMError as e:
                errors.append(f"{provider.name}: {e}")
                logger.warning("Provider %s failed, trying next: %s", provider.name, e)
                continue
            except Exception as e:
                errors.append(f"{provider.name}: unexpected error: {e}")
                logger.error("Provider %s unexpected error: %s", provider.name, e)
                continue

        raise AllProvidersExhaustedError(
            f"All LLM providers exhausted. Errors: {'; '.join(errors)}"
        )


# ---------------------------------------------------------------------------
# Module-level singleton (lazy initialization)
# ---------------------------------------------------------------------------

_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the singleton LLMClient instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
