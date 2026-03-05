# Implementation Plan: OpenAI Agents SDK with Gemini Models

**Branch**: `005-openai-agents-gemini` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/005-openai-agents-gemini/spec.md`

## Summary

Replace the existing hand-rolled LLM failover client (`services/llm_client.py`, 406 lines, 3 providers) with the **OpenAI Agents SDK** (`openai-agents`). Three dedicated agents — Tutor, Personalization, Translation — use Gemini models via Google's OpenAI-compatible `chat.completions` endpoint. Embeddings also migrate from `google-genai` to the OpenAI compat layer. Dependencies (`groq`, `google-genai`) are removed. All API contracts remain identical.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (`openai-agents`), `openai` (transitive), `qdrant-client`  
**Storage**: Neon PostgreSQL (asyncpg), Qdrant Cloud (vectors) — both unchanged  
**Testing**: pytest 9.0.2 + pytest-asyncio (asyncio mode=strict), 119 existing tests  
**Target Platform**: Linux server (Railway deployment)  
**Project Type**: Web service (REST API backend + Docusaurus frontend)  
**Performance Goals**: Chat queries respond in <5 seconds (p95), same as current baseline  
**Constraints**: Zero frontend changes, all existing tests pass, no Google agentic SDK  
**Scale/Scope**: ~10 files modified, ~2 new files, ~2 files deleted, net reduction in LOC

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| I. MVP-First | ✅ PASS | Migration is a backend refactor — no new features, reduces complexity |
| II. No Auth/Personalization/Translation (MVP scope) | ⚠️ N/A | Constitution was written for MVP. Features 003-004 already introduced auth/personalization/translation. This feature refactors their internals. |
| III. Content Scope | ✅ PASS | No content changes |
| IV. Chatbot Omnipresence | ✅ PASS | Chatbot API contract unchanged |
| V. Deployability & Demability | ✅ PASS | Reduced dependencies, simpler architecture |
| VI. No Over-Engineering | ✅ PASS | Replaces 406-line bespoke failover with ~80-line agent config using standard SDK. Net reduction in code. |
| Tech Stack | ✅ PASS | FastAPI backend, Python, same hosting |
| No Hardcoded Secrets | ✅ PASS | `GOOGLE_API_KEY` from env, tracing disabled |

**Post-Phase-1 Re-check**: All gates still pass. Removing `google-genai` and `groq` further simplifies the stack.

## Project Structure

### Documentation (this feature)

```text
specs/005-openai-agents-gemini/
├── plan.md              # This file
├── research.md          # Phase 0 output — all research decisions
├── data-model.md        # Phase 1 output — agent entity model
├── quickstart.md        # Phase 1 output — setup & verify
├── contracts/
│   └── api-contracts.md # Phase 1 output — unchanged API contracts
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (modifications)

```text
backend/
├── services/
│   ├── agent_config.py          # NEW — Agent definitions, shared Gemini client, Runner helper
│   ├── llm_client.py            # DELETED — Old 3-provider failover chain
│   ├── personalization_service.py  # MODIFIED — Use agent instead of llm_client
│   ├── translation_service.py      # MODIFIED — Use agent instead of llm_client
│   ├── cache_service.py            # UNCHANGED
│   └── chat_history_service.py     # UNCHANGED
├── rag_service.py               # MODIFIED — Use agent for generation, OpenAI SDK for embeddings
├── main.py                      # MODIFIED — Remove AllProvidersExhaustedError, use agent errors
├── routes/
│   ├── translate.py             # MODIFIED — Update error import
│   ├── personalize.py           # MODIFIED — Update error import
│   ├── chat.py                  # UNCHANGED
│   └── auth.py                  # UNCHANGED
├── requirements.txt             # MODIFIED — Remove groq/google-genai, add openai-agents
├── .env.example                 # MODIFIED — Remove GROQ/OPENAI/GEMINI keys, simplify
└── tests/
    ├── test_agent_config.py     # NEW — Agent infrastructure tests
    ├── test_llm_client.py       # DELETED — Old LLM client tests
    ├── test_chat_api.py         # MODIFIED — Update mocks
    ├── test_personalization_service.py  # MODIFIED — Update mocks
    ├── test_translation_service.py     # MODIFIED — Update mocks
    ├── test_translate_api.py           # MODIFIED — Update error imports
    └── test_personalize_cache.py       # MODIFIED — Update mocks
```

