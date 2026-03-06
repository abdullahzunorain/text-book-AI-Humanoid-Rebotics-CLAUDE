# Implementation Plan: Physical AI & Humanoid Robotics Textbook Platform

**Branch**: `004-physical-ai-textbook` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/004-physical-ai-textbook/spec.md`

---

## Summary

Extend the existing Physical AI textbook platform to achieve full production readiness. The codebase already has a working Docusaurus frontend, FastAPI backend with auth, RAG chatbot (Gemini + Qdrant), personalization (Gemini), and Urdu translation (Gemini). This plan fills the remaining gaps:

1. **Multi-model LLM failover** (Gemini → Groq → OpenAI) with exponential backoff retry
2. **DB-cached AI responses** for personalization and translation, with invalidation on profile update
3. **Persistent chat history** stored in Neon DB per user, surviving sign-out
4. **Content indexing** for all 4 modules (not just module 1)
5. **Frontend chat history UI** — display previous conversations on return visits

---

## 1. High-Level System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Pages (Static)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Docusaurus 3.9.2 + React 19                    │   │
│  │  ┌─────────────┐  ┌───────────────┐  ┌───────────────┐  │   │
│  │  │ Chapter View │  │  ChatWidget   │  │  AuthButton   │  │   │
│  │  │ Personalize  │  │  + History    │  │  + Modal      │  │   │
│  │  │ Translate    │  │  + Selection  │  │  + Background │  │   │
│  │  └──────┬───────┘  └──────┬────────┘  └──────┬────────┘  │   │
│  └─────────┼─────────────────┼──────────────────┼────────────┘   │
│            │                 │                  │                 │
└────────────┼─────────────────┼──────────────────┼─────────────────┘
             │  HTTPS + Cookies│                  │
             ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Railway (FastAPI Backend)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     FastAPI App (main.py)                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ /api/auth│  │/api/chat │  │/api/pers.│  │/api/trans│ │  │
│  │  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘ │  │
│  │        │              │             │             │       │  │
│  │  ┌─────┴──────────────┴─────────────┴─────────────┴────┐  │  │
│  │  │              LLM Client (failover layer)             │  │  │
│  │  │  Gemini 2.5 Flash → Groq → OpenAI                   │  │  │
│  │  │  Exponential backoff: 5 attempts, base 7, 1s init    │  │  │
│  │  └─────────────────────┬────────────────────────────────┘  │  │
│  │                        │                                   │  │
│  │  ┌────────────┐  ┌────┴───────┐  ┌──────────────────┐    │  │
│  │  │ DB Cache   │  │ RAG Service│  │ Auth Utils       │    │  │
│  │  │ Service    │  │ (embed +   │  │ (JWT + bcrypt)   │    │  │
│  │  │ (per-user) │  │  retrieve) │  │                  │    │  │
│  │  └──────┬─────┘  └──────┬─────┘  └──────────────────┘    │  │
│  └─────────┼───────────────┼──────────────────────────────────┘  │
│            │               │                                     │
└────────────┼───────────────┼──────────────────────────────────────┘
             │               │
     ┌───────┴───────┐  ┌───┴────────────┐
     │  Neon DB      │  │  Qdrant Cloud  │
     │  (PostgreSQL) │  │  (Vector DB)   │
     │               │  │                │
     │  - users      │  │  book_content  │
     │  - backgrounds│  │  collection    │
     │  - cache      │  │  (cosine,3072) │
     │  - chat_msgs  │  │                │
     └───────────────┘  └────────────────┘
```

### Request Flow — RAG Chatbot

