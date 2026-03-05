# Hack-I-Copilot Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-04

## Active Technologies
- Python 3.13 (backend), TypeScript 5.x (frontend) + FastAPI 0.115+, python-jose (JWT), bcrypt, asyncpg, Docusaurus 3.9.2, React 19 (003-fix-auth-cookie-persistence)
- Neon PostgreSQL (asyncpg), Qdrant Cloud (vector DB — unaffected by this change) (003-fix-auth-cookie-persistence)
- Python 3.13 (backend), TypeScript 5.x (frontend) + FastAPI 0.115+, python-jose (JWT HS256), bcrypt, asyncpg, Docusaurus 3.9.2, React 19 (003-fix-auth-cookie-persistence)
- Python 3.13 (backend), TypeScript/React 19 (frontend) + FastAPI, asyncpg, google-genai, qdrant-client, python-jose, bcrypt, groq, openai (004-physical-ai-textbook)
- Neon Serverless PostgreSQL (users, backgrounds, cache, chat_messages) + Qdrant Cloud (vectors) (004-physical-ai-textbook)
- Python 3.13 + FastAPI, OpenAI Agents SDK (`openai-agents`), `openai` (transitive), `qdrant-client` (005-openai-agents-gemini)
- Neon PostgreSQL (asyncpg), Qdrant Cloud (vectors) — both unchanged (005-openai-agents-gemini)

- Python 3.12+ (backend, uv), TypeScript/React 19 (frontend, Docusaurus 3.9.2) + FastAPI, google-genai (gemini-2.5-flash, gemini-embedding-001), qdrant-client, asyncpg, python-jose[cryptography], passlib[bcrypt], custom AuthProvider.tsx (frontend) (002-mvp2-complete-textbook)

## Project Structure

```text
backend/          # FastAPI backend (Python, uv)
website/          # Docusaurus 3.9.2 frontend (TypeScript, React 19)
specs/            # Feature specs, plans, contracts
.specify/         # SpecKit Plus templates and scripts
```

## Commands

```bash
# Backend
cd backend && uv sync && uv run uvicorn main:app --reload
cd backend && uv run pytest -v

# Frontend
cd website && npm install && npm start
cd website && npm run build
```

## Code Style

- Python: type hints required, async/await for I/O, ruff for linting
- TypeScript: strict mode, React functional components with hooks

## Recent Changes
- 005-openai-agents-gemini: Added Python 3.13 + FastAPI, OpenAI Agents SDK (`openai-agents`), `openai` (transitive), `qdrant-client`
- 004-physical-ai-textbook: Added Python 3.13 (backend), TypeScript/React 19 (frontend) + FastAPI, asyncpg, google-genai, qdrant-client, python-jose, bcrypt, groq, openai
- 003-fix-auth-cookie-persistence: Added Python 3.13 (backend), TypeScript 5.x (frontend) + FastAPI 0.115+, python-jose (JWT HS256), bcrypt, asyncpg, Docusaurus 3.9.2, React 19


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
