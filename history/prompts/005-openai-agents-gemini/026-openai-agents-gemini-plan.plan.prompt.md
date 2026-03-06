---
id: 026
title: OpenAI Agents Gemini Plan
stage: plan
date: 2026-03-06
surface: agent
model: claude-opus-4-6
feature: 005-openai-agents-gemini
branch: 005-openai-agents-gemini
user: zunorain
command: /speckit.plan
labels: ["openai-agents", "gemini", "architecture", "plan"]
links:
  spec: specs/005-openai-agents-gemini/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-openai-agents-gemini/plan.md
  - specs/005-openai-agents-gemini/research.md
  - specs/005-openai-agents-gemini/data-model.md
  - specs/005-openai-agents-gemini/contracts/api-contracts.md
  - specs/005-openai-agents-gemini/quickstart.md
  - .github/agents/copilot-instructions.md
tests:
  - N/A (plan phase — no tests yet)
---

## Prompt

Follow instructions in speckit.plan.prompt.md.

## Response snapshot

Created comprehensive implementation plan for replacing the hand-rolled LLM failover client with OpenAI Agents SDK + Gemini via OpenAI-compatible endpoint. Key research finding: Gemini's OpenAI compat layer supports embeddings too, allowing full removal of `google-genai` SDK. Plan defines 5-phase migration: infrastructure → service migration → route error handling → cleanup/tests → verification. Constitution check passes all gates. Generated 6 artifacts: plan.md, research.md, data-model.md, api-contracts.md, quickstart.md, updated copilot-instructions.md.

## Outcome

- ✅ Impact: Complete architecture plan with all research resolved, ready for `/speckit.tasks`
- 🧪 Tests: N/A (plan phase)
- 📁 Files: 6 artifacts created/updated
- 🔁 Next prompts: `/speckit.tasks` to generate implementation tasks
- 🧠 Reflection: Research revealed embeddings are supported via OpenAI compat — this simplifies the migration beyond original spec expectations (can remove google-genai entirely instead of keeping it for embeddings)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check — PASS (all gates)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