```
User types question
        │
        ▼
  ChatWidget.tsx ──POST /api/chat──▶ main.py chat()
        │                                │
        │                                ▼
        │                     rag_service.generate_answer()
        │                                │
        │                    ┌───────────┴───────────┐
        │                    │                       │
        │                    ▼                       ▼
        │             embed(question)          Build user_message
        │             via gemini-embedding-001  (+ selected_text)
        │                    │
        │                    ▼
        │             retrieve() from Qdrant
        │             (top 5, score > 0.4)
        │                    │
        │                    ▼
        │             LLM Client.generate()
        │             ┌─────────────────────┐
        │             │ Try Gemini 2.5 Flash│
        │             │   ↓ (429/503?)      │
        │             │ Try Groq            │
        │             │   ↓ (429/503?)      │
        │             │ Try OpenAI          │
        │             └─────────┬───────────┘
        │                       │
        │                       ▼
        │              Save to chat_messages
        │              (user_id, Q, A, sources)
        │                       │
        ◀──────────────────────┘
  Display answer + sources
```

### Multi-Model Failover Flowchart

```
                    ┌──────────────────┐
                    │ LLM Request      │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Select provider   │
                    │ (first available) │
                    └────────┬─────────┘
                             │
              ┌──────────────▼──────────────┐
              │ Provider rate-limited?       │
              │ (check RPM/TPM/RPD tracker) │
              └──┬──────────────────────┬───┘
                 │ YES                  │ NO
                 ▼                      ▼
          Skip to next           ┌─────────────┐
          provider               │ Call provider│
                                 └──────┬──────┘
                                        │
                              ┌─────────▼─────────┐
                              │ HTTP 429/500/503/  │
                              │ 504 error?         │
                              └──┬─────────────┬───┘
                                 │ YES         │ NO
                                 ▼             ▼
                          ┌─────────────┐  Return response ✓
                          │ Retry with  │
                          │ exp backoff │
                          │ attempt++   │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │ attempt > 5?│
                          └──┬──────┬───┘
                             │ YES  │ NO
                             ▼      └─── Retry same provider
                      Mark provider
                      as limited
                             │
                      ┌──────▼──────┐
                      │ More provs? │
                      └──┬──────┬───┘
                         │ YES  │ NO
                         ▼      ▼
                  Try next    Raise
                  provider    AllProvidersExhaustedError
```

### Cache Decision Flowchart (Personalization/Translation)

```
  Reader clicks "Personalize" or "Translate"
                    │
                    ▼
         ┌──────────────────────┐
         │ Query content_cache  │
         │ WHERE user_id = X    │
         │ AND chapter_slug = Y │
         │ AND cache_type = Z   │
         └────────┬─────────────┘
                  │
         ┌────────▼─────────┐
         │ Cache hit?        │
         └──┬────────────┬───┘
            │ YES        │ NO
            ▼            ▼
     Return cached    Call LLM Client
     content          (with failover)
                         │
                         ▼
                  Store in content_cache
                  (UPSERT)
                         │
                         ▼
                  Return fresh content
```

---

## 2. Backend Blueprint

### API Endpoints (Complete)

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| GET | `/` | No | API info | ✅ Exists |
| GET | `/health` | No | Health check | ✅ Exists |
| POST | `/api/auth/signup` | No | Create account | ✅ Exists |
| POST | `/api/auth/signin` | No | Login | ✅ Exists |
| POST | `/api/auth/signout` | Yes | Logout | ✅ Exists |
| GET | `/api/auth/me` | Yes | Current user | ✅ Exists |
| POST | `/api/user/background` | Yes | Save background | ✅ Exists |
| POST | `/api/chat` | No | RAG chatbot | ✅ Exists (needs failover + history) |
| POST | `/api/translate` | No* | Translate chapter | ✅ Exists (needs failover + cache) |
| POST | `/api/personalize` | Yes | Personalize chapter | ✅ Exists (needs failover + cache) |
| GET | `/api/chat/history` | Yes | Get chat history | ❌ **NEW** |

*Translation has IP-based rate limiting but no auth requirement currently. Per spec FR-022, translation requires auth.*

### New/Modified Backend Modules

#### `backend/services/llm_client.py` — **NEW**

Central LLM abstraction with multi-model failover and exponential backoff.

