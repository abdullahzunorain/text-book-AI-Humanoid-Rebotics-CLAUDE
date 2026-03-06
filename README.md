<div align="center">

# 📖 Physical AI & Humanoid Robotics — Interactive Textbook

**An AI-powered, interactive textbook for learning Physical AI, ROS 2, simulation, and humanoid robotics.**

[![Live Site](https://img.shields.io/badge/Live%20Site-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://abdullahzunorain.github.io/text-book-AI-Humanoid-Rebotics-claude/)
[![Backend](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## What Is This?

This is a full-stack, AI-enhanced interactive textbook that teaches **Physical AI and Humanoid Robotics**. It covers everything from ROS 2 fundamentals to simulation environments (Gazebo, Unity), NVIDIA Isaac, and Vision-Language-Action (VLA) models.

What makes it special? Every page comes with:

- An **AI study companion chatbot** that answers questions using only the textbook content (RAG-powered, so answers are grounded and accurate)
- **Highlight-and-ask** — select any text on a page, and instantly ask the AI about it
- **Urdu translation** — read any chapter in Urdu with a single click (اردو میں پڑھیں)
- **Personalized learning** — the AI adapts chapter content to your skill level (beginner, intermediate, or advanced)

It's free, open-source, and designed for students, hobbyists, and professionals who want to learn robotics with AI assistance.

---

## Features

### 📚 Comprehensive Textbook Content

The textbook is organized into **5 sections with 18 chapters**:

| Module | Topics | Chapters |
|--------|--------|----------|
| **Introduction** | What is Physical AI, sensor systems, ROS ecosystem | 1 |
| **Module 1: ROS 2** | Architecture, nodes/topics/services, Python packages, launch files, URDF | 5 |
| **Module 2: Simulation** | Gazebo basics, Gazebo–ROS 2 integration, Unity Robotics, ML-Agents | 4 |
| **Module 3: NVIDIA Isaac** | Isaac Sim, Isaac Gym, ROS 2 bridge, reinforcement learning | 4 |
| **Module 4: VLA Models** | VLA introduction, multimodal models, action chunking, VLA in robotics | 4 |

### 🤖 AI Study Companion (RAG Chatbot)

A chatbot widget appears on **every page** of the textbook:

- Ask any question about the textbook content
- The AI retrieves relevant passages from the textbook and generates an accurate answer
- Answers include source references so you can verify information
- Chat history is saved for signed-in users
- Press `Escape` to close the chatbot panel

### ✍️ Highlight-and-Ask

1. **Select (highlight)** any text on a textbook page
2. A small **"Ask AI about this"** popup appears above your selection
3. Click it — the chatbot opens with that passage as context
4. Type your question — the AI will answer specifically about the highlighted text

### 🌐 Urdu Translation (اردو ترجمہ)

Signed-in users can read any chapter in Urdu:

1. Click **"اردو میں پڑھیں"** (Read in Urdu) at the top of any chapter
2. The entire page is translated to formal Urdu while keeping:
   - All **code blocks** exactly as they are (untranslated)
   - All **technical terms** in English (ROS 2, Gazebo, Python, URDF, etc.)
   - All **markdown formatting** — headers, tables, lists, bold, links
3. Click **"Read in English"** to switch back

Translations are cached — the second time you visit, it loads instantly.

### 🎯 Personalized Learning

After signing in, a brief questionnaire asks about your:

- **Python level** — Beginner / Intermediate / Advanced
- **Robotics experience** — None / Hobbyist / Student / Professional
- **Math level** — High School / Undergraduate / Graduate
- **Hardware access** — Whether you have access to physical robots
- **Learning goal** — What you want to achieve (free-text)

Then on any chapter page, click **"🎯 Personalize This Chapter"** — the AI rewrites the chapter prose to match your level. A beginner gets simpler explanations; an advanced user gets technical depth. Code blocks are preserved unchanged.

### 🔐 User Authentication

- **Sign up** with email and password (passwords are hashed with bcrypt)
- **Sign in** to access personalization, translation, and chat history
- **JWT tokens** stored in secure httpOnly cookies (never exposed to JavaScript)
- No authentication required to read the textbook or use the chatbot

### 🌙 Dark / Light Mode

The site automatically uses your system preference. You can also toggle manually via the navbar switch.

### 📱 Mobile Responsive

The textbook, chatbot, and all features work on mobile, tablet, and desktop.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Docusaurus 3.9, React 19, TypeScript | Static site generation, textbook rendering |
| **Backend** | FastAPI 0.115, Python 3.13, Uvicorn | REST API for AI features |
| **AI Orchestration** | OpenAI Agents SDK (`openai-agents`) | Agent management for chatbot, translation, personalization |
| **LLM** | Gemini 2.5 Flash (via OpenAI-compatible endpoint) | Text generation, translation, personalization |
| **Embeddings** | `gemini-embedding-001` (3072 dims) | Semantic search for RAG chatbot |
| **Vector Database** | Qdrant Cloud | Stores and searches textbook content embeddings |
| **Relational Database** | Neon PostgreSQL (asyncpg) | Users, backgrounds, chat history, content cache |
| **Auth** | bcrypt + JWT (HS256, 7-day expiry) | Secure authentication via httpOnly cookies |
| **Frontend Hosting** | GitHub Pages | Free static site hosting with CI/CD |
| **Backend Hosting** | Render / Railway | Python web service hosting |

---

## Getting Started (Step by Step)

### Prerequisites

Before you begin, make sure you have these installed:

| Tool | Required Version | How to Check | Install Guide |
|------|-----------------|-------------|--------------|
| **Node.js** | 20 or higher | `node --version` | [nodejs.org](https://nodejs.org/) |
| **npm** | Comes with Node.js | `npm --version` | Included with Node.js |
| **Python** | 3.11 or higher | `python --version` | [python.org](https://www.python.org/downloads/) |
| **Git** | Any recent version | `git --version` | [git-scm.com](https://git-scm.com/) |

You'll also need free accounts for:

| Service | What For | Free Tier? | Sign Up |
|---------|---------|-----------|---------|
| **Google AI Studio** | Gemini API key (LLM + embeddings) | ✅ Yes | [aistudio.google.com](https://aistudio.google.com/) |
| **Qdrant Cloud** | Vector database for chatbot search | ✅ Yes (1 GB) | [cloud.qdrant.io](https://cloud.qdrant.io/) |
| **Neon** | PostgreSQL database for users/cache | ✅ Yes | [neon.tech](https://neon.tech/) |

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/abdullahzunorain/text-book-AI-Humanoid-Rebotics-claude.git
cd text-book-AI-Humanoid-Rebotics-claude
```

---

### Step 2: Set Up the Backend

```bash
cd backend

# Create a Python virtual environment
python -m venv .venv

# Activate it
# Linux / macOS:
source .venv/bin/activate
# Windows (Command Prompt):
.venv\Scripts\activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Configure Backend Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Now open `backend/.env` in a text editor and fill in your keys:

```dotenv
# Google Gemini — get your key from https://aistudio.google.com/apikey
GOOGLE_API_KEY=your-google-api-key-here

# Qdrant Cloud — get from https://cloud.qdrant.io → Clusters → API Keys
QDRANT_URL=https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here

# Neon Postgres — get from https://console.neon.tech → Connection Details
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# App settings
APP_ENV=development
JWT_SECRET=pick-any-random-string-at-least-32-characters
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

> **Tip**: You can generate a random JWT secret by running:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

### Step 4: Set Up the Database

Run the SQL migrations against your Neon database to create the required tables:

```bash
# Option A: Using psql (if installed)
psql "$DATABASE_URL" -f migrations/001_create_auth_tables.sql
psql "$DATABASE_URL" -f migrations/002_add_cache_and_chat.sql

# Option B: Copy-paste the SQL into Neon's web console (SQL Editor)
# Files are in: backend/migrations/
```

This creates 4 tables:
- `users` — email and hashed password
- `user_backgrounds` — learning profile (Python level, robotics experience, etc.)
- `content_cache` — cached personalized/translated content
- `chat_messages` — persistent chat history

---

### Step 5: Index the Textbook Content

This step reads all the textbook Markdown files, splits them into chunks, creates embeddings via Gemini, and uploads them to your Qdrant collection:

```bash
# Make sure you're in the backend/ directory with your .venv activated
python index_content.py
```

This takes about 1–2 minutes. You'll see progress output as each chapter is indexed.

> **Note**: You only need to run this once (or again if you add/change textbook content).

---

### Step 6: Set Up the Frontend

```bash
# Go back to the project root
cd ..

# Go to the website directory
cd website

# Install Node.js dependencies
npm install
```

Configure the frontend environment:

```bash
cp .env.example .env
```

Open `website/.env` and set:

```dotenv
REACT_APP_API_URL=http://localhost:8000
```

---

### Step 7: Start the Application

You need **two terminal windows** running at the same time:

**Terminal 1 — Backend API:**

```bash
cd backend
source .venv/bin/activate    # activate your Python environment
uvicorn main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Terminal 2 — Frontend website:**

```bash
cd website
npm run start
```

You should see:

```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

---

### Step 8: Open and Use the Textbook

1. Open your browser and go to **http://localhost:3000/text-book-AI-Humanoid-Rebotics-claude/**
2. You'll see the textbook landing page — click **"Textbook"** in the navbar to start reading
3. The **chatbot widget** (floating button in the bottom-right) is available on every page — click it and start asking questions!

**To use premium features** (translation, personalization, chat history):
1. Click **"Sign In"** in the top-right navbar
2. Create an account (email + password, minimum 8 characters)
3. Fill in the **learning profile questionnaire** that appears
4. Now you can:
   - Click **"اردو میں پڑھیں"** to read in Urdu
   - Click **"🎯 Personalize This Chapter"** to get content adapted to your level
   - Your chat history is automatically saved

---

## API Reference

The backend exposes these endpoints:

| Method | Endpoint | Auth? | Description |
|--------|----------|-------|-------------|
| `GET` | `/` | No | API info and available endpoints |
| `GET` | `/health` | No | Health check |
| `POST` | `/api/chat` | Optional | Ask a question (RAG chatbot) |
| `GET` | `/api/chat/history` | Required | Get paginated chat history |
| `POST` | `/api/translate` | Required | Translate a chapter to Urdu |
| `POST` | `/api/personalize` | Required | Personalize a chapter |
| `POST` | `/api/auth/signup` | No | Create an account |
| `POST` | `/api/auth/signin` | No | Sign in |
| `POST` | `/api/auth/signout` | No | Sign out (clears cookie) |
| `GET` | `/api/auth/me` | Required | Get current user info |
| `POST` | `/api/user/background` | Required | Save learning profile |

**Interactive API docs** are auto-generated at: `http://localhost:8000/docs` (Swagger UI)

---

## Running Tests

The backend has **112+ tests** covering all API endpoints, services, and edge cases:

```bash
cd backend
source .venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_chat_api.py -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing
```

---

## Deployment

### Frontend (GitHub Pages)

The frontend auto-deploys to GitHub Pages on every push to `main`:

1. Push your code to the `main` branch
2. GitHub Actions (`.github/workflows/deploy.yml`) builds the site and deploys it
3. Set the `API_URL` repository variable in GitHub → Settings → Variables to point to your deployed backend URL

### Backend (Render)

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repository
3. Set **Root Directory** to `backend`
4. Set **Build Command** to `pip install -r requirements.txt`
5. Set **Start Command** to `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables: `GOOGLE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `APP_ENV=production`

A `render.yaml` is included for one-click Render deployment.

---

## Project Structure

```
├── website/                          # Docusaurus 3 frontend
│   ├── docs/                         # Textbook content (Markdown)
│   │   ├── intro/                    #   Introduction (1 chapter)
│   │   ├── module1-ros2/             #   ROS 2 Fundamentals (5 chapters)
│   │   ├── module2-simulation/       #   Simulation Environments (4 chapters)
│   │   ├── module3-isaac/            #   NVIDIA Isaac (4 chapters)
│   │   └── module4-vla/              #   VLA Models (4 chapters)
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── ChatbotWidget.tsx      #   AI chatbot floating widget
│   │   │   ├── SelectedTextHandler.tsx #  Highlight-and-ask popup
│   │   │   ├── UrduTranslateButton.tsx #  Urdu translation toggle
│   │   │   ├── UrduContent.tsx        #   RTL Urdu content renderer
│   │   │   ├── PersonalizeButton.tsx  #   Personalization toggle
│   │   │   ├── PersonalizedContent.tsx #  Personalized content renderer
│   │   │   ├── AuthButton.tsx         #   Sign In / Sign Out navbar button
│   │   │   ├── AuthModal.tsx          #   Sign In / Sign Up modal dialog
│   │   │   ├── AuthProvider.tsx       #   React context for auth state
│   │   │   └── BackgroundQuestionnaire.tsx # Learning profile form
│   │   ├── theme/                     # Swizzled Docusaurus theme
│   │   │   ├── DocItem/Layout/        #   Wraps every doc page with AI buttons
│   │   │   ├── Navbar/                #   Custom navbar with auth button
│   │   │   └── Root.tsx               #   Root wrapper with AuthProvider
│   │   └── css/                       # Global styles + RTL support
│   ├── docusaurus.config.ts           # Site configuration
│   └── package.json                   # Node.js dependencies
│
├── backend/                           # FastAPI backend
│   ├── main.py                        # App entry point, CORS, /api/chat endpoint
│   ├── rag_service.py                 # RAG pipeline: embed → retrieve → generate
│   ├── index_content.py               # Textbook indexing script (Markdown → Qdrant)
│   ├── auth_utils.py                  # bcrypt hashing + JWT token management
│   ├── cookie_config.py               # Environment-aware cookie settings
│   ├── db.py                          # asyncpg connection pool for Neon Postgres
│   ├── services/
│   │   ├── agent_config.py            # OpenAI Agents SDK setup (3 agents + Gemini)
│   │   ├── translation_service.py     # English → Urdu translation with code preservation
│   │   ├── personalization_service.py # Chapter content adaptation by user profile
│   │   ├── cache_service.py           # DB-backed content cache (translation/personalization)
│   │   └── chat_history_service.py    # Chat message persistence
│   ├── routes/
│   │   ├── auth.py                    # /api/auth/* endpoints (signup, signin, signout, me)
│   │   ├── chat.py                    # /api/chat/history endpoint
│   │   ├── translate.py               # /api/translate endpoint
│   │   └── personalize.py            # /api/personalize endpoint
│   ├── migrations/                    # SQL migration files
│   │   ├── 001_create_auth_tables.sql #   users + user_backgrounds tables
│   │   └── 002_add_cache_and_chat.sql #   content_cache + chat_messages tables
│   ├── tests/                         # 112+ pytest tests
│   ├── requirements.txt               # Python dependencies
│   └── .env.example                   # Environment variable template
│
├── .github/
│   └── workflows/
│       └── deploy.yml                 # GitHub Actions: build & deploy frontend
├── render.yaml                        # Render.com backend deployment config
├── .gitignore
└── README.md                          # You are here
```

---

## How It Works (Architecture Overview)

```
┌──────────────────────────────────────────────────┐
│                   User's Browser                  │
│                                                   │
│  Docusaurus Site ─── ChatbotWidget ── Ask AI     │
│       │               SelectedTextHandler         │
│       │               UrduTranslateButton         │
│       │               PersonalizeButton           │
│       │               AuthButton / AuthModal      │
└───────┼───────────────────────────────────────────┘
        │ HTTPS (fetch with credentials: 'include')
        ▼
┌──────────────────────────────────────────────────┐
│              FastAPI Backend (Python)              │
│                                                   │
│  POST /api/chat ──► RAG Service                  │
│    │                  ├── Embed question (Gemini) │
│    │                  ├── Search Qdrant           │
│    │                  └── Generate (Tutor Agent)  │
│    │                                              │
│  POST /api/translate ──► Translation Service     │
│    │                      ├── Extract code blocks │
│    │                      ├── Strip frontmatter   │
│    │                      ├── Translate (Agent)   │
│    │                      └── Re-insert code      │
│    │                                              │
│  POST /api/personalize ──► Personalization Svc   │
│    │                        ├── Load user profile │
│    │                        ├── Adapt (Agent)     │
│    │                        └── Cache result      │
│    │                                              │
│  Auth routes ──► bcrypt + JWT httpOnly cookies    │
└───────┼────────────┼──────────────────────────────┘
        │            │
        ▼            ▼
┌──────────┐  ┌─────────────┐  ┌──────────────────┐
│  Qdrant  │  │ Neon Postgres│  │ Gemini 2.5 Flash │
│ (vectors)│  │ (users/cache)│  │ (via OpenAI SDK) │
└──────────┘  └─────────────┘  └──────────────────┘
```

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `GOOGLE_API_KEY is not set` warning | Make sure `backend/.env` exists and has your Google AI Studio key |
| `Database pool not initialized` error | Check your `DATABASE_URL` in `.env` — it must be a valid Neon Postgres connection string |
| Chatbot returns "Service temporarily unavailable" | Your Gemini API key may have hit rate limits — wait a minute and try again |
| Frontend shows blank page | Check that `REACT_APP_API_URL` in `website/.env` matches your backend URL |
| `npm run start` fails | Make sure you've run `npm install` in the `website/` directory first, and you're using Node.js 20+ |
| Translation shows raw markdown | Clear the cache by clicking the translate button again (it sends `force_refresh`) |
| Sign-in button not visible on mobile | The auth button is pinned outside the hamburger menu — check if custom CSS imported correctly |
| `ModuleNotFoundError` in backend | Make sure your virtual environment is activated (`source .venv/bin/activate`) |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests (`cd backend && python -m pytest tests/ -v`)
5. Commit with conventional format (`feat: add new chapter`, `fix: chatbot error handling`)
6. Open a Pull Request

---

## License

MIT
