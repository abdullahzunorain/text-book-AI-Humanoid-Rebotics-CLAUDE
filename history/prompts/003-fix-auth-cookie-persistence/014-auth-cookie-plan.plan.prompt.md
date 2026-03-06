---
id: 014
title: Auth Cookie Persistence Plan
stage: plan
date: 2026-03-05
surface: agent
model: claude-opus-4-dot-6
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: /sp.plan
labels: ["auth", "cookies", "planning", "architecture"]
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
tests:
  - none (planning phase — no code changes)
---

## Prompt

User invoked `/sp.plan` to generate the implementation plan for feature `003-fix-auth-cookie-persistence`. The plan addresses fixing cookie-based auth persistence where `secure=True` on HTTP localhost blocks cookies, and `SameSite=Lax` breaks cross-site production (GitHub Pages → Railway). User provided detailed plan objectives, scope, task table (T1-T11), environment config examples, and testing plan.

## Response snapshot

Executed full speckit.plan workflow:
- **Phase 0 (Research)**: Created `research.md` with 7 research findings — FastAPI set_cookie behavior, browser Secure cookie handling on localhost, CORS_ORIGINS parsing, HTTPS auto-detect guard, python-jose ExpiredSignatureError, Docusaurus customFields patterns, cookie clearing attribute matching.
- **Phase 1 (Design)**: Created `data-model.md` (CookieConfig entity, CORS config, unchanged DB schema), `contracts/cookie-contract.md` (Set-Cookie headers per env, 401 error codes, CORS headers, auto-detect guard), `quickstart.md` (env setup, TDD workflow, browser verification steps, troubleshooting).
- Updated agent context via `update-agent-context.sh copilot`.
- Constitution check: PASS (auth is post-MVP2, this is a bug fix).

## Outcome

- ✅ Impact: Complete plan with 5 artifacts ready for task generation
- 🧪 Tests: No tests yet — planning phase only
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, cookie-contract.md)
- 🔁 Next prompts: `/sp.tasks` to generate testable task breakdown
- 🧠 Reflection: Research phase resolved all NEEDS CLARIFICATION items from spec. Cross-site cookie topology (SameSite=None + Secure) is the key architectural insight.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate tasks.md with TDD red-green-refactor structure