**Responsibilities:**
- Maintain a provider registry: `[GeminiProvider, GroqProvider, OpenAIProvider]`
- Track per-provider rate-limit state (RPM counter, TPM counter, RPD counter, cooldown timestamps)
- Execute retry with exponential backoff: `delay = initial * (base ^ attempt)` → 1s, 7s, 49s, 343s, 2401s
- Cap max delay at 60s for practical purposes
- Log failover events for observability

**Key class: `LLMClient`**
```python
class LLMClient:
    async def generate(self, prompt: str, system: str = "", 
                       max_tokens: int = 1024, temperature: float = 0.3) -> str:
        """Try each provider in order; retry transient errors with backoff."""
        ...

class LLMProvider(Protocol):
    name: str
    def is_available(self) -> bool: ...
    async def generate(self, prompt: str, system: str, 
                       max_tokens: int, temperature: float) -> str: ...
    def mark_rate_limited(self, limit_type: str, retry_after: int) -> None: ...
```

**Edge Case Handling:**
- All providers exhausted → raise `AllProvidersExhaustedError` → routes return original content with banner
- RPD (daily limit) → mark provider unavailable for 24h
- RPM (per-minute) → mark provider unavailable for 60s
- Network timeout → treat as transient, retry with backoff

#### `backend/services/cache_service.py` — **NEW**

DB-backed cache for AI-generated content.

**Responsibilities:**
- `get_cached(user_id, chapter_slug, cache_type) -> str | None`
- `set_cached(user_id, chapter_slug, cache_type, content) -> None`
- `invalidate_personalization(user_id) -> None` — called when background profile updates

#### `backend/services/chat_history_service.py` — **NEW**

Persistent chat storage.

**Responsibilities:**
- `save_message(user_id, question, answer, selected_text, sources) -> int`
- `get_history(user_id, limit=50, offset=0) -> list[ChatMessage]`

#### Modified: `backend/rag_service.py`

- Replace direct `_genai_client.models.generate_content()` with `LLMClient.generate()`
- After generating answer, call `chat_history_service.save_message()` if user is authenticated
- Accept optional `user_id` parameter to enable history saving

#### Modified: `backend/services/personalization_service.py`

- Replace `_call_gemini_personalize()` with `LLMClient.generate()`
- Check `cache_service.get_cached()` before calling LLM
- Store result via `cache_service.set_cached()` after LLM call
- On profile update: call `cache_service.invalidate_personalization(user_id)`

#### Modified: `backend/services/translation_service.py`

- Replace `_call_gemini_translate()` with `LLMClient.generate()`
- Check `cache_service.get_cached()` before calling LLM
- Store result via `cache_service.set_cached()` after LLM call
- Translation cache is never invalidated (per spec clarification)

#### Modified: `backend/routes/auth.py`

- In `POST /api/user/background`: after saving profile, call `cache_service.invalidate_personalization(user_id)` (FR-035)

#### Modified: `backend/routes/translate.py`

- Add auth requirement (JWT cookie check) per FR-022
- Integrate cache service

#### New: `backend/routes/chat.py`

- `GET /api/chat/history` — returns paginated chat history for authenticated user
- `POST /api/chat` moved here (optional refactor) or history saving added to existing endpoint

### New Database Migration: `002_add_cache_and_chat.sql`

```sql
-- content_cache: stores personalized/translated chapter content per user
CREATE TABLE content_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_slug VARCHAR(200) NOT NULL,
    cache_type VARCHAR(20) NOT NULL CHECK (cache_type IN ('personalization', 'translation')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, chapter_slug, cache_type)
);

-- chat_messages: persistent chat history per user
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    selected_text TEXT,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_content_cache_lookup ON content_cache(user_id, chapter_slug, cache_type);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id, created_at DESC);
```

### New Dependencies

| Package | Purpose | Provider |
|---------|---------|----------|
| `groq` | Groq LLM API client | Failover provider #2 |
| `openai` | OpenAI API client | Failover provider #3 |

Add to `requirements.txt`:
```
groq>=0.15.0
openai>=1.60.0
```

### New Environment Variables

