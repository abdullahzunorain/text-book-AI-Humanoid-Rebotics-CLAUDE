---
id: 016
title: TDD Task Breakdown for Auth Cookie Fix
stage: tasks
date: 2026-03-05
surface: agent
model: claude-opus-4-6
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: /speckit.tasks
labels: ["tasks", "tdd", "cookie", "auth", "red-green-refactor"]
links:
  spec: specs/003-fix-auth-cookie-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-fix-auth-cookie-persistence/tasks.md
tests:
  - No tests run (task generation phase)
---

## Prompt

Follow instructions in speckit.tasks.prompt.md.
TDD Task Breakdown for 003-fix-auth-cookie-persistence. Branch: 003-fix-auth-cookie-persistence. Phase: Plan Complete (Updated). Detailed TDD Red-Green-Refactor breakdown for T1-T11 (environment detection, backend cookie management, CORS middleware, frontend fetch audit, error handling, testing plan, security validation). All tasks organized by user stories US1-US4 from spec.md.

## Response snapshot

Generated tasks.md with 36 tasks organized in 7 phases following strict TDD Red→Green→Refactor workflow:

- **Phase 1: Setup** (3 tasks) — env vars, file scaffolding
- **Phase 2: Foundational** (10 tasks) — cookie_config.py TDD cycle (8 RED tests → GREEN implementation → REFACTOR)
- **Phase 3: US1 — Signup & Save Background** (5 tasks) — P1 MVP, cookie set + "not_authenticated" detail
- **Phase 4: US2 — Sign In After Sign Out** (4 tasks) — P1, cookie clear with matching attrs
- **Phase 5: US3 — Production HTTPS Security** (5 tasks) — P1, expired/malformed JWT distinction
- **Phase 6: US4 — Personalize After Auth** (4 tasks) — P2, frontend audit + e2e verify
- **Phase 7: Polish** (5 tasks) — regression, edge cases, security checklist, quickstart validation

Format validation: 36/36 tasks have checkbox + ID + file path. 0 tasks missing paths. 22 parallel-marked. 18 story-labeled (US1:5, US2:4, US3:5, US4:4).

## Outcome

- ✅ Impact: Complete TDD task breakdown — immediately executable by LLM agent
- 🧪 Tests: 14 new test tasks defined (8 cookie config + 6 auth API)
- 📁 Files: 1 file created (tasks.md)
- 🔁 Next prompts: Begin implementation with Phase 1 Setup, then Phase 2 RED tests
- 🧠 Reflection: Tasks map cleanly to user stories. US1-US3 can run in parallel after Phase 2.

## Evaluation notes (flywheel)

- Failure modes observed: grep -c returns exit code 1 when count is 0, needed || true
- Graders run and results (PASS/FAIL): Format validation PASS (36/36 tasks, 0 missing paths)
- Prompt variant (if applicable): User provided detailed TDD table (T1-T11, S1-S6) as input
- Next experiment (smallest change to try): Start Phase 1 Setup → Phase 2 RED tests
