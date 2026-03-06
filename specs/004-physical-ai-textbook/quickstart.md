# Quickstart: Physical AI & Humanoid Robotics Textbook Platform

**Feature Branch**: `004-physical-ai-textbook`

---

## Prerequisites

- Python 3.13+, Node.js 20+, npm 10+
- API keys: `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY`
- Neon DB connection string (`DATABASE_URL`)
- Qdrant Cloud credentials (`QDRANT_URL`, `QDRANT_API_KEY`)

## Setup

```bash
# 1. Clone and switch to feature branch
git clone https://github.com/abdullahzunorain/text-book-AI-Humanoid-Rebotics-claude.git
cd text-book-AI-Humanoid-Rebotics-claude
git checkout 004-physical-ai-textbook

# 2. Backend setup
cd backend
cp .env.example .env   # Fill in all API keys and DATABASE_URL
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Run migrations
psql $DATABASE_URL -f migrations/001_create_auth_tables.sql
psql $DATABASE_URL -f migrations/002_add_cache_and_chat.sql

# 4. Index textbook content into Qdrant
python index_content.py

# 5. Start backend
uvicorn main:app --reload --port 8000

# 6. Frontend setup (new terminal)
cd ../website
npm install
npm start   # Opens http://localhost:3000
```

## Environment Variables (backend/.env)

```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
GOOGLE_API_KEY=your-gemini-key
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-key
JWT_SECRET=your-secret-key
APP_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

## Deployment

- **Frontend**: Push to `main` → GitHub Actions builds Docusaurus → deploys to GitHub Pages
- **Backend**: Push to `main` → Railway auto-deploys from Procfile (`uvicorn main:app`)
- **DB migrations**: Run manually via `psql` against Neon production DSN
- **Qdrant indexing**: Run `python index_content.py` manually when content changes
