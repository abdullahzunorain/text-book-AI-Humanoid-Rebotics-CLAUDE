---
id: 008
title: MVP2 Architecture Plan and Design Artifacts
stage: plan
date: 2025-07-24
surface: agent
model: claude-opus-4-6
feature: 002-mvp2-complete-textbook
branch: 002-mvp2-complete-textbook
user: abdullahzunorain
command: /speckit.plan
labels: ["architecture", "planning", "mvp2", "contracts", "data-model"]
links:
  spec: specs/002-mvp2-complete-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-mvp2-complete-textbook/plan.md
  - specs/002-mvp2-complete-textbook/research.md
  - specs/002-mvp2-complete-textbook/data-model.md
  - specs/002-mvp2-complete-textbook/contracts/translate.md
  - specs/002-mvp2-complete-textbook/contracts/auth.md
  - specs/002-mvp2-complete-textbook/contracts/background.md
  - specs/002-mvp2-complete-textbook/contracts/personalize.md
  - specs/002-mvp2-complete-textbook/quickstart.md
  - .github/agents/copilot-instructions.md
tests:
  - none (planning phase)
---

## Prompt

/speckit.plan

Plan — MVP2 Complete Textbook

Phase A (Content): 12 new content pages across 3 modules
Phase B (Subagents): 4 Claude subagents for content generation
Phase C (Urdu Translation): Urdu translation button with code-block preservation
Phase D (Auth): Email/password auth with JWT HTTP-only cookies
Phase E (Personalization): User background questionnaire + adapted AI responses

## Response snapshot

Completed full `/speckit.plan` workflow for MVP2:

**Phase 0 — Research** (research.md): 8 research topics resolved:
- R1: asyncpg + Neon Postgres (lifespan pool management)
- R2: python-jose JWT + passlib bcrypt (HS256, HTTP-only cookies)
- R3: Code-block extraction + Gemini translation (regex preserve)
- R4: Custom AuthProvider.tsx over better-auth (simpler, no risk)
- R5: Single structured Gemini prompt for profile-keyed adaptation
- R6: Direct filesystem path mapping for chapter slug resolution
- R7: Structured markdown subagent definitions
- R8: Neon free tier adequate (0.5 GB, 100 connections)

**Phase 1 — Design Artifacts**:
- data-model.md: ER diagram, SQL schema (users + user_backgrounds), entity details, state transitions
- contracts/translate.md: POST /api/translate (Urdu translation)
- contracts/auth.md: POST /api/auth/signup, POST /api/auth/signin, POST /api/auth/signout, GET /api/auth/me
- contracts/background.md: POST /api/user/background, GET /api/user/background
- contracts/personalize.md: POST /api/personalize (personalized RAG chat)
- quickstart.md: Developer setup guide with env vars, migration, backend/frontend startup

**Constitution Check**: 2 justified violations (Principles II & III) documented — amendment to v2.0.0 required before implementation.

Agent context updated (.github/agents/copilot-instructions.md) — corrected better-auth to custom AuthProvider.tsx.

## Outcome

- ✅ Impact: Complete architectural plan with 8 research decisions, full data model, 4 API contract files (8 endpoints), and developer quickstart
- 🧪 Tests: N/A (planning phase — test cases defined in contracts)
- 📁 Files: 9 files created/modified
- 🔁 Next prompts: /speckit.tasks to generate task breakdown, then amend constitution to v2.0.0
- 🧠 Reflection: Research phase was crucial — better-auth rejection saved potential React 19 compatibility issues. Custom AuthProvider decision reduces dependency risk.

## Evaluation notes (flywheel)

- Failure modes observed: Agent context script auto-detected "better-auth" from plan.md despite research deciding against it — manual correction needed
- Graders run and results (PASS/FAIL): PASS — all plan artifacts complete and internally consistent
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Amend constitution v2.0.0 before /speckit.tasks to avoid gate failures
