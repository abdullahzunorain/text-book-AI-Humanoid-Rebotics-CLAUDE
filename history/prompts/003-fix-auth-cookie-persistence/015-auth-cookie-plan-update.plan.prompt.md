---
id: 015
title: Auth Cookie Plan Update with Full Scope
stage: plan
date: 2026-03-05
surface: agent
model: claude-opus-4-6
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: /speckit.plan
labels: ["cookie", "auth", "plan", "security", "cors", "edge-cases"]
links:
  spec: specs/003-fix-auth-cookie-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-fix-auth-cookie-persistence/plan.md
  - specs/003-fix-auth-cookie-persistence/research.md
  - specs/003-fix-auth-cookie-persistence/data-model.md
  - specs/003-fix-auth-cookie-persistence/quickstart.md
  - specs/003-fix-auth-cookie-persistence/contracts/cookie-contract.md
  - .github/agents/copilot-instructions.md
tests:
  - No tests run (planning phase)
---

## Prompt

Follow instructions in speckit.plan.prompt.md.
pls a bit update the plan if needed as below instruction...

Context:
We have a FastAPI backend serving a RAG-powered Physical AI & Humanoid Robotics textbook platform. 
Authentication uses JWT stored in cookies. We have development (localhost HTTP) and production (HTTPS) environments. 
Current issue: On localhost, after signup/signin, authenticated endpoints (/api/auth/me, /api/user/background) return 401 because JWT cookie is not sent. 
Secure cookie flag is blocking HTTP transmission. Production works correctly (Secure=True, SameSite=None). 

Objective:
Design a complete, environment-aware plan to fix cookie-based authentication persistence across development and production, ensuring:

1. JWT cookie is set and transmitted correctly.
2. Secure flag is conditional based on environment.
3. SameSite is set appropriately (Lax for dev, None for production).
4. CORS and frontend fetch credentials are configured properly.
5. Sign-out clears cookies correctly.
6. Edge cases are handled (multiple tabs, mixed protocols, cookie expiry, port mismatch).
7. No regression in production security.

Tasks & Steps:

1. Environment Detection & Configuration
2. Backend Cookie Management
3. CORS Middleware
4. Frontend Fetch / API Calls
5. Error Handling & Response
6. Testing Plan
7. Security Validation
8. Documentation

## Response snapshot

Updated all Phase 0+1 plan artifacts with comprehensive scope from user's detailed instructions:

- **plan.md**: Expanded to include full task table (T1-T11), detailed design for each task, environment configuration examples (dev/prod), testing plan with 14 test cases, security validation matrix, and edge case testing plan (multiple tabs, port mismatch, cookie expiry, cookies disabled). Added Post-Phase 1 constitution re-check (PASS).
- **research.md**: Added 5 new research items (R8-R12): frontend credentials audit, multi-tab cookie state, mixed protocol transitions, cookies disabled scenario, port mismatch handling.
- **data-model.md**: Added security invariants table (6 checks), multi-tab state diagram, environment transition diagram, auto-detect edge case diagram.
- **contracts/cookie-contract.md**: Bumped to v1.1. Added security validation contract (6 invariants S1-S6), edge case contract table (7 cases).
- **quickstart.md**: Added sections 8 (env var reference for APP_ENV, CORS_ORIGINS, REACT_APP_API_URL, JWT_SECRET) and 9 (running dev/prod locally, simulating production with mkcert, Railway+GitHub Pages deployment).

## Outcome

- ✅ Impact: Comprehensive plan covering all 8 areas from user's request — environment detection, cookie management, CORS, frontend, error handling, testing, security, documentation.
- 🧪 Tests: Planning phase — test plan defines 14 unit tests + 5 edge case scenarios.
- 📁 Files: 5 spec artifacts updated, 1 agent context file refreshed.
- 🔁 Next prompts: `/sp.tasks` to generate testable task breakdown with TDD red-green-refactor.
- 🧠 Reflection: The setup-plan.sh script overwrites plan.md with the template on each run. Had to rewrite from scratch. Consider storing plan content before running setup in future.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.sh overwrites existing plan.md — lost previous content (recovered from conversation context)
- Graders run and results (PASS/FAIL): Constitution check PASS (pre and post-design)
- Prompt variant (if applicable): Plan update with detailed user scope instructions
- Next experiment (smallest change to try): Proceed to `/sp.tasks` for TDD task generation
