```prompt
---
id: 018
title: Fix questionnaire 401 and visibility after auth state change
stage: green
date: 2025-07-24
surface: agent
model: Claude Sonnet 4.6
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: speckit.implement
labels: ["bug-fix","auth","questionnaire","react","frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - website/src/components/AuthButton.tsx
  - website/src/components/AuthModal.tsx
tests:
  - backend/tests/ (68 passed)
  - npx tsc --noEmit (0 errors)
---

## Prompt

not working, pls resolve this errors, bugs, and issues so that direct after authentication the website ask for personalization not when i signouting

## Response snapshot

Root cause identified: `BackgroundQuestionnaire` was nested inside the `return` branch that only renders when `isAuthenticated === false`.  After signup `setUser(data)` fires → `isAuthenticated` becomes `true` → React switches to the "Sign Out" branch → the questionnaire DOM node unmounts before it can be submitted, causing the 401 `not_authenticated`.

**Fix 1 — AuthButton.tsx**: Removed early-return auth-conditional structure.  Now the component always renders one `<>` fragment containing the auth button (conditional), `<AuthModal>`, and `<BackgroundQuestionnaire>` — all three always mounted.  Questionnaire visibility is driven by a `useEffect` that fires whenever `!loading && isAuthenticated && user?.has_background === false`, covering both the signup and signin-without-background flows.  `handleSignout` explicitly sets `showQuestionnaire=false`.  `handleQuestionnaireComplete` calls `setShowQuestionnaire(false)` + `void checkAuth()` so `has_background` refreshes to `true` and the effect does not re-fire.

**Fix 2 — AuthModal.tsx**: Added optional `onSigninSuccess?: () => void` prop.  On a successful signin the modal now calls `onSigninSuccess()` instead of `onClose()` (falls back to `onClose` if prop is absent for backwards compat).  AuthButton passes `handleSigninSuccess` which closes the modal; questionnaire is shown by the effect, not directly by the signin callback.

All 68 backend tests passed.  `npx tsc --noEmit` reported 0 errors.  Committed as `8c5ea2c`.

## Outcome

- ✅ Impact: Questionnaire now renders regardless of auth state, so submit has the cookie → no more 401.  Auto-shows after signup AND after signin when `has_background=false`.  Dismissed automatically after successful submit via `checkAuth()` refresh.
- 🧪 Tests: 68/68 backend tests pass; TypeScript: 0 errors
- 📁 Files: 2 files changed (AuthButton.tsx, AuthModal.tsx)
- 🔁 Next prompts: Restart backend with `uv run uvicorn main:app --reload --port 8000` to pick up latest `.env`; smoke-test the full signup → questionnaire → submit flow in browser
- 🧠 Reflection: The core bug was a React render-branch scoping issue: placing a modal inside a conditional `return` branch meant it unmounted when the condition flipped.  Moving overlays/modals to always-render outside conditionals is the standard pattern.

## Evaluation notes (flywheel)

- Failure modes observed: Questionnaire unmounting due to auth-conditional branch switch; 401 because component was gone before submit
- Graders run and results (PASS/FAIL): pytest 68/68 PASS, tsc PASS
- Prompt variant (if applicable): null
- Next experiment: Add an explicit "Skip for now" button on the questionnaire that marks a session flag so it doesn't keep re-appearing if the user intentionally skips
```