**Structure Decision**: Existing `backend/services/` structure retained. Single new file `agent_config.py` replaces `llm_client.py`. No directory restructuring needed.

## Architecture

### Agent Configuration Pattern

```python
# services/agent_config.py — core pattern
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, ModelSettings, set_tracing_disabled

# Disable tracing (no OpenAI platform key)
set_tracing_disabled(True)

# Shared Gemini client (singleton)
_client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY", ""),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Shared model instance
_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=_client)

# Three agents with distinct instructions
tutor_agent = Agent(name="tutor", instructions=TUTOR_SYSTEM_PROMPT, model=_model, ...)
personalization_agent = Agent(name="personalizer", instructions=PERSONALIZE_PROMPT, model=_model, ...)
translation_agent = Agent(name="translator", instructions=TRANSLATE_PROMPT, model=_model, ...)

# Embeddings via same client
async def embed(text: str) -> list[float]:
    response = await _client.embeddings.create(input=text, model="gemini-embedding-001")
    return response.data[0].embedding

# Agent runner helper
async def run_agent(agent: Agent, input: str) -> str:
    result = await Runner.run(agent, input=input)
    return result.final_output
```

### Integration Points

| Caller | Before | After |
|--------|--------|-------|
| `rag_service.embed()` | `genai.Client.models.embed_content()` (sync) | `_client.embeddings.create()` (async) |
| `rag_service.generate_answer()` | `llm_client.generate(prompt, system, ...)` | `Runner.run(tutor_agent, input=prompt)` |
| `personalization_service.personalize_chapter()` | `llm_client.generate(prompt, system, ...)` | `Runner.run(personalization_agent, input=prompt)` |
| `translation_service.translate_to_urdu()` | `llm_client.generate(prompt, system, ...)` | `Runner.run(translation_agent, input=prompt)` |

### Error Handling

| SDK Exception | Maps To | HTTP Status |
|---------------|---------|-------------|
| `openai.RateLimitError` | Rate limit | 429 |
| `openai.APIError` (5xx) | Server error | 503 |
| `openai.APITimeoutError` | Timeout | 503 |
| Any other `Exception` | Generic | 503 |

The old `AllProvidersExhaustedError` and `TransientLLMError` are removed. Standard `openai` exceptions replace them.

## Migration Strategy

### Phase 1: Infrastructure
1. Add `openai-agents` to requirements, remove `groq` and `google-genai`
2. Create `services/agent_config.py` with shared client, 3 agents, embed helper, run helper
3. Write tests for agent config

### Phase 2: Service Migration
4. Update `rag_service.py` — switch embed to async, switch generation to tutor agent
5. Update `personalization_service.py` — switch to personalization agent
6. Update `translation_service.py` — switch to translation agent

### Phase 3: Route Error Handling
7. Update `main.py` — replace `AllProvidersExhaustedError` with `openai` exceptions
8. Update `routes/translate.py` — update error imports
9. Update `routes/personalize.py` — update error imports

### Phase 4: Cleanup & Tests
10. Delete `services/llm_client.py`
11. Delete `tests/test_llm_client.py`
12. Update all test mocks to target agent_config instead of llm_client
13. Update `.env.example` — remove obsolete keys
14. Run full test suite, fix any remaining mock issues

### Phase 5: Verification
15. Full test suite passes (119+ tests)
16. TypeScript compilation clean
17. Manual smoke test (start backend, send chat/translate/personalize requests)

## Risks

1. **Gemini model name changes** — Google may rename/deprecate `gemini-2.5-flash`. Mitigated by making model name configurable via env var.
2. **OpenAI Agents SDK breaking changes** — SDK is pre-1.0. Mitigated by pinning version in requirements.txt.
3. **Embedding dimension mismatch** — If the OpenAI compat embedding format differs from `google-genai`, Qdrant queries may fail. Mitigated by testing embedding dimensions match (3072).

## Complexity Tracking

No constitution violations to justify. All gates pass cleanly.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
