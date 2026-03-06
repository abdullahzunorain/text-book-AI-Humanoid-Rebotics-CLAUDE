# Research: Physical AI & Humanoid Robotics Textbook Platform

**Feature Branch**: `004-physical-ai-textbook`  
**Date**: 2026-03-06  
**Status**: Complete  
**Input**: Technical Context unknowns from plan.md

---

## Research Tasks

### R1: Multi-Model LLM Failover Pattern

**Context**: The system needs to failover from Gemini → Groq → OpenAI when rate-limited (FR-030).

**Decision**: Chain-of-responsibility pattern with per-provider health tracking.

**Rationale**:
- Each provider has different rate limits (RPM, TPM, RPD) and error codes
- A central `LLMClient` class maintains an ordered list of providers
- Each provider implements a common `LLMProvider` protocol
- The client iterates through providers, skipping those marked as rate-limited
- This is the simplest pattern that handles heterogeneous providers

**Alternatives considered**:
1. **Round-robin load balancing** — Rejected: wastes quota on secondary providers when primary is healthy
2. **Circuit breaker pattern** — Considered but overkill: only 3 providers, no complex state machine needed. A simple cooldown timer per provider achieves the same effect
3. **External proxy (LiteLLM, OpenRouter)** — Rejected: adds an external dependency and network hop; we want direct control

**Implementation notes**:
- Gemini errors: `google.genai` raises exceptions; check for `RESOURCE_EXHAUSTED` or HTTP 429 in message
- Groq errors: `groq` SDK raises `groq.RateLimitError` (HTTP 429) with `retry-after` header
- OpenAI errors: `openai` SDK raises `openai.RateLimitError` (HTTP 429) with `retry-after` header
- All three SDKs support async: `google.genai` via `client.aio`, `groq` via `AsyncGroq`, `openai` via `AsyncOpenAI`

---

### R2: Exponential Backoff Implementation

**Context**: Retry transient errors (HTTP 429, 500, 503, 504) with exponential backoff: 5 attempts, base 7, 1s initial (FR-031).

**Decision**: Custom async retry with configurable parameters, capped max delay.

**Rationale**:
- Formula: `delay = min(initial * base^attempt, max_delay)` → 1s, 7s, 49s, capped at 60s, 60s
- The base of 7 is aggressive but appropriate for LLM APIs that may take minutes to recover
- Capping at 60s prevents waiting 343s+ which would exceed the SC-002 10s target for chatbot responses
- When retries exhaust for one provider, immediately try the next provider (no backoff between providers)

**Alternatives considered**:
1. **Tenacity library** — Rejected: adds a dependency for ~30 lines of custom code. Our retry logic is specific (per-provider tracking, failover)
2. **Fixed delay retry** — Rejected: wastes time on fast-recovering 429s and doesn't adapt to sustained outages
3. **Jitter** — Considered: adding random jitter (±20%) could help with thundering herd. At 10-20 users, not critical but low cost. INCLUDED.

**Implementation**:
```python
async def _retry_with_backoff(self, provider, prompt, **kwargs):
    for attempt in range(self.max_retries):
        try:
            return await provider.generate(prompt, **kwargs)
        except TransientError as e:
            if attempt == self.max_retries - 1:
                raise
            delay = min(self.initial * (self.base ** attempt), self.max_delay)
            jitter = delay * random.uniform(-0.2, 0.2)
            await asyncio.sleep(delay + jitter)
```

---

### R3: DB Caching for AI-Generated Content

**Context**: Cache personalized/translated chapter content in Neon DB per (user_id, chapter_slug) (FR-033, FR-034).

**Decision**: Single `content_cache` table with UPSERT semantics and type discriminator.

**Rationale**:
- Both personalization and translation produce the same output shape (markdown string)
- A `cache_type` column (`'personalization'` | `'translation'`) distinguishes them
- UPSERT via `INSERT ... ON CONFLICT (user_id, chapter_slug, cache_type) DO UPDATE` ensures atomicity
- No TTL needed: personalization invalidated by profile change; translation never invalidated

**Alternatives considered**:
1. **Redis cache** — Rejected: adds infrastructure complexity. Neon DB is already connected; 10-20 users won't benefit from Redis speed. DB round-trip adds ~5ms, negligible vs. LLM's 5-15s generation time
2. **Separate tables per type** — Rejected: identical schema, unnecessary duplication
3. **File-based cache** — Rejected: Railway filesystem is ephemeral; would lose cache on redeploy

**Cache hit rate estimate**: At 10-20 users × 17 chapters × 2 types = 340-680 potential cache entries. Neon free tier handles this trivially.

**Invalidation logic**:
- `DELETE FROM content_cache WHERE user_id = $1 AND cache_type = 'personalization'` — called in `POST /api/user/background` handler
- Translation cache: no invalidation (same Urdu translation regardless of profile)