```env
# Existing
GOOGLE_API_KEY=...
GEMINI_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
DATABASE_URL=...
JWT_SECRET=...

# NEW for failover
GROQ_API_KEY=...
OPENAI_API_KEY=...

# NEW for LLM config (optional, with defaults)
LLM_MAX_RETRIES=5           # default: 5
LLM_BACKOFF_BASE=7          # default: 7
LLM_BACKOFF_INITIAL=1       # default: 1 (seconds)
LLM_BACKOFF_MAX=60          # default: 60 (seconds)
```

---

## 3. RAG Pipeline Design

### Content Indexing (`index_content.py`)

**Current state:** Indexes all `.md` files under `website/docs/` recursively by H2/H3 headings. Uses `gemini-embedding-001` (3072 dimensions). Chunks limited to 400 tokens.

**Needed changes:**
1. Update `_infer_module()` to handle all 4 modules + intro:
   ```python
   def _infer_module(filepath: str) -> str:
       if "module1" in filepath: return "module1-ros2"
       if "module2" in filepath: return "module2-simulation"
       if "module3" in filepath: return "module3-isaac"
       if "module4" in filepath: return "module4-vla"
       if "intro" in filepath: return "introduction"
       return "unknown"
   ```
2. Increase `MAX_TOKENS` to 500 for richer context per chunk (spec says 500-1000)
3. Add chapter_slug to payload for cache key matching

**Indexing flow:**
```
website/docs/**/*.md
        │
        ▼
  chunk_markdown()
  Split by H2/H3 headings
  Max 500 tokens per chunk
        │
        ▼
  embed_text() via gemini-embedding-001
  → 3072-dimensional vector
        │
        ▼
  Upsert to Qdrant "book_content"
  Payload: {text, chapter, module, page_title, heading, chapter_slug}
```

### Retrieval Flow (`rag_service.py`)

**Current state:** Embeds question → retrieves top 5 from Qdrant (score ≥ 0.4) → builds context → calls Gemini with system prompt.

**Selected-text mode:** When `selected_text` is provided, prepend it to the user message for scoped answers.

**No changes to retrieval logic needed** — the existing flow is sound. Only the LLM call needs to go through `LLMClient` for failover.

### Multilingual Considerations

Embeddings are English-only (`gemini-embedding-001` supports multilingual but content is authored in English). For Urdu translation questions, the chatbot will:
1. Accept questions in English (primary)
2. Retrieve English chunks from Qdrant
3. Generate answers in English
4. Translation is a separate endpoint, not part of RAG

---

## 4. Caching & Chat Persistence

### Content Cache Strategy

| Aspect | Personalization | Translation |
|--------|----------------|-------------|
| Cache key | `(user_id, chapter_slug, 'personalization')` | `(user_id, chapter_slug, 'translation')` |
| Invalidation | On background profile update (FR-035) | Never |
| Storage | `content_cache` table in Neon DB | `content_cache` table in Neon DB |
| TTL | None (invalidated by profile change) | None (permanent) |
| Warm-up | On first request per user+chapter | On first request per user+chapter |

### Cache Invalidation Flow

```
User updates background profile
(POST /api/user/background)
         │
         ▼
  Save new profile to user_backgrounds
  (UPSERT)
         │
         ▼
  DELETE FROM content_cache
  WHERE user_id = X
  AND cache_type = 'personalization'
         │
         ▼
  Return success
  (Next personalize request will generate fresh content)
```

### Chat History Persistence

- **Storage:** `chat_messages` table, keyed by `user_id`
- **Retention:** Indefinite (no expiry at hackathon scale)
- **Scope:** Per-user, includes question, answer, selected_text (nullable), sources (JSONB)
- **Access:** `GET /api/chat/history?limit=50&offset=0` returns newest-first
- **Auth:** Required (JWT cookie)
- **On signout:** History persists in DB; visible again on next signin

### Session Management

