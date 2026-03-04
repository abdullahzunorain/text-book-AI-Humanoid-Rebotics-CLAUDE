---
id: 009
title: MVP2 Spec Clarification Five Questions
stage: spec
date: 2026-03-04
surface: agent
model: claude-opus-4-6
feature: 002-mvp2-complete-textbook
branch: 002-mvp2-complete-textbook
user: abdullahzunorain
command: /speckit.clarify
labels: ["clarification", "spec", "mvp2", "schema", "security"]
links:
  spec: specs/002-mvp2-complete-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-mvp2-complete-textbook/spec.md
  - specs/002-mvp2-complete-textbook/contracts/background.md
  - specs/002-mvp2-complete-textbook/contracts/personalize.md
  - specs/002-mvp2-complete-textbook/contracts/translate.md
tests:
  - none (clarification phase)
---

## Prompt

/speckit.clarify

Review specs/002-mvp2-complete-textbook/spec.md and the previous sp.plan outline. Clarify ambiguities across 6 areas: Content (filenames, word counts), Subagents (behavior, Gemini config), Urdu Translation (code blocks, RTL CSS), Auth (DB schema, JWT claims, questionnaire fields), Personalization (attributes, code vs prose), Testing (TDD approach, linting).

## Response snapshot

Performed structured ambiguity scan across 11 taxonomy categories. Found 5 critical ambiguities and resolved all 5 via sequential Q&A:

1. **Questionnaire Schema** → Spec's 5 fields canonical (python_level, robotics_experience, math_level, hardware_access, learning_goal). Fixed contracts/background.md and contracts/personalize.md to match.
2. **Personalization Scope** → Prose only; code examples remain unchanged. Fixed FR-033 contradiction.
3. **Rate Limiting** → Added FR-016a: 10 req/min per IP on /api/translate. Updated contracts/translate.md with 429 response.
4. **better-auth Reference** → Fixed FR-017 to reference custom AuthProvider.tsx per R4 decision.
5. **Content Generation Method** → 12 pages written manually in Phase A; subagents (Phase B) are for future maintenance.

All answers integrated into spec.md Clarifications section and relevant FRs/contracts.

## Outcome

- ✅ Impact: 5 ambiguities resolved, 3 contracts updated, 2 FRs corrected, 1 FR added
- 🧪 Tests: N/A (clarification phase)
- 📁 Files: 4 files modified (spec.md, contracts/background.md, contracts/personalize.md, contracts/translate.md)
- 🔁 Next prompts: /speckit.tasks to generate task breakdown, or /speckit.plan if further planning needed
- 🧠 Reflection: Schema divergence between spec and contracts (5 fields vs 3 fields) was the highest-impact find — would have caused DB migration rework if caught during implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Contract files created during /speckit.plan used different field names than spec (plan phase didn't cross-reference spec schema closely enough)
- Graders run and results (PASS/FAIL): PASS — all 5 clarifications integrated, no contradictions remain
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): During /speckit.plan, add automated cross-reference check between spec API contracts and generated contract files
