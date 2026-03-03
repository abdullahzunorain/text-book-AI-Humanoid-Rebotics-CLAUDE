---
id: 003
title: Phase 0 Research Eight Technical Topics
stage: spec
date: 2026-03-03
surface: agent
model: claude-opus-4-6
feature: docusaurus-rag-textbook
branch: 001-docusaurus-rag-textbook
user: zunorain
command: research
labels: ["research", "docusaurus", "rag", "gemini", "qdrant", "fastapi", "github-pages", "railway"]
links:
  spec: specs/001-docusaurus-rag-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-docusaurus-rag-textbook/research.md
tests:
  - none
---

## Prompt

Research the following technical topics for building a Docusaurus v3 site with an embedded RAG chatbot. For each topic, provide: Decision (what to use/do), Rationale (why), and Alternatives Considered (what else was evaluated). Be concise and practical.

Topics to research:

1. **Docusaurus 3 DocItem swizzling**: How to swizzle the DocItem/Layout component in Docusaurus 3 to inject custom React components (ChatbotWidget, SelectedTextHandler) on every docs page. What is the correct swizzle path and pattern?

2. **Gemini via OpenAI Python SDK**: How to use the openai Python package to call Gemini 2.0 Flash (chat.completions) and Gemini text-embedding-004. What base_url and model strings to use? Any gotchas with the compatibility layer?

3. **Qdrant Cloud free tier**: What are the limits (vectors, collections, storage)? Best practices for a small collection (~50 vectors, 768-dim embeddings). How to create a collection and upsert/search via qdrant-client Python.

4. **FastAPI CORS for GitHub Pages**: How to configure CORS in FastAPI so a GitHub Pages frontend (on github.io domain) can call the API on Railway/Vercel. Minimal CORS middleware setup.

5. **Markdown chunking by headings**: Best approach to split Docusaurus markdown files by H2/H3 headings into chunks of max 400 tokens. Libraries or simple regex approach. How to preserve metadata (chapter, module, page_title) per chunk.

6. **GitHub Pages deployment for Docusaurus 3**: The recommended GitHub Actions workflow for deploying a Docusaurus 3 site. Key config in docusaurus.config.ts (url, baseUrl, organizationName, projectName).

7. **Text selection detection in React**: How to detect text selection (mouseup/selectionchange events) in a React component and position a floating popup near the selection. Cross-browser and mobile considerations.

8. **Railway deployment for FastAPI**: Minimal setup to deploy a FastAPI app to Railway (Procfile, requirements.txt, env vars). Any free tier limits to be aware of.

Return your findings as structured markdown with one ## section per topic, each containing Decision, Rationale, and Alternatives Considered subsections.

## Response snapshot

Created comprehensive research document at specs/001-docusaurus-rag-textbook/research.md covering all 8 technical topics with Decision, Rationale, Alternatives Considered, and working code snippets for each. Key decisions: (1) Wrap DocItem/Layout via swizzling, (2) openai SDK pointed at Gemini endpoint, (3) Qdrant Cloud free tier with cosine/768-dim, (4) Explicit CORS origins in CORSMiddleware, (5) Regex split by H2/H3 with 400-token max, (6) actions/deploy-pages with baseUrl config, (7) mouseup + selectionchange + getBoundingClientRect, (8) Railway Procfile + requirements.txt.

## Outcome

- ✅ Impact: Phase 0 research complete; all 8 topics documented with actionable decisions and code samples
- 🧪 Tests: none (research artifact)
- 📁 Files: specs/001-docusaurus-rag-textbook/research.md created
- 🔁 Next prompts: /sp.tasks to generate implementation tasks from plan + research
- 🧠 Reflection: Research covers all integration points; Railway free tier credit limit ($5 one-time) is the main risk for sustained hosting

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A — research artifact
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate Gemini base_url and model strings with a live API call before implementation
