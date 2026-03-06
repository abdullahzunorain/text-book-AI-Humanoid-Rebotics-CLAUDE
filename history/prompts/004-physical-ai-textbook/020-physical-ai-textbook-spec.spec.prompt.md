```prompt
---
id: 020
title: Physical AI textbook platform specification
stage: spec
date: 2026-03-05
surface: agent
model: Claude Opus 4.6
feature: 004-physical-ai-textbook
branch: 004-physical-ai-textbook
user: zunorain
command: speckit.specify
labels: ["spec","hackathon","textbook","physical-ai","robotics"]
links:
  spec: specs/004-physical-ai-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-physical-ai-textbook/spec.md
  - specs/004-physical-ai-textbook/checklists/requirements.md
tests:
  - Specification quality checklist: 14/14 items pass
---

## Prompt

Hackathon I: Create a Textbook for Teaching Physical AI & Humanoid Robotics Course [full hackathon description with requirements, course details, modules, hardware specs, and scoring rubric]

## Response snapshot

Created feature branch `004-physical-ai-textbook` and wrote comprehensive specification at `specs/004-physical-ai-textbook/spec.md`.

Spec covers all 7 hackathon deliverables:
1. **Textbook** (P1): 4 modules, 17+ chapters, Docusaurus static site
2. **RAG Chatbot** (P1): Embedded widget, textbook-sourced answers
3. **Selected-text Q&A** (P2): Scoped answers from highlighted passages
4. **Auth** (P2): Email/password signup/signin with httpOnly cookies
5. **Background Questionnaire** (P2): Python level, robotics exp, math, hardware, learning goal
6. **Personalization** (P2): Per-chapter content adaptation based on profile
7. **Urdu Translation** (P2): Per-chapter translation with RTL rendering

29 functional requirements (FR-001 through FR-029), 9 measurable success criteria, 6 user stories with acceptance scenarios, 6 edge cases, key entities, assumptions, and scope boundaries.

Quality checklist: 14/14 items pass. No NEEDS CLARIFICATION markers — all requirements derived from the detailed hackathon description and existing project context.

## Outcome

- ✅ Impact: Complete specification ready for planning phase
- 🧪 Tests: Quality checklist 14/14 pass
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: `/speckit.plan` to create architectural plan, then `/speckit.tasks` for task breakdown
- 🧠 Reflection: The hackathon description was extremely detailed, providing all the context needed to derive requirements without clarification. Existing project (already has all 4 modules, chatbot, auth, personalization, translation) confirms the spec matches reality.

## Evaluation notes (flywheel)

- Failure modes observed: None — spec derived cleanly from detailed input
- Graders run and results (PASS/FAIL): Quality checklist 14/14 PASS
- Prompt variant (if applicable): null
- Next experiment: null
```
