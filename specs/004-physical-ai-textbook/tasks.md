# Tasks: Physical AI & Humanoid Robotics Textbook Platform

**Input**: Design documents from `specs/004-physical-ai-textbook/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-contracts.md, quickstart.md

**Tests**: Included — the existing codebase has 68 passing tests and test-driven development is expected.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (US1–US6)
- Exact file paths included in every task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies, DB migration, and foundational services that all user stories depend on.

- [x] T001 Add `groq>=0.15.0` and `openai>=1.60.0` to `backend/requirements.txt` and install
- [x] T002 [P] Add `GROQ_API_KEY`, `OPENAI_API_KEY`, and LLM config vars to `backend/.env.example`
- [x] T003 Create database migration `backend/migrations/002_add_cache_and_chat.sql` with `content_cache` and `chat_messages` tables per data-model.md
- [x] T004 Run migration `002_add_cache_and_chat.sql` against local/dev Neon DB

**Checkpoint**: Dependencies installed, new DB tables created. Ready for foundational services.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services that MUST be complete before ANY user story work can begin.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### LLM Client (FR-030, FR-031, FR-032)

- [x] T005 Create `LLMProvider` protocol and `GeminiProvider` class in `backend/services/llm_client.py` — wraps `google.genai` async API (`client.aio.models.generate_content`), catches `RESOURCE_EXHAUSTED` / HTTP 429 as transient errors
- [x] T006 [P] Create `GroqProvider` class in `backend/services/llm_client.py` — wraps `groq.AsyncGroq`, model `llama-3.3-70b-versatile`, catches `groq.RateLimitError`
- [x] T007 [P] Create `OpenAIProvider` class in `backend/services/llm_client.py` — wraps `openai.AsyncOpenAI`, model `gpt-4o-mini`, catches `openai.RateLimitError`
- [x] T008 Implement `LLMClient` class in `backend/services/llm_client.py` — chain-of-responsibility failover with per-provider rate-limit tracking (RPM/TPM/RPD cooldowns), exponential backoff retry (5 attempts, base 7, 1s initial, capped 60s, ±20% jitter), and `AllProvidersExhaustedError`
- [x] T009 Write unit tests for `LLMClient` in `backend/tests/test_llm_client.py` — test: Gemini success, Gemini 429 → Groq called, Groq 429 → OpenAI called, all exhausted → error, backoff delays verified, rate-limit cooldown tracking, jitter within bounds

### Cache Service (FR-033, FR-034, FR-035)

- [x] T010 [P] Create `backend/services/cache_service.py` with `get_cached(user_id, chapter_slug, cache_type) -> str | None`, `set_cached(user_id, chapter_slug, cache_type, content, metadata) -> None`, and `invalidate_personalization(user_id) -> None` — uses asyncpg pool from `db.py`, UPSERT on `content_cache`
- [x] T011 [P] Write tests for cache service in `backend/tests/test_cache_service.py` — test: cache miss returns None, set+get returns content, UPSERT overwrites, invalidate deletes only personalization rows, translation rows survive invalidation

### Chat History Service (FR-011 chat persistence)

- [x] T012 [P] Create `backend/services/chat_history_service.py` with `save_message(user_id, question, answer, selected_text, sources) -> int` and `get_history(user_id, limit, offset) -> list[dict]` — uses asyncpg pool, ordered by `created_at DESC`
- [x] T013 [P] Write tests for chat history service in `backend/tests/test_chat_history.py` — test: save + retrieve returns message, ordering is newest-first, pagination with limit/offset, selected_text nullable, sources stored as JSONB

**Checkpoint**: Foundation ready — `LLMClient`, `cache_service`, and `chat_history_service` all passing tests. User story implementation can begin.

---

## Phase 3: User Story 1 — Reader Browses the Textbook (Priority: P1) 🎯 MVP

**Goal**: All 4 modules and 17+ chapters accessible with sidebar navigation, rich content rendering, and next/prev links.

**Independent Test**: Visit deployed site → sidebar shows all modules → click any chapter → content renders correctly with code blocks and images.

**Note**: Textbook content and Docusaurus config already exist. This phase verifies completeness and fixes gaps.

### Implementation for User Story 1

- [x] T014 [US1] Verify all chapters in `website/docs/` have valid frontmatter (`title`, `sidebar_position`) — fix any missing metadata in `website/docs/intro/`, `website/docs/module1-ros2/`, `website/docs/module2-simulation/`, `website/docs/module3-isaac/`, `website/docs/module4-vla/`
- [x] T015 [US1] Verify `website/sidebars.ts` includes all 4 modules and their chapters in correct order — add any missing entries
- [x] T016 [P] [US1] Verify `website/docusaurus.config.ts` footer links point to correct chapter paths for all 4 modules
- [x] T017 [US1] Update `_infer_module()` in `backend/index_content.py` to handle `module2`, `module3`, `module4` patterns and add `chapter_slug` to Qdrant payload. Increase `MAX_TOKENS` from 400 to 500
- [x] T018 [US1] Run `python backend/index_content.py` to re-index all 4 modules into Qdrant `book_content` collection
- [x] T019 [US1] Verify `npm run build` succeeds in `website/` with no broken links or missing pages

**Checkpoint**: Textbook fully browsable — all 4 modules, 17+ chapters, sidebar navigation, next/prev links. SC-001 verifiable.

---

## Phase 4: User Story 2 — Reader Asks the RAG Chatbot a Question (Priority: P1) 🎯 MVP

**Goal**: RAG chatbot answers questions using textbook content with multi-model failover, selected-text mode, and persistent chat history.

**Independent Test**: Open any chapter → click chatbot → type "What is ROS 2?" → receive textbook-sourced answer. Sign in → ask questions → sign out → sign back in → see history.

### Implementation for User Story 2

- [x] T020 [US2] Refactor `backend/rag_service.py` — replace direct `_genai_client.models.generate_content()` with `LLMClient.generate()` import from `services/llm_client.py`. Keep embedding via `gemini-embedding-001` unchanged
- [x] T021 [US2] Add optional `user_id: int | None = None` parameter to `generate_answer()` in `backend/rag_service.py` — when provided, call `chat_history_service.save_message()` after generating answer
- [x] T022 [US2] Update `POST /api/chat` in `backend/main.py` — extract optional `user_id` from JWT cookie (non-failing: unauthenticated users get None), pass to `generate_answer()`
- [x] T023 [US2] Create `backend/routes/chat.py` with `GET /api/chat/history` endpoint — auth required, accepts `limit` (default 50, max 100) and `offset` (default 0) query params, returns `{messages: [...], total, limit, offset}` per api-contracts.md
- [x] T024 [US2] Register chat router in `backend/main.py` — `app.include_router(chat_router)`
- [x] T025 [US2] Update root endpoint in `backend/main.py` to include `chat_history: "GET /api/chat/history"` in endpoints dict
- [x] T026 [US2] Write contract tests for `GET /api/chat/history` in `backend/tests/test_chat.py` — test: 401 without auth, 200 with valid token returns messages array, pagination works, empty history returns `[]`
- [x] T027 [US2] Write contract test for `POST /api/chat` history saving in `backend/tests/test_chat.py` — test: authenticated request saves to DB, unauthenticated request does not save
- [x] T028 [US2] Update `ChatWidget.tsx` in `website/src/components/ChatWidget.tsx` — on mount, if user is authenticated, fetch `GET /api/chat/history` and display previous messages in chat window
- [x] T029 [US2] Add empty-question validation UX in `ChatWidget.tsx` — show validation message when submitting blank

**Checkpoint**: Chatbot fully working — RAG answers via failover, selected-text Q&A, chat history persisted and displayed. SC-002, SC-006 verifiable.

---

## Phase 5: User Story 3 — Reader Signs Up and Provides Background (Priority: P2)

**Goal**: Signup/signin via email+password, background questionnaire trigger, profile persistence.

**Independent Test**: Click "Sign In" → switch to "Sign Up" → enter email/password → submit → see questionnaire → fill + submit.

**Note**: Auth system already fully built (68 tests passing). This phase adds cache invalidation on profile update.

### Implementation for User Story 3

- [x] T030 [US3] Modify `POST /api/user/background` in `backend/routes/auth.py` — after saving background, call `cache_service.invalidate_personalization(user_id)` to delete stale personalization cache (FR-035)
- [x] T031 [US3] Write integration test in `backend/tests/test_auth.py` — test: save background → verify `content_cache` personalization rows deleted for that user, translation rows untouched
- [x] T032 [US3] Verify existing auth tests still pass after cache invalidation integration — run `pytest tests/test_auth.py -v`

**Checkpoint**: Auth + background flow complete with cache invalidation on profile update. SC-003 verifiable.

---

## Phase 6: User Story 4 — Logged-In Reader Personalizes Chapter Content (Priority: P2)

**Goal**: "Personalize" button adapts chapter content using background profile + LLM failover + DB cache.

**Independent Test**: Sign in (with profile) → open chapter → click "Personalize" → see adapted content. Click again → served from cache instantly.

### Implementation for User Story 4

- [x] T033 [US4] Modify `personalize_chapter()` in `backend/services/personalization_service.py` — check `cache_service.get_cached(user_id, slug, 'personalization')` before calling LLM; on cache miss, call `LLMClient.generate()` instead of `_call_gemini_personalize()`, then `cache_service.set_cached()`
- [x] T034 [US4] Remove or deprecate `_call_gemini_personalize()` in `backend/services/personalization_service.py` — all LLM calls go through `LLMClient`
- [x] T035 [US4] Update error handling in `POST /api/personalize` route in `backend/routes/personalize.py` — catch `AllProvidersExhaustedError` and return 503 with descriptive message
- [x] T036 [US4] Write integration test in `backend/tests/test_personalize.py` — test: first call generates + caches, second call returns cached (no LLM call), profile update clears cache, next call regenerates
- [x] T037 [US4] Write contract test for 503 on all-providers-exhausted in `backend/tests/test_personalize.py`

**Checkpoint**: Personalization works with failover + caching + invalidation. SC-004 verifiable.

---

## Phase 7: User Story 5 — Logged-In Reader Translates Chapter to Urdu (Priority: P2)

**Goal**: "Translate to Urdu" button translates chapter via LLM failover + DB cache. Auth required.

**Independent Test**: Sign in → open chapter → click "Translate to Urdu" → see Urdu RTL content. Click again → served from cache.

### Implementation for User Story 5

- [x] T038 [US5] Add JWT auth requirement to `POST /api/translate` in `backend/routes/translate.py` — extract `user_id` from cookie (reuse `_get_user_id_from_cookie` pattern from `routes/personalize.py`), per FR-022
- [x] T039 [US5] Modify `translate_to_urdu()` in `backend/services/translation_service.py` — accept `user_id` parameter, check `cache_service.get_cached(user_id, slug, 'translation')` before calling LLM; on miss, call `LLMClient.generate()` instead of `_call_gemini_translate()`, then `cache_service.set_cached()`
- [x] T040 [US5] Remove or deprecate `_call_gemini_translate()` in `backend/services/translation_service.py` — all LLM calls go through `LLMClient`
- [x] T041 [US5] Update `translate_chapter()` endpoint in `backend/routes/translate.py` — pass `user_id` to service, catch `AllProvidersExhaustedError` as 503
- [x] T042 [US5] Update existing translate tests in `backend/tests/test_translate.py` — test: 401 without auth, first call generates + caches, second call returns cached, cache NOT invalidated by profile update
- [x] T043 [US5] Write contract test for 503 on all-providers-exhausted in `backend/tests/test_translate.py`

**Checkpoint**: Translation works with auth + failover + permanent caching. SC-005 verifiable.

---

## Phase 8: User Story 6 — Reader Asks Chatbot About Selected Text (Priority: P2)

**Goal**: Highlight text on page → chatbot scopes answer to that selection.

**Independent Test**: Open chapter → select paragraph → open chatbot → ask question → answer references selected text.

**Note**: Backend `POST /api/chat` already accepts `selected_text`. This phase ensures frontend integration works end-to-end.

### Implementation for User Story 6

- [x] T044 [US6] Verify `ChatWidget.tsx` captures document selection via `window.getSelection()` and passes it as `selected_text` to `POST /api/chat` — fix or implement if missing in `website/src/components/ChatWidget.tsx`
- [x] T045 [US6] Add visual indicator in `ChatWidget.tsx` showing selected text context above the input when text is selected — clear selection button to reset
- [x] T046 [US6] Write contract test in `backend/tests/test_chat.py` — test: `POST /api/chat` with `selected_text` returns answer that mentions the selected passage, without `selected_text` returns general RAG answer

**Checkpoint**: Selected-text Q&A end-to-end. SC-006 verifiable.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Quality, documentation, and deployment readiness.

- [x] T047 [P] Update `backend/.env.example` with all new env vars documented with comments
- [x] T048 [P] Update root endpoint response in `backend/main.py` to accurately reflect all available endpoints
- [x] T049 Run full test suite — `cd backend && .venv/bin/python -m pytest tests/ -v` — all tests must pass
- [x] T050 [P] Run `cd website && npx tsc --noEmit` — verify no TypeScript errors
- [x] T051 [P] Run `cd website && npm run build` — verify Docusaurus builds with no broken links
- [x] T052 Verify quickstart.md instructions work end to end — clone, install, migrate, index, run
- [x] T053 [P] Update `backend/README.md` with new endpoints, env vars, and migration instructions

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup → no dependencies
Phase 2: Foundational → depends on Phase 1 (deps + migration)
Phase 3: US1 (Textbook) → depends on Phase 2 (needs index_content updates)
Phase 4: US2 (Chatbot) → depends on Phase 2 (needs LLMClient + chat history service)
Phase 5: US3 (Auth/Background) → depends on Phase 2 (needs cache service)
Phase 6: US4 (Personalization) → depends on Phase 2 + Phase 5 (needs cache + invalidation)
Phase 7: US5 (Translation) → depends on Phase 2 (needs cache + LLMClient)
Phase 8: US6 (Selected Text) → depends on Phase 4 (needs chatbot working)
Phase 9: Polish → depends on all prior phases
```

