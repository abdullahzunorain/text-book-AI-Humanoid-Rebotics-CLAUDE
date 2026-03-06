```prompt
---
id: 028
title: Implement Feature 005 — OpenAI Agents SDK + Gemini Migration
stage: implement
date: 2025-07-24
surface: agent
model: claude-opus-4-20250514
feature: 005-openai-agents-gemini
branch: 005-openai-agents-gemini
user: abdullahzunorain
command: /speckit.implement
labels: ["openai-agents", "gemini", "migration", "implementation", "agents-sdk"]
links:
  spec: specs/005-openai-agents-gemini/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/services/agent_config.py
  - backend/tests/test_agent_config.py
  - backend/rag_service.py
  - backend/main.py
  - backend/services/personalization_service.py
  - backend/services/translation_service.py
  - backend/routes/personalize.py
  - backend/routes/translate.py
  - backend/tests/test_personalization_service.py
  - backend/tests/test_translation_service.py
  - backend/tests/test_translate_api.py
  - backend/tests/test_personalize_cache.py
  - backend/requirements.txt
  - backend/.env.example
  - specs/005-openai-agents-gemini/tasks.md
tests:
  - backend/tests/test_agent_config.py (9 tests — NEW)
  - backend/tests/test_personalization_service.py (mocks updated)
  - backend/tests/test_translation_service.py (mocks updated)
  - backend/tests/test_translate_api.py (error type updated)
  - backend/tests/test_personalize_cache.py (error type updated)
  - Full suite: 112 passed, 0 failed
---

## Prompt

/speckit.implement

## Response snapshot

Executed all 20 tasks from tasks.md across 7 phases to migrate from hand-rolled LLM failover client to OpenAI Agents SDK + Gemini backend.

### Key Changes
- **Created** `backend/services/agent_config.py` (~133 lines): Central agent infrastructure with shared `AsyncOpenAI` client pointing at Gemini's OpenAI-compatible endpoint, 3 Agent instances (tutor, personalizer, translator), `embed()` and `run_agent()` helpers, `set_tracing_disabled(True)`
- **Created** `backend/tests/test_agent_config.py`: 9 unit tests for agent instances, shared client, run_agent, embed
- **Migrated** `rag_service.py`: Removed google-genai imports, switched to `agent_config.embed()` (now async) and `run_agent(tutor_agent)`
- **Migrated** `personalization_service.py`: Replaced `get_llm_client().generate()` with `run_agent(personalization_agent)`
- **Migrated** `translation_service.py`: Replaced `get_llm_client().generate()` with `run_agent(translation_agent)`
- **Updated** error handling in `main.py`, `routes/personalize.py`, `routes/translate.py`: `AllProvidersExhaustedError` → `openai.APIError`/`openai.RateLimitError`
- **Updated** 4 test files: Mock targets changed from `get_llm_client` to `run_agent`, error types updated
- **Deleted** `services/llm_client.py` (406 lines) and `tests/test_llm_client.py` (15 tests)
- **Updated** `requirements.txt`: Removed groq, google-genai, openai; added openai-agents>=0.0.15
- **Updated** `.env.example`: Simplified to GOOGLE_API_KEY only

### Verification
- 112 tests pass, 0 failures
- No old `llm_client`/`AllProvidersExhaustedError`/`groq` references in production code
- `groq` and `google-genai` removed from installed packages
- Net ~300 LOC reduction

## Outcome

- ✅ Impact: Complete migration from 406-line hand-rolled LLM failover chain to OpenAI Agents SDK (3 declarative agents, ~80 lines). All 3 services (chat, personalization, translation) now use Gemini via Agents SDK.
- 🧪 Tests: 112 passed (0 failed). Lost 15 from deleted test_llm_client.py, gained 9 from new test_agent_config.py. Net: -6 tests, +100% migration coverage.
- 📁 Files: 2 created, 12 modified, 2 deleted. Net ~300 LOC reduction.
- 🔁 Next prompts: Manual smoke test with live API keys; consider adding integration tests for agent responses; update README if needed.
- 🧠 Reflection: Migration was clean because all 3 services had identical patterns (get_llm_client → generate). openai.APIError constructor requires `request` param (not `response`) — caught by test run.

## Evaluation notes (flywheel)

- Failure modes observed: openai.APIError(response=None) is invalid — correct signature requires request=httpx.Request(...). Terminal grep commands with spaces in path get interrupted (code 130).
- Graders run and results (PASS/FAIL): pytest full suite PASS (112/112). grep verification PASS (zero production references to old code).
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add live integration test that calls Gemini via agent to verify end-to-end flow with real API key.

```
