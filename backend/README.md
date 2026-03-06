# Physical AI Textbook — Backend API

FastAPI backend for the Physical AI & Humanoid Robotics textbook platform.

## Features

- **RAG Chatbot** — Ask questions, get answers sourced from textbook content
- **Multi-model LLM failover** — Gemini 2.5 Flash → Groq (Llama 3.3 70B) → OpenAI (GPT-4o-mini)
- **Urdu Translation** — Translate chapters with code-block preservation
- **Content Personalization** — Adapt chapters to learner background
- **DB-backed caching** — Personalization and translation results cached per user
- **Chat History** — Persistent Q&A history for authenticated users
- **JWT Auth** — httpOnly cookie-based authentication

## Quick Start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env

# Run migrations
psql "$DATABASE_URL" -f migrations/001_create_users.sql
psql "$DATABASE_URL" -f migrations/002_add_cache_and_chat.sql

# Index textbook content into Qdrant
python index_content.py

# Start development server
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/api/chat` | Optional | RAG chatbot (saves history if authenticated) |
| GET | `/api/chat/history` | Yes | Paginated chat history |
| POST | `/api/translate` | Yes | Translate chapter to Urdu |
| POST | `/api/personalize` | Yes | Personalize chapter content |
| POST | `/api/auth/signup` | No | Create account |
| POST | `/api/auth/signin` | No | Sign in |
| POST | `/api/auth/signout` | No | Sign out (clears cookie) |
| GET | `/api/auth/me` | Yes | Current user info |
| POST | `/api/user/background` | Yes | Save learning background |

## Environment Variables

See [.env.example](.env.example) for all required and optional variables.

**Required:**
- `GEMINI_API_KEY` / `GOOGLE_API_KEY` — Google AI Studio API key
- `GROQ_API_KEY` — Groq API key (failover)
- `OPENAI_API_KEY` — OpenAI API key (failover)
- `QDRANT_URL` / `QDRANT_API_KEY` — Qdrant Cloud credentials
- `DATABASE_URL` — Neon PostgreSQL connection string
- `JWT_SECRET` — Secret for JWT token signing

## Testing

```bash
cd backend
.venv/bin/python -m pytest tests/ -v
```

119 tests covering auth, chat, translation, personalization, caching, and LLM failover.

## Architecture

- **LLM Client** (`services/llm_client.py`) — Chain-of-responsibility failover with exponential backoff
- **Cache Service** (`services/cache_service.py`) — DB-backed content cache (personalization + translation)
- **Chat History** (`services/chat_history_service.py`) — Persistent Q&A storage
- **RAG Service** (`rag_service.py`) — Embed → Retrieve from Qdrant → Generate via LLMClient
