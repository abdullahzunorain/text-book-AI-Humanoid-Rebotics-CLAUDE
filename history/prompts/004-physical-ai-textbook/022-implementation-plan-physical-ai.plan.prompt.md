---
id: 022
title: Implementation Plan for Physical AI Textbook
stage: plan
date: 2026-03-06
surface: agent
model: claude-opus-4-6
feature: 004-physical-ai-textbook
branch: 004-physical-ai-textbook
user: abdullahzunorain
command: /speckit.plan
labels: ["architecture", "plan", "failover", "caching", "chat-history", "rag"]
links:
  spec: specs/004-physical-ai-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-physical-ai-textbook/plan.md
  - specs/004-physical-ai-textbook/research.md
  - specs/004-physical-ai-textbook/data-model.md
  - specs/004-physical-ai-textbook/contracts/api-contracts.md
  - specs/004-physical-ai-textbook/quickstart.md
  - .github/agents/copilot-instructions.md
tests:
  - none (planning phase — no code changes)
---

## Prompt

/speckit.plan

Instructions for the plan:
1. High-Level System Architecture — Show the full system: frontend (Docusaurus), backend (FastAPI), and all integrations (Qdrant, Neon DB, Gemini, Groq, OpenAI). Include the RAG pipeline, multi-model failover chain, caching layer, and chat persistence. This should give a bird's-eye view of every component and how they communicate.
2. Backend Blueprint — Detail every API endpoint (existing + new), the multi-model LLM failover/retry logic, auth flow, and RAG/Qdrant integration. Include the new services (llm_client.py, cache_service.py, chat_history_service.py) and how they plug into the existing routes.
3. RAG Pipeline Design — Explain the full pipeline: markdown chunking (500–1000 tokens), embedding with Gemini Embedding 1, Qdrant upsert/retrieval, and answer generation. Cover how selected-text Q&A works and any multilingual considerations.
4. Caching & Chat Persistence — Design the content_cache table (personalization + translation), define invalidation rules (personalization invalidated on profile update; translation never invalidated), and define the chat_messages table. Cover httpOnly cookie session management, and how chat history survives sign-out and is available indefinitely.
5. Deployment & Infrastructure — Map out GitHub Pages (frontend), Railway (backend), Neon DB, and Qdrant Cloud. Include monitoring, health checks, and the CI pipeline.
6. Validation & Testing — Align every test with the spec's FRs and SCs. Cover unit tests (LLM client, cache, chat), contract tests (API schemas), integration tests (DB flows), and E2E (manual). Include edge cases for failover and rate-limiting.

Include diagrams, flowcharts, and clear component responsibilities. Include edge case handling and failover strategies explicitly.

## Response snapshot

Generated comprehensive implementation plan with 6 artifacts:

1. **plan.md** — Full architectural plan covering all 6 requested sections with ASCII diagrams for system architecture, request flow, failover flowchart, and cache decision flow. Includes Technical Context, Constitution Check (PASS with justified violations for Principles II/III), and Project Structure.

2. **research.md** — Phase 0 research resolving 8 technical decisions: multi-model failover pattern (chain-of-responsibility), exponential backoff (base 7, capped 60s, with jitter), DB caching (single table), chat persistence (append-only), Groq SDK (llama-3.3-70b-versatile), OpenAI SDK (gpt-4o-mini), Qdrant multi-module indexing, frontend chat history UI.

3. **data-model.md** — Complete data model with ER diagram, 4 tables (2 existing: users, user_backgrounds; 2 new: content_cache, chat_messages), Qdrant collection schema, and full migration SQL.

4. **contracts/api-contracts.md** — Full REST API contracts for 11 endpoints including new GET /api/chat/history. Covers request/response schemas, validation rules, error taxonomy, cookie contract, idempotency notes, and timeouts.

5. **quickstart.md** — Developer setup guide: prerequisites, backend/frontend setup, migrations, indexing, and deployment.

6. Agent context updated via `update-agent-context.sh copilot`.

Key architectural decisions:
- 3 new backend services: llm_client.py, cache_service.py, chat_history_service.py
- 2 new DB tables: content_cache, chat_messages (migration 002)
- 1 new endpoint: GET /api/chat/history
- Multi-model failover: Gemini → Groq → OpenAI with exp backoff (5 attempts, base 7, 1s, capped 60s)
- New dependencies: groq, openai

Committed as b34ee2d on branch 004-physical-ai-textbook.

## Outcome

- ✅ Impact: Complete implementation plan with all Phase 0 and Phase 1 artifacts generated. Ready for /speckit.tasks.
- 🧪 Tests: No code changes — planning phase only
- 📁 Files: 6 files created/modified (plan.md, research.md, data-model.md, api-contracts.md, quickstart.md, copilot-instructions.md)
- 🔁 Next prompts: /speckit.tasks to generate implementation tasks from the plan
- 🧠 Reflection: Constitution violations (Principles II and III) are pre-existing — the codebase already has auth, personalization, and translation. Recommend amending constitution to v2.0.0.

## Evaluation notes (flywheel)

- Failure modes observed: None — all plan artifacts generated successfully
- Graders run and results (PASS/FAIL): Constitution Check PASS (with justified violations)
- Prompt variant (if applicable): Standard /speckit.plan with 6-section user guidance
- Next experiment: Verify task decomposition covers all new services and migration
