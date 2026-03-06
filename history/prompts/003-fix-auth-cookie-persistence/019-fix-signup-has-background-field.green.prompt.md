```prompt
---
id: 019
title: Fix signup response missing has_background field
stage: green
date: 2026-03-05
surface: agent
model: Claude Sonnet 4.6
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: speckit.implement
labels: ["bug-fix","auth","signup","questionnaire","backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/routes/auth.py
  - backend/tests/test_auth_api.py
tests:
  - backend/tests/ (68 passed)
---

## Prompt

(backend) uv run uvicorn main:app --reload --port 8000 [shows 4x POST /api/user/background 401]
pls run this functionality and check by yourself, is it working or not??

## Response snapshot

Ran full live diagnostic:

1. `curl` signup → confirmed `set-cookie: token=...; HttpOnly; SameSite=lax` (no Secure — correct for dev)
2. `curl` background POST with cookie → **200 OK** (backend works perfectly)
3. Identified the real bug: signup response returned `{"show_questionnaire": true}` — a field the frontend `User` interface doesn't have. `AuthButton`'s `useEffect` checks `user?.has_background === false` to open the questionnaire; `undefined === false` is `false`, so the questionnaire **never opened** after signup, and any old-session submits (from before the Secure=True → False fix, where the browser had no cookie) hit the endpoint without a cookie → 401.

**Root cause**: two compounding issues:
- `show_questionnaire` field was silently ignored by the frontend (`User` interface only has `user_id`, `email`, `has_background?`)
- Old server session (Secure=True) meant browser had no stored cookie; questionnaire was showing from React state but submitting without credentials

**Fix — `backend/routes/auth.py`**: Replace `"show_questionnaire": True` with `"has_background": False` in the signup response. New users always have no background profile.

**Fix — `backend/tests/test_auth_api.py`**: Add `assert data["has_background"] is False` to the signup contract test.

Live e2e verified: signup (has_background=false) → background POST → 200 OK.
68/68 tests pass. Committed as `ccf2d89`.

## Outcome

- ✅ Impact: Questionnaire now opens automatically after signup via the useEffect in AuthButton. Background POST succeeds with the valid cookie from the fresh signup.
- 🧪 Tests: 68/68 PASS
- 📁 Files: 2 files changed (routes/auth.py, tests/test_auth_api.py)
- 🔁 Next prompts: Hard-refresh the browser (Ctrl+Shift+R), sign up with a new email, confirm questionnaire appears and submits successfully
- 🧠 Reflection: The fix was in the backend response contract — frontend was correct all along. The `show_questionnaire` field was dead code that never connected to any frontend type. Always align backend response fields to the frontend `User` interface.

## Evaluation notes (flywheel)

- Failure modes observed: Response field name mismatch (show_questionnaire vs has_background) silently broke the questionnaire trigger; compounded by stale browser cookie from old Secure=True server
- Graders run and results (PASS/FAIL): pytest 68/68 PASS; live curl e2e PASS
- Prompt variant (if applicable): null
- Next experiment: Add a TypeScript type for the exact signup/signin response shape (separate from User) to catch field mismatches at compile time
```