- **JWT cookies:** httpOnly, 7-day expiry, env-aware Secure/SameSite via `cookie_config.py`
- **Cookie attributes:** Dev: `Secure=false, SameSite=lax` | Prod: `Secure=true, SameSite=none`
- **Session expiry:** 401 with `detail="session_expired"` → frontend prompts re-signin

---

## 5. Deployment & Infrastructure

### Deployment Architecture

```
┌──────────────────────┐      ┌──────────────────────┐
│   GitHub Repository   │      │   GitHub Actions CI   │
│ (source of truth)     │──────│                       │
│                       │      │  - lint (ruff)        │
│  website/ (Docusaurus)│      │  - test (pytest)      │
│  backend/ (FastAPI)   │      │  - build (Docusaurus) │
│  website/docs/ (content)     │  - deploy (Pages)     │
└───────────┬──────────┘      └───────────────────────┘
            │
    ┌───────┴────────────────────┐
    │                            │
    ▼                            ▼
┌────────────────┐     ┌────────────────────┐
│ GitHub Pages   │     │ Railway            │
│ (Static Site)  │     │ (FastAPI Backend)  │
│                │     │                    │
│ Docusaurus     │────▶│ uvicorn main:app   │
│ HTML/JS/CSS    │     │ Single instance    │
│                │     │ Auto-deploy on push│
└────────────────┘     └────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
           ┌──────────────┐       ┌──────────────┐
           │ Neon DB      │       │ Qdrant Cloud │
           │ (Serverless) │       │ (Free Tier)  │
           │              │       │              │
           │ Tables:      │       │ Collection:  │
           │ - users      │       │ book_content │
           │ - backgrounds│       │ 3072 dims    │
           │ - cache      │       │ cosine       │
           │ - chat_msgs  │       │              │
           └──────────────┘       └──────────────┘
```

### Environment Configuration

| Service | Plan | Scaling | Notes |
|---------|------|---------|-------|
| GitHub Pages | Free | Static CDN | Docusaurus build output |
| Railway | Free/Hobby | Single instance | Auto-sleep on inactivity |
| Neon DB | Free tier | Serverless | Auto-suspend after 5min idle |
| Qdrant Cloud | Free tier | 1GB storage | Sufficient for 17 chapters |

### Monitoring & Observability

- **Backend logging:** Python `logging` module, structured JSON in production
- **LLM failover logging:** Log every provider switch with timestamps and error codes
- **Health endpoint:** `GET /health` returns `{"status": "ok"}`
- **Error tracking:** HTTP error responses include descriptive detail messages
- **Rate limit visibility:** Log RPM/TPM/RPD counters per provider

---

## 6. Validation & Testing

### Test Strategy

| Layer | Tool | Coverage Target |
|-------|------|----------------|
| Unit | pytest | LLM client, cache service, chat history, auth utils |
| Contract | pytest + httpx | All API endpoints — schema, status codes, error paths |
| Integration | pytest | DB operations (cache CRUD, chat CRUD, auth flow) |
| E2E (manual) | curl / browser | Full user journeys: browse → chat → signup → personalize → translate |

### Test Matrix vs Requirements

| Requirement | Test Type | Test Description |
|-------------|-----------|------------------|
| FR-006 (chatbot on every page) | E2E | ChatWidget renders on 3+ chapter pages |
| FR-007 (RAG answers) | Contract | POST /api/chat returns answer + sources |
| FR-009 (selected text) | Contract | POST /api/chat with selected_text scopes answer |
| FR-011 (chat persistence) | Integration | Save message → GET history returns it |
| FR-030 (failover) | Unit | Mock Gemini 429 → verify Groq called |
| FR-031 (exp backoff) | Unit | Mock 503 → verify delays: 1s, 7s, 49s... |
| FR-032 (rate tracking) | Unit | Mark Gemini limited → next call skips Gemini |
| FR-033 (personalization cache) | Integration | Personalize → cache hit on retry |
| FR-034 (translation cache) | Integration | Translate → cache hit on retry |
| FR-035 (cache invalidation) | Integration | Update background → personalization cache cleared |
| SC-002 (chatbot <10s) | Contract | Assert /api/chat response time < 10s |
| SC-004 (personalize <15s) | Contract | Assert /api/personalize response time < 15s |
| SC-005 (translate <15s) | Contract | Assert /api/translate response time < 15s |

