# Implementation Plan: MVP2 — Complete Physical AI Textbook

**Branch**: `002-mvp2-complete-textbook` | **Date**: 2026-03-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-mvp2-complete-textbook/spec.md`

## Summary

Extend the Physical AI textbook from 1 module to 4 modules (12 new pages), add Urdu translation with RTL rendering, implement email/password authentication with JWT, build a learner background questionnaire persisted to Neon Postgres, deliver AI-powered chapter personalization, and create 4 Claude Code subagents for content creation workflows. Phased rollout: Content → Subagents → Translation → Auth → Personalization.

## Technical Context

**Language/Version**: Python 3.12+ (backend, uv), TypeScript/React 19 (frontend, Docusaurus 3.9.2)
**Primary Dependencies**: FastAPI, google-genai (gemini-2.5-flash, gemini-embedding-001), qdrant-client, asyncpg, python-jose[cryptography], passlib[bcrypt], better-auth (frontend)
**Storage**: Qdrant Cloud (vector search, existing), Neon Postgres (new: auth + user profiles)
**Testing**: pytest (backend contracts + unit), Docusaurus build verification (frontend)
**Target Platform**: GitHub Pages (static frontend), local/Railway (FastAPI backend)
**Project Type**: Web application (static site + API backend)
**Performance Goals**: Translation <3s p95, Personalization <5s p95, JWT validation <50ms, Pages <2s load
**Constraints**: HTTP-only cookies for JWT, bcrypt cost 12+, Gemini API free-tier budget
**Scale/Scope**: ~100 concurrent users, 18 chapter pages, 5 new API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | MVP-First (Minimal Scope) | ✅ PASS | MVP2 is the natural next increment. All 5 deliverables directly expand the textbook product. |
| II | No Auth, No Personalization, No Translation | ⚠️ VIOLATION — JUSTIFIED | Constitution v1.1.0 Principle II was scoped to MVP1 hackathon phase. MVP2 explicitly adds auth (P3), translation (P2), and personalization (P4) as the primary deliverables. **Amendment required: v1.1.0 → v2.0.0** to lift MVP1 scope freeze. User has explicitly requested these features. |
| III | Content Scope (Introduction + Module 1 Only) | ⚠️ VIOLATION — JUSTIFIED | MVP2 adds Modules 2, 3, 4 (12 new pages). This is the core P1 deliverable. Constitution scope limit was for hackathon MVP1 only. |
| IV | Chatbot Omnipresence | ✅ PASS | Existing chatbot widget unchanged. New content will be indexed into Qdrant for RAG. |
| V | Deployability & Demability | ✅ PASS | Each phase produces demoable output. Content pages → translation → auth → personalization are incrementally deployable. |
| VI | No Over-Engineering | ✅ PASS | Using existing stack (FastAPI, Gemini, Docusaurus). Adding Neon Postgres is the minimum viable database for auth. No custom frameworks, no new services beyond what spec requires. |
| — | Tech Stack Compliance | ✅ PASS | Python + TypeScript, Docusaurus 3.x, FastAPI, LLM RAG — all compliant with constitution requirements. |
| — | Testing Standards | ✅ PASS | Contract tests, unit tests, build verification all planned per constitution. |
| — | Code Standards | ✅ PASS | Conventional commits, no hardcoded secrets, .env config, OpenAPI docs. |
| — | <3 New Services | ✅ PASS | Adding 1 new service (Neon Postgres). Total: Qdrant + Neon = 2 external services. |

**Gate Resolution**: Principles II and III have justified violations. Constitutional amendment v2.0.0 is required before implementation begins. The amendment lifts the MVP1 scope freeze while preserving all quality/testing/deployment standards.

**Pre-Design Gate**: ✅ PASSED (with noted amendments)

## Project Structure

### Documentation (this feature)

```text
specs/002-mvp2-complete-textbook/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── translate.md
│   ├── auth.md
│   ├── background.md
│   └── personalize.md
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py                     # FastAPI app (MODIFY: register new routers)
├── rag_service.py              # Existing RAG pipeline (unchanged)
├── index_content.py            # Content indexer (MODIFY: handle new modules)
├── db.py                       # NEW: asyncpg connection pool for Neon Postgres
├── auth_utils.py               # NEW: JWT create/verify, password hash/check
├── routes/
│   ├── translate.py            # NEW: POST /api/translate
│   ├── auth.py                 # NEW: POST /api/auth/signup, /api/auth/signin
│   └── personalize.py          # NEW: POST /api/personalize, POST /api/user/background
├── services/
│   ├── translation_service.py  # NEW: Gemini translation with code-block preservation
│   └── personalization_service.py # NEW: Gemini personalization with user profile
├── migrations/
│   └── 001_create_auth_tables.sql # NEW: users + user_backgrounds DDL
├── tests/
│   ├── test_chat_api.py        # Existing (6 tests)
│   ├── test_translate_api.py   # NEW: translation endpoint contracts
│   ├── test_auth_api.py        # NEW: signup/signin endpoint contracts
│   ├── test_personalize_api.py # NEW: personalization endpoint contracts
│   └── test_content_pages.py   # NEW: validate chapter word count, code blocks
├── pyproject.toml              # MODIFY: add asyncpg, python-jose, passlib
└── requirements.txt            # MODIFY: add new dependencies

