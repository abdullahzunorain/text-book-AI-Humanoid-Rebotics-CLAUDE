# Hack-I-Copilot Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-04

## Active Technologies

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

- 002-mvp2-complete-textbook: Added asyncpg (Neon Postgres), python-jose[cryptography] (JWT auth), passlib[bcrypt], custom AuthProvider.tsx (replaced better-auth per research R4)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
