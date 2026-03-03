# Implementation Plan: Docusaurus RAG Textbook

**Branch**: `001-docusaurus-rag-textbook` | **Date**: 2026-03-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-docusaurus-rag-textbook/spec.md`

## Summary

Build and deploy a Docusaurus v3 static textbook (Introduction + Module 1: ROS 2, 7 pages total) to GitHub Pages, with an embedded RAG chatbot that answers questions using Qdrant vector search + Gemini LLM. The chatbot is a floating React widget injected on every page via DocItem swizzling, with selected-text query support. The backend is a single stateless FastAPI endpoint (POST /api/chat) deployed to Railway/Vercel. No auth, no database, no sessions.

## Technical Context

**Frontend Language/Version**: TypeScript/JSX (Node.js 18+, React 18)  
**Backend Language/Version**: Python 3.11+  
**Primary Dependencies**:  
  - Frontend: Docusaurus 3.x, React 18, MDX  
  - Backend: FastAPI, uvicorn, openai (Python SDK), qdrant-client  
**Storage**: Qdrant Cloud (free tier) — vector database only; no relational DB  
**Testing**: pytest (backend contract tests), Docusaurus build check (frontend)  
**Target Platform**: Web (GitHub Pages for static site, Railway or Vercel for API)  
**Project Type**: Web application (static frontend + stateless API backend)  
**Performance Goals**: Pages load <3s on 4G; chatbot responds <5s (p95)  
**Constraints**: Stateless backend (no sessions/DB), 3 env vars only (GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY), max 2 services (static site + API)  
**Scale/Scope**: 7 pages, 1 API endpoint, 1 Qdrant collection, ~30–50 knowledge chunks  
**AI Model**: Gemini 2.0 Flash via OpenAI Python SDK (chat.completions pointed at Gemini endpoint)  
**Embeddings**: models/text-embedding-004 (Gemini)  
**Vector DB**: Qdrant Cloud free tier, collection `book_content`, chunk by H2/H3 headings (max 400 tokens), payload: text, chapter, module, page_title

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | MVP-First | ✅ PASS | Only 2 services (static site + API), 1 endpoint, 7 pages, no extras |
| II | No Auth/Personalization/Translation | ✅ PASS | FR-006, FR-013 explicitly forbid auth; no i18n; no user accounts |
| III | Content Scope (Intro + Module 1) | ✅ PASS | Exactly 7 pages: home + intro + 5 ROS 2 chapters |
| IV | Chatbot Omnipresence | ✅ PASS | Swizzled DocItem injects ChatbotWidget on every page; FR-009 |
| V | Deployability | ✅ PASS | GitHub Pages (static) + Railway/Vercel (API) — deploy in minutes |
| VI | No Over-Engineering | ✅ PASS | 1 FastAPI route, 1 service file, 1 indexing script; no ORM; ≤3 services |

**Gate Result**: ✅ ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-docusaurus-rag-textbook/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chat-api.md      # POST /api/chat contract
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
website/                          # Docusaurus 3 project root
├── docusaurus.config.ts          # Site config (title, URL, theme, navbar)
├── sidebars.ts                   # Sidebar navigation structure
├── package.json
├── tsconfig.json
├── static/
│   └── img/                      # Logos, diagrams
├── docs/
│   ├── intro/
│   │   └── index.md              # Introduction: What is Physical AI
│   └── module1-ros2/
│       ├── 01-architecture.md
│       ├── 02-nodes-topics-services.md
│       ├── 03-python-packages.md
│       ├── 04-launch-files.md
│       └── 05-urdf.md
├── src/
│   ├── components/
│   │   ├── ChatbotWidget.jsx     # Floating chat UI, calls /api/chat
│   │   └── SelectedTextHandler.jsx  # Text selection → chatbot
│   ├── css/
│   │   └── chatbot.css           # Chatbot widget styles
│   ├── theme/
│   │   └── DocItem/
│   │       └── index.tsx         # Swizzled DocItem wrapper
│   └── pages/
│       └── index.tsx             # Home/landing page
└── .env.example                  # REACT_APP_API_URL placeholder

backend/                          # FastAPI backend
├── main.py                       # FastAPI app, CORS, POST /api/chat
├── rag_service.py                # embed + retrieve + generate
├── index_content.py              # Chunk markdown → embed → upsert Qdrant
├── requirements.txt              # FastAPI, uvicorn, openai, qdrant-client
├── .env.example                  # GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY
├── Procfile                      # Railway deployment
└── tests/
    └── test_chat_api.py          # Contract tests for POST /api/chat
```

**Structure Decision**: Web application (frontend + backend). Frontend is a Docusaurus 3 project in `website/` with two custom React components swizzled into DocItem. Backend is a minimal FastAPI app in `backend/` with a single endpoint. Both are independently deployable. The two components share zero code—they communicate only via HTTP (POST /api/chat).

## Complexity Tracking

> No constitution violations. Table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
