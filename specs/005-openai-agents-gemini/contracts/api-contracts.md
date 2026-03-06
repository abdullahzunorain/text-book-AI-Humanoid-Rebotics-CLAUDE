# API Contracts: OpenAI Agents SDK with Gemini Models

**Feature**: 005-openai-agents-gemini  
**Date**: 2026-03-06

## Contract Summary

All existing API endpoints remain **identical** in request/response schema. This feature is a backend-only refactor — the agent layer is an internal implementation detail invisible to API consumers.

**No new endpoints are introduced. No existing endpoints are modified.**

## Unchanged Endpoints

### POST /api/chat

**Auth**: Optional (JWT cookie)

```json
// Request
{
  "question": "string (1-2000 chars, required)",
  "selected_text": "string (0-2000 chars, optional)"
}

// Response 200
{
  "answer": "string",
  "sources": ["string"]
}

// Response 400
{ "detail": "Question cannot be empty" }

// Response 429
{ "detail": "AI service rate limit reached. Please wait a moment and try again." }

// Response 503
{ "detail": "Service temporarily unavailable. Please try again later." }
```

**Internal change**: `generate_answer()` now calls `Runner.run(tutor_agent, ...)` instead of `llm_client.generate(...)`.

---

### POST /api/translate

**Auth**: Required (JWT cookie → 401 if missing/expired)

```json
// Request
{
  "chapter_slug": "string (1-200 chars, required)"
}

// Response 200
{
  "translated_content": "string",
  "original_code_blocks": ["string"]
}

// Response 401
{ "detail": "not_authenticated" | "session_expired" | "invalid_token" }

// Response 404
{ "detail": "Chapter not found: {slug}" }

// Response 429
{ "detail": "Rate limit exceeded. Try again in 60 seconds." }
// or
{ "detail": "AI service rate limit reached. Please wait a moment and try again." }

// Response 503
{ "detail": "All AI providers are temporarily unavailable. Please try again later." }
```

**Internal change**: `translate_to_urdu()` now calls `Runner.run(translation_agent, ...)` instead of `llm_client.generate(...)`.

---

### POST /api/personalize

**Auth**: Required (JWT cookie → 401 if missing/expired)

```json
// Request
{
  "chapter_slug": "string (1-200 chars, required)"
}

// Response 200
{
  "personalized_content": "string"
}

// Response 401
{ "detail": "not_authenticated" | "session_expired" | "invalid_token" }

// Response 404
{ "detail": "Chapter not found" }

// Response 503
{ "detail": "All AI providers are temporarily unavailable. Please try again later." }
```

**Internal change**: `personalize_chapter()` now calls `Runner.run(personalization_agent, ...)` instead of `llm_client.generate(...)`.

---

### GET /api/chat/history

**Auth**: Required (JWT cookie → 401 if missing/expired)

```json
// Query params: ?limit=50&offset=0

// Response 200
{
  "messages": [
    {
      "id": 1,
      "question": "string",
      "answer": "string",
      "selected_text": "string | null",
      "sources": ["string"],
      "created_at": "ISO datetime string"
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}

// Response 401
{ "detail": "not_authenticated" | "session_expired" | "invalid_token" }
```

**Internal change**: None — this endpoint does not use LLM.

---

## Internal Agent Contracts (not externally exposed)

These are the internal interfaces between the service layer and the agent infrastructure.

### Agent Infrastructure Module

**File**: `backend/services/agent_config.py`

```python
# Public API
def get_gemini_client() -> AsyncOpenAI:
    """Returns singleton AsyncOpenAI client configured for Gemini endpoint."""

def get_tutor_agent() -> Agent:
    """Returns the Tutor Agent configured with RAG system prompt."""

def get_personalization_agent() -> Agent:
    """Returns the Personalization Agent configured with adaptation instructions."""

def get_translation_agent() -> Agent:
    """Returns the Translation Agent configured with Urdu translation instructions."""

async def run_agent(agent: Agent, input: str) -> str:
    """Run an agent and return final_output text. Raises on error."""
```

### Error Mapping

| Agent/SDK Exception | HTTP Status | Detail |
|---------------------|------------|--------|
| `openai.RateLimitError` | 429 | "AI service rate limit reached..." |
| `openai.APIError` (500/503) | 503 | "Service temporarily unavailable..." |
| `openai.APITimeoutError` | 503 | "Service temporarily unavailable..." |
| Any other `Exception` | 503 | "Service temporarily unavailable..." |
