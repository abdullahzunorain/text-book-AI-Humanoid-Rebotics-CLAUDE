"""
Agent infrastructure: shared Gemini client, three agents, embed + run helpers.

Replaces services/llm_client.py (406-line hand-rolled failover chain) with the
OpenAI Agents SDK.  All agents use Gemini models via Google's OpenAI-compatible
endpoint.  Embeddings also go through the same client.

Public API:
    tutor_agent          — Agent for RAG chatbot answers
    personalization_agent — Agent for chapter personalization
    translation_agent    — Agent for English → Urdu translation
    embed(text)          — Async embedding via gemini-embedding-001
    run_agent(agent, input) — Run an agent and return its final_output string
"""

from __future__ import annotations

import logging
import os

from agents import (
    Agent,
    ModelSettings,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tracing — must be disabled; we have no OpenAI platform key.
# ---------------------------------------------------------------------------
set_tracing_disabled(True)

# ---------------------------------------------------------------------------
# Shared Gemini client (singleton)
# ---------------------------------------------------------------------------
_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if not _GOOGLE_API_KEY:
    logger.warning(
        "GOOGLE_API_KEY is not set — all agent and embedding calls will fail."
    )

_client = AsyncOpenAI(
    api_key=_GOOGLE_API_KEY,
    base_url=_GEMINI_BASE_URL,
)

# ---------------------------------------------------------------------------
# Shared model
# ---------------------------------------------------------------------------
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

_model = OpenAIChatCompletionsModel(
    model=GENERATION_MODEL,
    openai_client=_client,
)

# ---------------------------------------------------------------------------
# System prompts (extracted from existing services)
# ---------------------------------------------------------------------------
TUTOR_SYSTEM_PROMPT = (
    "You are a helpful study companion for the Physical AI & Humanoid Robotics textbook. "
    "Answer questions based ONLY on the provided textbook context. If the context doesn't contain "
    "enough information to answer, say so honestly. Keep answers concise, accurate, and educational. "
    "When referencing specific chapters or sections, mention them by name. "
    "Stay on topic — only answer questions related to Physical AI, ROS 2, robotics, and the textbook content. "
    'If a question is clearly off-topic, politely redirect: '
    '"I\'m designed to help with the Physical AI textbook content. Could you ask something about the topics covered?"'
)

PERSONALIZATION_SYSTEM_PROMPT = (
    "You are an AI tutor. Adapt textbook content for the student profile."
)

TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional Urdu translator for educational robotics content."
)

# ---------------------------------------------------------------------------
# Agent instances
# ---------------------------------------------------------------------------
tutor_agent = Agent(
    name="tutor",
    instructions=TUTOR_SYSTEM_PROMPT,
    model=_model,
    model_settings=ModelSettings(temperature=0.3, max_tokens=1024),
)

personalization_agent = Agent(
    name="personalizer",
    instructions=PERSONALIZATION_SYSTEM_PROMPT,
    model=_model,
    model_settings=ModelSettings(temperature=0.4, max_tokens=4096),
)

translation_agent = Agent(
    name="translator",
    instructions=TRANSLATION_SYSTEM_PROMPT,
    model=_model,
    model_settings=ModelSettings(temperature=0.3, max_tokens=4096),
)

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


async def embed(text: str) -> list[float]:
    """Embed *text* via the Gemini OpenAI-compatible embeddings endpoint.

    Returns a list of floats (3 072 dimensions for ``gemini-embedding-001``).
    """
    response = await _client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
    )
    return response.data[0].embedding


async def run_agent(agent: Agent, *, input: str) -> str:
    """Run *agent* with the given *input* and return the final output text.

    Raises standard ``openai`` exceptions on failure (``RateLimitError``,
    ``APIError``, ``APITimeoutError``).
    """
    result = await Runner.run(agent, input=input)
    return result.final_output
