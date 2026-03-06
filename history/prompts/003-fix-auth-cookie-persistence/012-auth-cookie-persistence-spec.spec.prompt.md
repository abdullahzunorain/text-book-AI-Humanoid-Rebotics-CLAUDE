---
id: 012
title: Auth Cookie Persistence Specification
stage: spec
date: 2025-07-16
surface: agent
model: claude-opus-4-20250514
feature: 003-fix-auth-cookie-persistence
branch: 003-fix-auth-cookie-persistence
user: zunorain
command: /speckit.specify
labels: ["auth", "cookies", "security", "bug-fix"]
links:
  spec: specs/003-fix-auth-cookie-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-fix-auth-cookie-persistence/spec.md
  - specs/003-fix-auth-cookie-persistence/checklists/requirements.md
tests:
  - none (specification phase only)
---

## Prompt

Fix cookie-based auth persistence: secure flag blocks cookies on localhost HTTP, causing 401 errors after signup/signout on dev environment. Do NOT jump to code immediately. First analyze architecture and authentication flow carefully. Then propose a clean, production-safe fix strategy.

## Response snapshot

Created feature branch `003-fix-auth-cookie-persistence` and wrote a comprehensive specification analyzing the root cause of 401 errors after signup/signout. Key findings:

1. **Root cause**: `_set_token_cookie()` in `routes/auth.py` unconditionally sets `secure=True`. Browsers comply with RFC 6265 §5.4 — cookies with the Secure attribute are never sent over HTTP. On `http://localhost`, the cookie is received but silently dropped on subsequent requests.

2. **Secondary factors**: `SameSite=Lax` combined with cross-port fetch (3000→8000) and the Secure flag compound the issue. CORS and frontend `credentials: 'include'` are correctly configured.

3. **Specification includes**: 4 prioritized user stories (P1-P2), 10 functional requirements (FR-001 to FR-010), 6 measurable success criteria (SC-001 to SC-006), 6 edge cases, and 5 documented assumptions.

4. **Quality checklist**: All 16 checklist items pass. No NEEDS CLARIFICATION markers needed.

## Outcome

- ✅ Impact: Feature specification created — ready for `/speckit.plan` or `/speckit.clarify`
- 🧪 Tests: None (specification phase only)
- 📁 Files: spec.md, checklists/requirements.md
- 🔁 Next prompts: `/speckit.plan` to create architecture plan, then `/speckit.tasks` for implementation tasks
- 🧠 Reflection: Root cause was clear from codebase analysis — `secure=True` on HTTP is the definitive issue. No clarification markers were needed.

## Evaluation notes (flywheel)

- Failure modes observed: None — problem was well-defined and root cause identifiable from code.
- Graders run and results (PASS/FAIL): Quality checklist 16/16 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase with environment-aware cookie configuration strategy.
