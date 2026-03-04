# Quickstart — MVP2 Complete Textbook

## Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.12+ with [uv](https://docs.astral.sh/uv/)
- **Neon Postgres** account (free tier: https://neon.tech)
- **Google AI** API key (Gemini 2.5 Flash access)
- **Qdrant Cloud** cluster (from MVP1)

## 1. Environment Setup

```bash
# Clone and checkout feature branch
git checkout 002-mvp2-complete-textbook

# Backend: create .env from template
cp backend/.env.example backend/.env
```

Fill `backend/.env`:

```env
GEMINI_API_KEY=<your-google-ai-key>
QDRANT_URL=<your-qdrant-cloud-url>
QDRANT_API_KEY=<your-qdrant-api-key>
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>/<db>?sslmode=require
JWT_SECRET=<random-32+-char-string>
```

Generate JWT_SECRET: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## 2. Database Migration

```bash
cd backend
# Run migration (creates users + user_backgrounds tables)
uv run python migrations/001_create_users.py
```

## 3. Backend

```bash
cd backend
uv sync                          # Install deps (adds asyncpg, python-jose, passlib)
uv run uvicorn main:app --reload # http://localhost:8000
```

Verify: `curl http://localhost:8000/health`

## 4. Frontend

```bash
cd website
npm install
npm run clear && npm start       # http://localhost:3000
```

## 5. Run Tests

```bash
# Backend
cd backend && uv run pytest -v

# Frontend (if applicable)
cd website && npm test
```

## 6. Key Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/signup | No | Create account |
| POST | /api/auth/signin | No | Sign in |
| POST | /api/auth/signout | No | Clear cookie |
| GET | /api/auth/me | JWT | Check auth |
| POST | /api/translate | No | Urdu translation |
| POST | /api/user/background | JWT | Save profile |
| GET | /api/user/background | JWT | Get profile |
| POST | /api/personalize | JWT | Personalized chat |
| POST | /api/chat | No | Standard chat (MVP1) |