### Success Criteria Verification

- [ ] SC-001: All 4 modules accessible — verify with sidebar navigation test
- [ ] SC-002: RAG chatbot <10s p90 — measure with pytest timing
- [ ] SC-003: Signup → questionnaire <2min — manual E2E test
- [ ] SC-004: Personalize <15s — contract test with timing
- [ ] SC-005: Translate <15s — contract test with timing
- [ ] SC-006: Selected-text accuracy 80% — manual test with 10 samples
- [ ] SC-007: Public URL no auth — verify with unauthenticated curl
- [ ] SC-008: Chatbot discoverability — usability observation
- [ ] SC-009: Full journey 90% success — manual E2E test ×10
- [ ] SC-010: 10-20 concurrent users — load test with concurrent curl

---

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript/React 19 (frontend)
**Primary Dependencies**: FastAPI, asyncpg, google-genai, qdrant-client, python-jose, bcrypt, groq, openai
**Storage**: Neon Serverless PostgreSQL (users, backgrounds, cache, chat_messages) + Qdrant Cloud (vectors)
**Testing**: pytest with httpx (backend), tsc --noEmit (frontend)
**Target Platform**: Railway (backend), GitHub Pages (frontend)
**Project Type**: Web service + static site (Docusaurus)
**Performance Goals**: Chatbot <10s p90, Personalization <15s, Translation <15s
**Constraints**: Single Railway instance, free-tier Neon/Qdrant, 3 LLM provider API keys required
**Scale/Scope**: 10-20 concurrent users (hackathon demo), 4 modules, 17+ chapters

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Evaluation

| # | Constitution Principle | Status | Notes |
|---|----------------------|--------|-------|
| I | MVP-First (Minimal Scope) | ✅ PASS | Plan targets only unfilled gaps; no speculative features |
| II | No Auth, No Personalization, No Translation | ⚠️ VIOLATION (JUSTIFIED) | Auth, personalization, and translation already exist in codebase. The constitution reflects initial MVP scope; the project has evolved to post-MVP. See Complexity Tracking below. |
| III | Content Scope (Intro + Module 1 Only) | ⚠️ VIOLATION (JUSTIFIED) | All 4 modules already exist in `website/docs/`. The spec (FR-001) requires all 4 modules. See Complexity Tracking below. |
| IV | Chatbot Omnipresence | ✅ PASS | ChatWidget already renders on every page; this plan adds history + failover |
| V | Deployability & Demability | ✅ PASS | All changes are deployable; no incomplete subsystems |
| VI | No Over-Engineering | ✅ PASS | LLM failover uses 3 providers (< 3 new services). DB cache uses existing Neon. No custom frameworks |

### Post-Phase 1 Re-Evaluation

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | MVP-First | ✅ PASS | Data model adds 2 tables; no unnecessary abstractions |
| II | No Auth/Pers/Trans | ⚠️ MAINTAINED VIOLATION | Justified — these features are the spec's core deliverables |
| III | Content Scope | ⚠️ MAINTAINED VIOLATION | Justified — all 4 modules already authored and deployed |
| IV | Chatbot Omnipresence | ✅ PASS | Chat history enhances omnipresence |
| V | Deployability | ✅ PASS | Migration is additive; no breaking changes |
| VI | No Over-Engineering | ✅ PASS | LLMClient is a thin wrapper, not a framework |