---

### R4: Chat History Persistence

**Context**: Persist chat Q&A per user in Neon DB, surviving sign-out, retained indefinitely (FR-011).

**Decision**: `chat_messages` table with user_id FK, ordered by `created_at DESC`.

**Rationale**:
- Simple append-only table — no updates, no deletes (at hackathon scale)
- JSONB column for `sources` allows flexible source metadata
- `selected_text` is nullable (only populated for selected-text Q&A)
- Paginated retrieval via `LIMIT/OFFSET` for `GET /api/chat/history`

**Alternatives considered**:
1. **Conversation/thread model** — Considered: grouping messages into conversations would support multi-turn context. Rejected for MVP: the current chatbot is single-turn Q&A. Can be added post-MVP.
2. **Local storage (frontend)** — Rejected: doesn't survive sign-out or device change per FR-011
3. **Separate history service** — Rejected: overkill at this scale; direct DB queries are sufficient

**Storage estimate**: Average message ~500 bytes (question + answer). 20 users × 50 messages = 1000 rows × 500B = ~500KB. Trivial for Neon.

---

### R5: Groq SDK Integration

**Context**: Groq is the second failover provider.

**Decision**: Use official `groq` Python SDK with `AsyncGroq` client.

**Rationale**:
- Official SDK handles auth, retries (disabled in our wrapper), and response parsing
- Compatible model: `llama-3.3-70b-versatile` or `gemma2-9b-it` — best available for educational content
- Groq free tier: 30 RPM, 15000 TPM — sufficient for failover burst

**Key config**:
```python
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
response = await client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    max_tokens=max_tokens,
    temperature=temperature,
)
return response.choices[0].message.content
```

---

### R6: OpenAI SDK Integration

**Context**: OpenAI is the third (last resort) failover provider.

**Decision**: Use official `openai` Python SDK with `AsyncOpenAI` client.

**Rationale**:
- Official SDK handles auth and response parsing
- Compatible model: `gpt-4o-mini` — cost-effective for educational content, fast responses
- OpenAI free tier / pay-as-you-go: rates vary but serve as last resort

**Key config**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    max_tokens=max_tokens,
    temperature=temperature,
)
return response.choices[0].message.content
```

---

### R7: Qdrant Multi-Module Indexing

**Context**: `index_content.py` currently infers only module1 and intro. All 4 modules must be indexed.

**Decision**: Update `_infer_module()` to handle all modules; add `chapter_slug` to Qdrant payload.

**Rationale**:
- The existing indexing pipeline is sound — chunks by H2/H3, embeds with `gemini-embedding-001`, upserts to Qdrant
- Only the module inference function needs updating
- Adding `chapter_slug` to payload enables cache key matching between Qdrant results and DB cache

**Changes needed**:
1. `_infer_module()` — add module2, module3, module4 patterns
2. Add `chapter_slug` computation: `os.path.relpath(filepath, DOCS_DIR).replace('.md', '').replace('/index', '')`
3. Increase `MAX_TOKENS` from 400 to 500 (spec guidance: 500-1000 tokens per chunk)

---

### R8: Frontend Chat History UI

**Context**: Chat history must be visible on return visits (FR-011).

**Decision**: Extend existing `ChatWidget.tsx` to load and display previous messages on mount.

**Rationale**:
- Minimal UI change: on mount, if authenticated, fetch `GET /api/chat/history`
- Display previous messages in the chat window (scrollable)
- New messages are appended and saved via existing `POST /api/chat` flow
- Backend saves chat history atomically with answer generation

**Alternatives considered**:
1. **Separate history page** — Rejected: breaks the chatbot omnipresence principle (Principle IV). History should be in the chat widget itself
2. **Infinite scroll** — Deferred: at 50-message limit per page load, sufficient for hackathon demo

---

## Summary of Decisions

| # | Topic | Decision | Key Tradeoff |
|---|-------|----------|-------------|
| R1 | Failover pattern | Chain-of-responsibility | Simplicity over resilience; no circuit breaker |
| R2 | Retry strategy | Exponential backoff with jitter, capped at 60s | Aggressive base (7) but capped; prioritizes UX |
| R3 | AI content cache | Single DB table with type discriminator | DB latency (~5ms) vs. Redis speed; acceptable at scale |
| R4 | Chat history | Append-only DB table, no threading | No multi-turn context; can be added later |
| R5 | Groq model | llama-3.3-70b-versatile | Quality vs. speed; 70B model is high quality |
| R6 | OpenAI model | gpt-4o-mini | Cost vs. quality; good enough for last resort |
| R7 | Indexing | Update module inference + add chapter_slug | Minimal change to working pipeline |
| R8 | Chat history UI | In-widget history display | Keeps chatbot omnipresent; no separate page |
