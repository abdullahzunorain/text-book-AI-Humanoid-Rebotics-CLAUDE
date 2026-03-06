---
id: 013
title: Auth Cookie Spec Clarification Session
stage: spec
date: 2025-07-16
surface: agent
model: claude-opus-4-20250514
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: /speckit.clarify
labels: ["auth", "cookies", "security", "clarification", "cross-site"]
links:
  spec: specs/003-fix-auth-cookie-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-fix-auth-cookie-persistence/spec.md
tests:
  - none (clarification phase only)
---

## Prompt

Follow speckit.clarify instructions. Before proposing fixes, ask clarifying questions about JWT generation/storage, signup auto-login, cookie flags, CORS config, frontend fetch credentials, origin separation, and token validation. Identify missing architectural details that could cause 401 on /api/auth/me and /api/user/background.

## Response snapshot

Ran structured ambiguity scan across 11 taxonomy categories. Asked 5 sequential clarification questions, all accepted:

1. **Production safety guard** (B): Auto-detect HTTPS via CORS_ORIGINS and force Secure=True regardless of APP_ENV. Log warning on contradiction. → Added FR-011.
2. **Token expiry distinction** (A): Return distinct 401 detail strings: `not_authenticated`, `session_expired`, `invalid_token`. → Updated FR-006 and cookie expiry edge case.
3. **CORS origins config** (B): Environment-driven via `CORS_ORIGINS` env var. Dev lists localhost; production lists GitHub Pages domain. → Updated FR-010, FR-011, CORS entity.
4. **SameSite cross-site split** (user-corrected): User identified critical hidden catch — production is true cross-site (GitHub Pages → Railway), requiring `SameSite=None` + `Secure=True` in prod. Dev stays `Lax` + `Secure=False`. → Updated FR-004, FR-005, Root Cause Analysis, US3 scenario, SC-003, JWT entity.
5. **Frontend API_URL** (A): In scope — cookie fix is meaningless if frontend targets wrong backend. API_URL via Docusaurus customFields. → Added FR-012 and SC-007.

Key user correction on Q4: The original spec assumed SameSite=Lax works in production. User correctly identified that GitHub Pages → Railway is cross-site, requiring SameSite=None. This was the most architecturally significant finding.

## Outcome

- ✅ Impact: Spec clarified from 135 to 149 lines. 5 questions asked, 5 answered. All critical ambiguities resolved.
- 🧪 Tests: None (clarification phase only)
- 📁 Files: spec.md updated with Clarifications section and refined requirements
- 🔁 Next prompts: `/speckit.plan` to create architecture plan
- 🧠 Reflection: Q4 user correction was critical — same-site vs cross-site distinction for production deployment was the most impactful finding. Without this, production auth would have been broken even after the Secure flag fix.

## Evaluation notes (flywheel)

- Failure modes observed: Q4 initially recommended keeping SameSite=Lax for both envs — user caught the cross-site deployment topology. Agent should have analyzed the actual production deployment architecture (frontend domain vs backend domain) more carefully.
- Graders run and results (PASS/FAIL): Final validation PASS — 0 duplicates, 0 placeholders, 5 clarifications, all sections consistent.
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): When analyzing cookie attributes, always map the actual deployment topology (same-site vs cross-site) before recommending SameSite values.