**GATE DECISION**: PASS with justified violations. Recommend amending constitution to v2.0.0 to reflect post-MVP phase.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-physical-ai-textbook/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-contracts.md # REST API contracts
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py                          # FastAPI app, CORS, routers
├── db.py                            # asyncpg pool management
├── auth_utils.py                    # JWT + bcrypt utilities
├── cookie_config.py                 # Env-aware cookie attributes
├── rag_service.py                   # RAG pipeline: embed → retrieve → generate
├── index_content.py                 # Qdrant indexing script
├── requirements.txt                 # Python dependencies
├── Procfile                         # Railway deployment
├── migrations/
│   ├── 001_create_auth_tables.sql   # users + user_backgrounds
│   └── 002_add_cache_and_chat.sql   # content_cache + chat_messages (NEW)
├── routes/
│   ├── auth.py                      # signup/signin/signout/me/background
│   ├── personalize.py               # POST /api/personalize
│   ├── translate.py                 # POST /api/translate
│   └── chat.py                      # GET /api/chat/history (NEW)
├── services/
│   ├── llm_client.py                # Multi-model failover (NEW)
│   ├── cache_service.py             # DB cache for AI content (NEW)
│   ├── chat_history_service.py      # Chat persistence (NEW)
│   ├── personalization_service.py   # Chapter personalization
│   └── translation_service.py       # Urdu translation
└── tests/
    ├── test_auth.py
    ├── test_chat.py
    ├── test_translate.py
    ├── test_personalize.py
    ├── test_llm_client.py           # (NEW) failover + backoff tests
    ├── test_cache_service.py        # (NEW) cache CRUD + invalidation
    └── test_chat_history.py         # (NEW) history persistence

website/
├── docusaurus.config.ts             # Site config, custom fields
├── sidebars.ts                      # Sidebar navigation
├── src/
│   ├── components/
│   │   ├── AuthButton.tsx           # Auth UI + questionnaire trigger
│   │   ├── AuthModal.tsx            # Signin/signup modal
│   │   ├── AuthProvider.tsx         # Auth context provider
│   │   ├── BackgroundQuestionnaire.tsx
│   │   ├── PersonalizedContent.tsx  # Personalized markdown renderer
│   │   └── ChatWidget.tsx           # Chatbot (needs history UI) (MODIFY)
│   └── css/
│       └── custom.css
└── docs/
    ├── intro/                       # Introduction module
    ├── module1-ros2/                # Module 1: ROS 2 (5 chapters)
    ├── module2-simulation/          # Module 2: Simulation
    ├── module3-isaac/               # Module 3: NVIDIA Isaac
    └── module4-vla/                 # Module 4: VLA Models
```

**Structure Decision**: Web application pattern (Option 2). Backend and frontend are separate directories at repo root. Frontend is a Docusaurus static site; backend is a FastAPI service. This structure already exists and is maintained.

---

## Complexity Tracking

> Constitution Principles II and III are violated. Justification below.

### Violation: Principle II — "No Auth, No Personalization, No Translation"

**What changed**: The project has evolved past the initial MVP scope. Auth (`routes/auth.py`, `cookie_config.py`), personalization (`services/personalization_service.py`), and translation (`services/translation_service.py`) were implemented in prior features and are now production code with 68 passing tests.

**Why this is necessary**: Feature 004's spec (the authoritative document) explicitly requires auth (FR-011–FR-017), personalization (FR-018–FR-021), and translation (FR-022–FR-025). These are core deliverables for the hackathon evaluation.

**Tradeoff accepted**: Increased backend complexity and state management. Mitigated by using existing Neon DB and keeping the LLM failover layer thin.

**Recommendation**: Amend constitution to v2.0.0 — remove Principle II restrictions, update scope to reflect full feature set.

### Violation: Principle III — "Content Scope (Introduction + Module 1 Only)"

**What changed**: All 4 modules with content already exist in `website/docs/` (intro, module1-ros2, module2-simulation, module3-isaac, module4-vla).

**Why this is necessary**: FR-001 requires "at least 4 modules and 17 chapters." SC-001 measures success by all 4 modules being accessible.

**Tradeoff accepted**: More content to index in Qdrant (more vectors, more embedding API calls). Mitigated by batch indexing with rate-limiting delays (already implemented in `index_content.py`).

**Recommendation**: Amend constitution Principle III to "4 modules minimum."

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
