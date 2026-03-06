# Quickstart: OpenAI Agents SDK with Gemini Models

**Feature**: 005-openai-agents-gemini  
**Date**: 2026-03-06

## Prerequisites

- Python 3.13+
- `uv` package manager
- `GOOGLE_API_KEY` from [Google AI Studio](https://aistudio.google.com)
- Existing Neon PostgreSQL + Qdrant Cloud setup (unchanged from Feature 004)

## Setup

```bash
# Switch to feature branch
git checkout 005-openai-agents-gemini

# Install updated dependencies
cd backend
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Key Changes from Feature 004

| Before (004) | After (005) |
|--------------|-------------|
| `services/llm_client.py` (406 lines, 3 providers, failover) | `services/agent_config.py` (~80 lines, 3 agents, single Gemini provider) |
| `google-genai` for embeddings + generation | Removed — all via OpenAI compat layer |
| `groq` package for failover | Removed |
| `get_llm_client().generate(prompt, system, ...)` | `Runner.run(agent, input=prompt)` |
| `AllProvidersExhaustedError` | Standard `openai` exceptions mapped to HTTP errors |

## Verify Setup

```bash
# Run all tests
python -m pytest tests/ -v

# Start backend
uvicorn main:app --reload --port 8000

# Quick smoke test
curl -s http://localhost:8000/ | python -m json.tool
```

## Environment Variables

Only one LLM key is now needed:

```env
# Required
GOOGLE_API_KEY=your-google-ai-studio-api-key

# Unchanged
DATABASE_URL=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=...
JWT_SECRET=...
CORS_ORIGINS=http://localhost:3000
```

`GEMINI_API_KEY`, `GROQ_API_KEY`, and `OPENAI_API_KEY` are no longer needed.

## Architecture Overview

```
Frontend (unchanged)
    │
    ▼
FastAPI Routes (unchanged contracts)
    │
    ├── POST /api/chat     → rag_service.generate_answer()
    │                             ├── embed() via AsyncOpenAI + gemini-embedding-001
    │                             ├── retrieve() via Qdrant
    │                             └── Runner.run(tutor_agent, input=...)
    │
    ├── POST /api/personalize → personalization_service.personalize_chapter()
    │                             ├── cache check
    │                             └── Runner.run(personalization_agent, input=...)
    │
    └── POST /api/translate  → translation_service.translate_to_urdu()
                                  ├── cache check
                                  └── Runner.run(translation_agent, input=...)
```