### User Story Dependencies

- **US1 (Textbook)**: Independent — can start after Phase 2
- **US2 (Chatbot)**: Independent — can start after Phase 2
- **US3 (Auth/Background)**: Independent — can start after Phase 2 (existing auth; only adds invalidation)
- **US4 (Personalization)**: Depends on US3 completion (needs cache invalidation wired into background endpoint)
- **US5 (Translation)**: Independent — can start after Phase 2 (translation cache never invalidated)
- **US6 (Selected Text)**: Depends on US2 completion (needs chatbot working end-to-end)

### Parallel Opportunities

After Phase 2, the following can run in parallel:

```
                     ┌──── US1 (Textbook) ──────┐
                     │                          │
Phase 2 ─── done ──├──── US2 (Chatbot) ────────├──── US6 (Selected Text)
                     │                          │
                     ├──── US3 (Auth) ──────────├──── US4 (Personalization)
                     │                          │
                     └──── US5 (Translation) ───┘
                                                │
                                          Phase 9: Polish
```

### Within Each User Story

1. Models / service changes before route changes
2. Route changes before frontend changes
3. Tests alongside or after implementation
4. Commit after each logical task group

---

## Parallel Example: Post-Phase 2

```bash
# These 4 streams can execute simultaneously after Phase 2:
Stream A: T014 → T015 → T016 → T017 → T018 → T019 (US1: Textbook)
Stream B: T020 → T021 → T022 → T023 → T024 → T025 → T026 → T027 → T028 → T029 (US2: Chatbot)
Stream C: T030 → T031 → T032 (US3: Auth cache invalidation)
Stream D: T038 → T039 → T040 → T041 → T042 → T043 (US5: Translation)
# Then, after C completes: T033 → T034 → T035 → T036 → T037 (US4: Personalization)
# Then, after B completes: T044 → T045 → T046 (US6: Selected Text)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T013)
3. Complete Phase 3: US1 — Textbook browsing (T014–T019)
4. Complete Phase 4: US2 — RAG Chatbot with failover + history (T020–T029)
5. **STOP and VALIDATE**: Browse textbook + ask questions + check history
6. Deploy if ready — this is the minimal viable demo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Textbook) → Browse all 4 modules ✓
3. US2 (Chatbot) → Ask questions, get RAG answers, see history ✓ **← MVP demo-ready**
4. US3 (Auth) → Cache invalidation on profile update ✓
5. US4 (Personalization) → Adaptive content with caching ✓
6. US5 (Translation) → Urdu translation with caching ✓
7. US6 (Selected Text) → Contextual Q&A ✓
8. Polish → Documentation, full test pass, build verification ✓

---

## Notes

- [P] tasks = different files, no dependencies on in-progress tasks
- [USn] label maps task to specific user story for traceability
- Each user story is independently testable at its checkpoint
- Commit after each task or logical group
- Existing 68 tests must continue passing throughout
- All LLM calls go through `LLMClient` — no direct Gemini/Groq/OpenAI calls in routes or services