website/
├── docs/
│   ├── intro/                  # Existing (unchanged)
│   ├── module1-ros2/           # Existing (unchanged)
│   ├── module2-simulation/     # NEW: 4 Gazebo/Unity chapters
│   │   ├── chapter1-gazebo-basics.md
│   │   ├── chapter2-gazebo-ros2-integration.md
│   │   ├── chapter3-unity-robotics.md
│   │   └── chapter4-unity-ml-agents.md
│   ├── module3-isaac/          # NEW: 4 NVIDIA Isaac chapters
│   │   ├── chapter1-isaac-sim-intro.md
│   │   ├── chapter2-isaac-gym.md
│   │   ├── chapter3-isaac-ros2-bridge.md
│   │   └── chapter4-isaac-reinforcement-learning.md
│   └── module4-vla/            # NEW: 4 VLA chapters
│       ├── chapter1-vla-intro.md
│       ├── chapter2-multimodal-models.md
│       ├── chapter3-action-chunking.md
│       └── chapter4-vla-robotics.md
├── sidebars.ts                 # MODIFY: add Module 2, 3, 4
├── docusaurus.config.ts        # MODIFY: add auth API URL customField
├── src/
│   ├── components/
│   │   ├── ChatbotWidget.tsx           # Existing (unchanged)
│   │   ├── SelectedTextHandler.tsx     # Existing (unchanged)
│   │   ├── UrduTranslateButton.tsx     # NEW: "اردو میں پڑھیں" toggle
│   │   ├── UrduContent.tsx             # NEW: RTL rendered translated content
│   │   ├── PersonalizeButton.tsx       # NEW: "Personalize This Chapter" (auth-gated)
│   │   ├── PersonalizedContent.tsx     # NEW: rendered personalized markdown
│   │   ├── AuthModal.tsx               # NEW: signup/signin modal
│   │   ├── AuthButton.tsx              # NEW: navbar auth trigger
│   │   ├── BackgroundQuestionnaire.tsx # NEW: 5-question post-signup form
│   │   └── AuthProvider.tsx            # NEW: React context for auth state
│   ├── css/
│   │   ├── chatbot.css                 # Existing (unchanged)
│   │   ├── urdu-rtl.css                # NEW: RTL styles, Noto Nastaliq Urdu font
│   │   └── auth-modal.css              # NEW: modal + questionnaire styles
│   └── theme/
│       └── DocItem/Layout/index.tsx    # MODIFY: inject UrduTranslateButton + PersonalizeButton

.claude/agents/                         # NEW: 4 Claude Code subagent definitions
├── content-writer.md
├── code-example-generator.md
├── urdu-translator.md
└── content-personalizer.md
```

**Structure Decision**: Extending the existing 2-project layout (backend/ + website/). New backend modules organized into routes/, services/, migrations/ subdirectories to handle the increased complexity while keeping the flat-file structure for existing code. Frontend adds components and CSS files following existing patterns.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Constitution Principle II (auth/personalization/translation) | These are the explicit MVP2 deliverables requested by user. They are the product's growth features. | Keeping MVP1 scope would mean no product evolution. Auth enables personalization which is the key differentiator. |
| Constitution Principle III (content scope) | User explicitly requires 3 new modules (12 chapters). Complete textbook is the primary value proposition. | Shipping with only Module 1 limits educational value. Modules 2-4 cover the remaining curriculum. |
| Adding Neon Postgres (new external service) | Auth requires persistent user accounts + background profiles. Qdrant is vector-only, cannot store relational user data. | SQLite rejected because Railway/serverless needs managed DB. In-memory rejected because data must persist across restarts. |
