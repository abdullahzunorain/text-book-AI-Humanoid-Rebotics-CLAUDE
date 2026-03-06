---
id: 017
title: Implement Auth Cookie Persistence Fix
stage: green
date: 2025-07-23
surface: agent
model: Claude Opus 4.6
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: /speckit.implement
labels: ["cookie", "auth", "tdd", "implementation"]
links:
  spec: specs/003-fix-auth-cookie-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/cookie_config.py
  - backend/main.py
  - backend/routes/auth.py
  - backend/routes/personalize.py
  - backend/tests/test_cookie_config.py
  - backend/tests/test_auth_api.py
  - backend/tests/test_personalize_api.py
  - backend/.env
tests:
  - backend/tests/test_cookie_config.py (15 tests — all pass)
  - backend/tests/test_auth_api.py (14 tests — 6 new, all pass)
  - backend/tests/test_personalize_api.py (4 tests — 1 updated, all pass)
  - Full regression: 68/68 pass
---

## Prompt

/speckit.implement

## Response snapshot

Executed all 36 tasks across 7 phases following TDD Red→Green→Refactor:

**Phase 1 (Setup):** Added CORS_ORIGINS env var, created cookie_config.py and test scaffolds.

**Phase 2 (Foundational TDD):** Wrote 15 failing tests for get_cookie_config(), implemented the module with APP_ENV + HTTPS auto-detect logic, replaced hardcoded CORS in main.py with env var parsing. All 15 tests green.

**Phase 3 (US1 Signup):** RED — 2 failing tests for cookie attrs + not_authenticated detail. GREEN — Modified _set_token_cookie() to use get_cookie_config(), updated detail string. 10/10 pass.

**Phase 4 (US2 Signout/Signin):** RED — 1 failing test (signout Secure flag). GREEN — Modified _clear_token_cookie() to use get_cookie_config(). 12/12 pass.

**Phase 5 (US3 Production/401):** RED — 2 failing tests for session_expired and invalid_token. GREEN — Added ExpiredSignatureError + JWTError catch in _get_user_id_from_cookie(). 29/29 pass.

**Phase 6 (US4 Frontend Audit):** All 6 authenticated fetch calls have credentials:'include'. API_URL resolves correctly in all 5 components. docusaurus.config.ts reads REACT_APP_API_URL. Updated personalize route's duplicated auth function.

**Phase 7 (Polish):** Full regression 68/68 pass. Security checklist S1-S6 verified. Committed on branch 003-fix-auth-cookie-persistence.

## Outcome

- ✅ Impact: Cookie auth persistence fixed — dev uses Secure=False/SameSite=Lax, prod uses Secure=True/SameSite=None
- 🧪 Tests: 68/68 pass (21 new tests added)
- 📁 Files: 5 modified, 2 new, 1 env updated
- 🔁 Next prompts: Manual browser testing on localhost, production deployment with CORS_ORIGINS set to GitHub Pages URL
- 🧠 Reflection: Discovered personalize.py had a duplicated _get_user_id_from_cookie() that also needed updating — caught by regression suite

## Evaluation notes (flywheel)

- Failure modes observed: Duplicated auth helper in personalize.py needed same fix (not in original task list)
- Graders run and results (PASS/FAIL): pytest 68/68 PASS, security checklist S1-S6 PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Extract _get_user_id_from_cookie into shared auth middleware to eliminate duplication
