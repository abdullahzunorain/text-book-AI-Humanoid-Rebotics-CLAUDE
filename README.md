# Physical AI & Humanoid Robotics Textbook

An interactive online textbook covering Physical AI, ROS 2, and humanoid robotics — with an embedded RAG-powered AI study companion chatbot.

**Live Site**: [https://abdullahzunorain.github.io/Hack-I-Copilot/](https://abdullahzunorain.github.io/Hack-I-Copilot/)

## Features

- **7-page textbook** covering Introduction to Physical AI and Module 1: ROS 2 Fundamentals
- **AI Chatbot** on every page — ask questions about the textbook content
- **Selected-text queries** — highlight any passage and ask the AI to explain it
- **Dark/light mode** with system preference detection
- **Mobile responsive** design

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Docusaurus 3, React 18, TypeScript |
| Backend | FastAPI, Python 3.11+ |
| AI Model | Gemini 2.0 Flash (via OpenAI SDK) |
| Embeddings | text-embedding-004 (768 dims) |
| Vector DB | Qdrant Cloud (free tier) |
| Frontend Hosting | GitHub Pages |
| Backend Hosting | Railway |

## Quickstart

### Prerequisites

- Node.js 18+
- Python 3.11+
- npm

### 1. Clone & Install

```bash
git clone https://github.com/abdullahzunorain/Hack-I-Copilot.git
cd Hack-I-Copilot

# Frontend
cd website
npm install
cd ..

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys:
#   GEMINI_API_KEY=<your Google AI Studio key>
#   QDRANT_URL=<your Qdrant Cloud URL>
#   QDRANT_API_KEY=<your Qdrant API key>

# Frontend
cp website/.env.example website/.env
# Edit website/.env:
#   REACT_APP_API_URL=http://localhost:8000
```

### 3. Index Content

```bash
cd backend
python index_content.py
cd ..
```

### 4. Run Locally

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd website
npm run start
```

Visit [http://localhost:3000](http://localhost:3000) to see the textbook.

### 5. Deploy

- **Frontend (GitHub Pages)**: Push to `main` branch — GitHub Actions auto-deploys
- **Backend (Railway)**: Connect repo, set root directory to `backend/`, add env vars

## Project Structure

```
website/                    # Docusaurus 3 frontend
├── docs/                   # Textbook content (Markdown/MDX)
├── src/components/         # ChatbotWidget, SelectedTextHandler
├── src/theme/              # Swizzled DocItem wrapper
└── docusaurus.config.ts    # Site configuration

backend/                    # FastAPI backend
├── main.py                 # API endpoint (POST /api/chat)
├── rag_service.py          # RAG pipeline (embed → retrieve → generate)
├── index_content.py        # Markdown chunking & Qdrant indexing
└── tests/                  # Contract tests
```

## License

MIT
