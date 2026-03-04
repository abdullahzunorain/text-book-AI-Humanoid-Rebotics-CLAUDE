# Tasks: MVP2 — Complete Physical AI Textbook

**Feature**: `002-mvp2-complete-textbook`
**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/)
**TDD**: Yes — test files created before implementation for all backend logic and endpoints
**Linting**: All Python must pass `ruff check`, all Python must use type hints, all TypeScript strict mode

---

## Phase A: Content (P1 — US1)

**Goal**: Add 12 new chapter pages across 3 modules (Gazebo/Unity, NVIDIA Isaac, VLA)

**Independent Test**: Navigate to each of 18 total pages, verify ≥600 words, ≥2 code blocks, Learning Objectives, Key Takeaways

### A1 — Create Module 2 Chapter 1: Gazebo Basics

- **ID**: A1
- **Title**: Create Gazebo Basics chapter page
- **Files Affected**:
  - CREATE `website/docs/module2-simulation/chapter1-gazebo-basics.md`
  - CREATE `website/docs/module2-simulation/_category_.json`
- **Acceptance Criteria**:
  - [X] File exists at exact path with valid Docusaurus frontmatter (title, sidebar_position: 1)
  - [X] Contains ≥600 words of educational prose on Gazebo simulator fundamentals
  - [X] Contains ≥2 Python/Bash code examples with syntax highlighting
  - [X] Starts with "## Learning Objectives" section (≥3 bullet points)
  - [X] Ends with "## Key Takeaways" section (≥3 bullet points)

### A2 — Create Module 2 Chapter 2: Gazebo ROS 2 Integration

- **ID**: A2
- **Title**: Create Gazebo ROS 2 Integration chapter page
- **Files Affected**:
  - CREATE `website/docs/module2-simulation/chapter2-gazebo-ros2-integration.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 2)
  - [X] Contains ≥600 words on integrating Gazebo with ROS 2 launch files and plugins
  - [X] Contains ≥2 code examples (Python/YAML/Bash)
  - [X] Has Learning Objectives and Key Takeaways sections

### A3 — Create Module 2 Chapter 3: Unity Robotics

- **ID**: A3
- **Title**: Create Unity Robotics chapter page
- **Files Affected**:
  - CREATE `website/docs/module2-simulation/chapter3-unity-robotics.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 3)
  - [X] Contains ≥600 words on Unity Robotics Hub and URDF import
  - [X] Contains ≥2 code examples (C#/Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A4 — Create Module 2 Chapter 4: Unity ML-Agents

- **ID**: A4
- **Title**: Create Unity ML-Agents chapter page
- **Files Affected**:
  - CREATE `website/docs/module2-simulation/chapter4-unity-ml-agents.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 4)
  - [X] Contains ≥600 words on Unity ML-Agents for robot training
  - [X] Contains ≥2 code examples (Python/YAML)
  - [X] Has Learning Objectives and Key Takeaways sections

### A5 — Create Module 3 Chapter 1: Isaac Sim Intro

- **ID**: A5
- **Title**: Create Isaac Sim Introduction chapter page
- **Files Affected**:
  - CREATE `website/docs/module3-isaac/chapter1-isaac-sim-intro.md`
  - CREATE `website/docs/module3-isaac/_category_.json`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 1)
  - [X] Contains ≥600 words on NVIDIA Isaac Sim architecture and setup
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A6 — Create Module 3 Chapter 2: Isaac Gym

- **ID**: A6
- **Title**: Create Isaac Gym chapter page
- **Files Affected**:
  - CREATE `website/docs/module3-isaac/chapter2-isaac-gym.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 2)
  - [X] Contains ≥600 words on Isaac Gym for RL-based robot training
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A7 — Create Module 3 Chapter 3: Isaac ROS 2 Bridge

- **ID**: A7
- **Title**: Create Isaac ROS 2 Bridge chapter page
- **Files Affected**:
  - CREATE `website/docs/module3-isaac/chapter3-isaac-ros2-bridge.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 3)
  - [X] Contains ≥600 words on bridging Isaac Sim with ROS 2
  - [X] Contains ≥2 code examples (Python/Bash)
  - [X] Has Learning Objectives and Key Takeaways sections

### A8 — Create Module 3 Chapter 4: Isaac Reinforcement Learning

- **ID**: A8
- **Title**: Create Isaac Reinforcement Learning chapter page
- **Files Affected**:
  - CREATE `website/docs/module3-isaac/chapter4-isaac-reinforcement-learning.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 4)
  - [X] Contains ≥600 words on RL policies in Isaac Gym/Sim
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A9 — Create Module 4 Chapter 1: VLA Introduction

- **ID**: A9
- **Title**: Create VLA Introduction chapter page
- **Files Affected**:
  - CREATE `website/docs/module4-vla/chapter1-vla-intro.md`
  - CREATE `website/docs/module4-vla/_category_.json`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 1)
  - [X] Contains ≥600 words on Vision-Language-Action model fundamentals
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A10 — Create Module 4 Chapter 2: Multimodal Models

- **ID**: A10
- **Title**: Create Multimodal Models chapter page
- **Files Affected**:
  - CREATE `website/docs/module4-vla/chapter2-multimodal-models.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 2)
  - [X] Contains ≥600 words on multimodal architectures (CLIP, Flamingo, PaLM-E)
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A11 — Create Module 4 Chapter 3: Action Chunking

- **ID**: A11
- **Title**: Create Action Chunking chapter page
- **Files Affected**:
  - CREATE `website/docs/module4-vla/chapter3-action-chunking.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 3)
  - [X] Contains ≥600 words on action chunking transformers (ACT)
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A12 — Create Module 4 Chapter 4: VLA in Robotics

- **ID**: A12
- **Title**: Create VLA in Robotics chapter page
- **Files Affected**:
  - CREATE `website/docs/module4-vla/chapter4-vla-robotics.md`
- **Acceptance Criteria**:
  - [X] File exists with valid frontmatter (sidebar_position: 4)
  - [X] Contains ≥600 words on deploying VLA models on physical robots
  - [X] Contains ≥2 code examples (Python)
  - [X] Has Learning Objectives and Key Takeaways sections

### A13 — Update Sidebar + Qdrant Re-index

- **ID**: A13
- **Title**: Update sidebar navigation and re-index content into Qdrant
- **Dependencies**: A1–A12
- **Files Affected**:
  - MODIFY `website/sidebars.ts` — add Module 2, Module 3, Module 4 category entries
  - MODIFY `backend/index_content.py` — ensure new module paths are scanned
- **Acceptance Criteria**:
  - [X] `website/sidebars.ts` includes all 3 new module categories with correct chapter ordering
  - [X] `_category_.json` files exist in `module2-simulation/`, `module3-isaac/`, `module4-vla/` with correct label and position
  - [X] `npm run build` in `website/` succeeds with zero errors
  - [ ] Running `backend/index_content.py` inserts new chapter embeddings into Qdrant `book_content` collection

**Checkpoint**: All 18 pages navigable, build passes, Qdrant has embeddings for all content

---

## Phase B: Subagents (P5 — US5)

**Goal**: Create 4 Claude Code subagent definitions for content creation workflows

**Independent Test**: Invoke each subagent in VS Code with Claude Code, verify structured output

### B1 — Create content-writer Subagent

- **ID**: B1
- **Title**: Create content-writer subagent definition
- **Files Affected**:
  - CREATE `.claude/agents/content-writer.md`
- **Acceptance Criteria**:
  - [X] File defines Role, Input Schema (module name + chapter topic), Output Schema (complete .md with frontmatter)
  - [X] Constraints specify ≥600 words, ≥2 code examples, Learning Objectives, Key Takeaways
  - [X] Includes at least 1 example invocation and expected output snippet

### B2 — Create code-example-generator Subagent

- **ID**: B2
- **Title**: Create code-example-generator subagent definition
- **Files Affected**:
  - CREATE `.claude/agents/code-example-generator.md`
- **Acceptance Criteria**:
  - [X] File defines Role, Input Schema (topic + target framework), Output Schema (fenced code blocks with comments)
  - [X] Constraints specify PEP 8 compliance, expected output comments, error handling
  - [X] Includes at least 1 example invocation and expected output snippet

### B3 — Create urdu-translator Subagent

- **ID**: B3
- **Title**: Create urdu-translator subagent definition
- **Files Affected**:
  - CREATE `.claude/agents/urdu-translator.md`
- **Acceptance Criteria**:
  - [X] File defines Role, Input Schema (English markdown text), Output Schema (Urdu markdown)
  - [X] Constraints specify: ALL code blocks remain in English, technical terms stay in English, markdown formatting preserved
  - [X] Includes at least 1 example with code block preservation demonstrated

### B4 — Create content-personalizer Subagent

- **ID**: B4
- **Title**: Create content-personalizer subagent definition
- **Files Affected**:
  - CREATE `.claude/agents/content-personalizer.md`
- **Acceptance Criteria**:
  - [X] File defines Role, Input Schema (chapter markdown + 5 user profile fields), Output Schema (personalized markdown)
  - [X] Constraints specify: code examples unchanged, prose-only adaptation, profile-keyed rules
  - [X] Includes at least 1 example with beginner vs advanced adaptation shown

**Checkpoint**: All 4 subagent files exist in `.claude/agents/`, each with Role/Input/Output/Constraints/Example

---

## Phase C: Urdu Translation (P2 — US2)

**Goal**: Add Urdu translation button to every chapter with RTL rendering and rate limiting

**Independent Test**: Click "اردو میں پڑھیں" on any chapter, verify Urdu prose loads in RTL, code blocks stay English, toggle back works

### C1 — TDD: Create translation service unit tests

- **ID**: C1
- **Title**: Create translation service unit tests (TDD — write first, must fail)
- **Files Affected**:
  - CREATE `backend/tests/test_translation_service.py`
- **Acceptance Criteria**:
  - [X] Tests cover: `extract_code_blocks()` returns correct placeholder prose + block list
  - [X] Tests cover: `translate_to_urdu()` returns `translated_content` string and `original_code_blocks` list
  - [X] Tests cover: code block re-insertion after translation preserves original blocks
  - [X] All tests use type hints, pass `ruff check`
  - [X] Tests FAIL when run (no implementation yet)

### C2 — Implement translation service

- **ID**: C2
- **Title**: Implement translation service with code-block preservation
- **Dependencies**: C1
- **Files Affected**:
  - CREATE `backend/services/translation_service.py`
- **Acceptance Criteria**:
  - [X] `extract_code_blocks(markdown: str) -> tuple[str, list[str]]` extracts fenced code blocks, replaces with `{{CODE_BLOCK}}`
  - [X] `translate_to_urdu(chapter_markdown: str) -> dict` calls Gemini gemini-2.5-flash, returns `{"translated_content": str, "original_code_blocks": list[str]}`
  - [X] All code blocks from input appear unchanged in output
  - [X] All functions have type hints, pass `ruff check`
  - [X] C1 tests now PASS

### C3 — TDD: Create translate endpoint tests

- **ID**: C3
- **Title**: Create /api/translate endpoint contract tests (TDD — must fail)
- **Dependencies**: C1
- **Files Affected**:
  - CREATE `backend/tests/test_translate_api.py`
- **Acceptance Criteria**:
  - [X] Tests cover: POST /api/translate with valid slug → 200 + `translated_content` and `original_code_blocks`
  - [X] Tests cover: POST with invalid slug → 400
  - [X] Tests cover: POST with nonexistent chapter → 404
  - [X] Tests cover: rate limit exceeded → 429 with `Retry-After` header
  - [X] All tests use type hints, pass `ruff check`
  - [X] Tests FAIL when run (no route yet)

### C4 — Add POST /api/translate route with rate limiting

- **ID**: C4
- **Title**: Add translate endpoint route to FastAPI with IP rate limiting
- **Dependencies**: C2, C3
- **Files Affected**:
  - CREATE `backend/routes/translate.py`
  - MODIFY `backend/main.py` — register translate router
- **Acceptance Criteria**:
  - [X] `POST /api/translate` accepts `{"chapter_slug": str}`, validates slug format via regex `^[a-zA-Z0-9/_-]+$`
  - [X] Reads chapter file from `website/docs/{slug}.md`, returns 404 if not found
  - [X] Calls `translation_service.translate_to_urdu()`, returns 200 with result
  - [X] IP-based rate limiter: 10 req/min per IP, returns 429 with `{"detail": "Rate limit exceeded. Try again in 60 seconds."}` (FR-016a)
  - [X] All functions have type hints, pass `ruff check`
  - [X] C3 endpoint tests now PASS

### C5 — Create UrduButton component

- **ID**: C5
- **Title**: Create "اردو میں پڑھیں" toggle button component
- **Files Affected**:
  - CREATE `website/src/components/UrduTranslateButton.tsx`
- **Acceptance Criteria**:
  - [X] Renders "اردو میں پڑھیں" button (visible to all users, no auth check)
  - [X] On click, calls `POST /api/translate` with current chapter slug
  - [X] Shows loading spinner during translation request
  - [X] On error/timeout, shows toast "Translation unavailable, please try again" and keeps English visible
  - [X] Passes TypeScript strict mode compilation

### C6 — Create UrduContent component

- **ID**: C6
- **Title**: Create RTL Urdu content renderer component
- **Dependencies**: C5
- **Files Affected**:
  - CREATE `website/src/components/UrduContent.tsx`
- **Acceptance Criteria**:
  - [X] Renders translated markdown in a `div.urdu-content` with `dir="rtl"`
  - [X] Shows "Read in English" button to toggle back to original
  - [X] Code blocks within translated content have `dir="ltr"` override
  - [X] Passes TypeScript strict mode compilation

### C7 — Inject UrduButton into DocItem Layout

- **ID**: C7
- **Title**: Inject UrduTranslateButton + UrduContent into chapter page layout
- **Dependencies**: C5, C6
- **Files Affected**:
  - MODIFY `website/src/theme/DocItem/Layout/index.tsx`
- **Acceptance Criteria**:
  - [X] UrduTranslateButton renders at top of every doc page
  - [X] When Urdu is active, UrduContent replaces default prose
  - [X] Toggle back restores original English content
  - [X] `npm run build` succeeds

### C8 — Add scoped Urdu RTL CSS

- **ID**: C8
- **Title**: Add scoped RTL CSS for Urdu content
- **Files Affected**:
  - CREATE `website/src/css/urdu-rtl.css`
  - MODIFY `website/src/css/custom.css` — import urdu-rtl.css
- **Acceptance Criteria**:
  - [X] `.urdu-content` class: `direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif;`
  - [X] `.urdu-content pre, .urdu-content code` override: `direction: ltr; text-align: left;`
  - [X] Google Fonts `@import` for Noto Nastaliq Urdu
  - [X] RTL scoped ONLY to `.urdu-content` — no global RTL side effects
  - [X] Dark mode compatible (inherits Docusaurus theme colors)

### C9 — Verify rate limiting + 429 handling end-to-end

- **ID**: C9
- **Title**: Verify rate limiting returns 429 and frontend handles it
- **Dependencies**: C4, C5
- **Files Affected**:
  - MODIFY `backend/tests/test_translate_api.py` — add rapid-fire rate limit test
  - MODIFY `website/src/components/UrduTranslateButton.tsx` — handle 429 response
- **Acceptance Criteria**:
  - [X] Sending 11 requests in <60s from same IP → 11th returns 429
  - [X] Frontend shows "Translation limit reached. Please wait a moment." on 429
  - [X] After 60s cooldown, requests succeed again
  - [X] Test passes in `pytest`

**Checkpoint**: Urdu button visible on all chapters, translation works with RTL, rate limiting enforced, code blocks unchanged

---

## Phase D: Auth (P3 — US3)

**Goal**: Email/password signup + signin with JWT httpOnly cookies, background questionnaire saves 5 fields

**Independent Test**: Sign up → see questionnaire → submit 5 answers → sign in again → no questionnaire → sign out

### D1 — Create migration SQL

- **ID**: D1
- **Title**: Create SQL migration for users + user_backgrounds tables
- **Files Affected**:
  - CREATE `backend/migrations/001_create_auth_tables.sql`
- **Acceptance Criteria**:
  - [X] Contains `CREATE TABLE users` with id, email (UNIQUE), password_hash, created_at, updated_at
  - [X] Contains `CREATE TABLE user_backgrounds` with user_id FK, python_level, robotics_experience, math_level, hardware_access, learning_goal (max 200 chars), created_at, updated_at, UNIQUE(user_id)
  - [X] Contains CHECK constraints for enum fields matching FR-022
  - [X] Contains indexes on users(email) and user_backgrounds(user_id)
  - [X] SQL is valid and executable against Postgres

### D2 — TDD: Create auth service unit tests

- **ID**: D2
- **Title**: Create auth service unit tests (TDD — must fail)
- **Files Affected**:
  - CREATE `backend/tests/test_auth_service.py`
- **Acceptance Criteria**:
  - [X] Tests cover: `hash_password()` returns bcrypt hash, `verify_password()` validates correctly
  - [X] Tests cover: `create_token()` returns valid JWT with sub, email, exp claims
  - [X] Tests cover: `decode_token()` extracts user_id and email from valid token, raises on expired/invalid
  - [X] All tests use type hints, pass `ruff check`
  - [X] Tests FAIL when run (no implementation yet)

### D3 — Create db.py (asyncpg pool)

- **ID**: D3
- **Title**: Create asyncpg connection pool module
- **Files Affected**:
  - CREATE `backend/db.py`
- **Acceptance Criteria**:
  - [X] `init_pool(dsn: str) -> None` creates asyncpg pool with min_size=2, max_size=10
  - [X] `close_pool() -> None` closes pool gracefully
  - [X] `get_pool() -> asyncpg.Pool` returns active pool, raises AssertionError if not initialized
  - [X] Reads `DATABASE_URL` from environment, requires `sslmode=require` for Neon
  - [X] All functions have type hints, pass `ruff check`

### D4 — Implement auth_utils.py (bcrypt + JWT)

- **ID**: D4
- **Title**: Implement JWT and password hashing utilities
- **Dependencies**: D2
- **Files Affected**:
  - CREATE `backend/auth_utils.py`
- **Acceptance Criteria**:
  - [X] `hash_password(password: str) -> str` uses bcrypt with cost 12
  - [X] `verify_password(plain: str, hashed: str) -> bool` validates bcrypt hash
  - [X] `create_token(user_id: int, email: str) -> str` creates HS256 JWT with 7-day expiry, claims: sub, email, exp
  - [X] `decode_token(token: str) -> dict` decodes and validates JWT, raises `JWTError` on failure
  - [X] Reads `JWT_SECRET` from env (never hardcoded)
  - [X] All functions have type hints, pass `ruff check`
  - [X] D2 tests now PASS

### D5 — TDD: Create auth endpoint tests

- **ID**: D5
- **Title**: Create signup + signin endpoint contract tests (TDD — must fail)
- **Dependencies**: D2
- **Files Affected**:
  - CREATE `backend/tests/test_auth_api.py`
- **Acceptance Criteria**:
  - [X] Tests cover: POST /api/auth/signup with valid email/password → 201 + user_id + Set-Cookie header with httpOnly
  - [X] Tests cover: POST /api/auth/signup with duplicate email → 400
  - [X] Tests cover: POST /api/auth/signup with short password → 422
  - [X] Tests cover: POST /api/auth/signin with valid credentials → 200 + Set-Cookie
  - [X] Tests cover: POST /api/auth/signin with wrong password → 401
  - [X] Tests cover: POST /api/auth/signout → 200 + cookie cleared
  - [X] Tests cover: GET /api/auth/me with valid cookie → 200
  - [X] Tests cover: GET /api/auth/me without cookie → 401
  - [X] All tests use type hints, pass `ruff check`
  - [X] Tests FAIL when run (no routes yet)

### D6 — Add auth routes (signup, signin, signout, me)

- **ID**: D6
- **Title**: Add auth endpoints to FastAPI
- **Dependencies**: D3, D4, D5
- **Files Affected**:
  - CREATE `backend/routes/auth.py`
  - MODIFY `backend/main.py` — register auth router, add db pool lifespan, add `allow_credentials=True` to CORS
  - MODIFY `backend/pyproject.toml` — add asyncpg, python-jose[cryptography], passlib[bcrypt]
- **Acceptance Criteria**:
  - [X] POST /api/auth/signup creates user in DB, returns 201, sets JWT in httpOnly cookie (Secure, SameSite=Lax)
  - [X] POST /api/auth/signin validates credentials, returns 200 with has_background flag, sets JWT cookie
  - [X] POST /api/auth/signout clears cookie (Max-Age=0)
  - [X] GET /api/auth/me returns user info from JWT cookie, 401 if missing/invalid
  - [X] POST /api/user/background upserts 5 fields to user_backgrounds table, requires JWT
  - [X] No token in response body — JWT only in httpOnly cookie
  - [X] CORS has `allow_credentials=True` with explicit origins
  - [X] D5 endpoint tests now PASS
  - [X] `ruff check` passes

### D7 — Create AuthProvider.tsx (React Context)

- **ID**: D7
- **Title**: Create custom AuthProvider with React Context for auth state
- **Files Affected**:
  - CREATE `website/src/components/AuthProvider.tsx`
- **Acceptance Criteria**:
  - [X] Exports `AuthProvider` component and `useAuth()` hook
  - [X] Provides: `user`, `isAuthenticated`, `hasBackground`, `signup()`, `signin()`, `signout()`, `checkAuth()`
  - [X] `checkAuth()` calls GET /api/auth/me on mount (cookie-based, no localStorage)
  - [X] `signup()` calls POST /api/auth/signup with `credentials: 'include'`
  - [X] All methods use `credentials: 'include'` for cookie transport
  - [X] Passes TypeScript strict mode

### D8 — Create AuthModal.tsx (signup/signin form)

- **ID**: D8
- **Title**: Create signup/signin modal component
- **Dependencies**: D7
- **Files Affected**:
  - CREATE `website/src/components/AuthModal.tsx`
  - CREATE `website/src/css/auth-modal.css`
- **Acceptance Criteria**:
  - [X] Modal with tabs: "Sign Up" and "Sign In"
  - [X] Sign Up form: email + password fields, submit calls `useAuth().signup()`
  - [X] Sign In form: email + password fields, submit calls `useAuth().signin()`
  - [X] Shows validation errors inline (email format, password ≥8 chars)
  - [X] On successful signup: triggers questionnaire display (via callback prop)
  - [X] Passes TypeScript strict mode

### D9 — Create BackgroundQuestionnaire.tsx

- **ID**: D9
- **Title**: Create 5-question background questionnaire component
- **Dependencies**: D7
- **Files Affected**:
  - CREATE `website/src/components/BackgroundQuestionnaire.tsx`
- **Acceptance Criteria**:
  - [X] Renders 5 fields per FR-022: python_level (select), robotics_experience (select), math_level (select), hardware_access (checkbox), learning_goal (textarea, max 200 chars)
  - [X] Submit calls POST /api/user/background with `credentials: 'include'`
  - [X] On success: closes questionnaire, redirects to homepage
  - [X] On error: shows inline error message
  - [X] Passes TypeScript strict mode

### D10 — Create AuthButton.tsx (navbar injection)

- **ID**: D10
- **Title**: Create auth button for navbar with sign in/out states
- **Dependencies**: D7, D8
- **Files Affected**:
  - CREATE `website/src/components/AuthButton.tsx`
  - MODIFY `website/docusaurus.config.ts` — add AuthButton to navbar items (or custom component slot)
- **Acceptance Criteria**:
  - [X] When logged out: shows "Sign In" button that opens AuthModal
  - [X] When logged in: shows user email + "Sign Out" button
  - [X] Sign Out calls `useAuth().signout()` and resets UI
  - [X] Visible on all pages in the navigation header
  - [X] Passes TypeScript strict mode, `npm run build` succeeds

**Checkpoint**: Full signup → questionnaire → signin → signout flow works, JWT in httpOnly cookie only, 5 fields saved to DB

---

## Phase E: Personalization (P4 — US4)

**Goal**: Logged-in users can personalize chapter content based on their background profile

**Independent Test**: Log in as user with saved background, click "Personalize This Chapter", verify adapted prose, code unchanged

### E1 — TDD: Create personalization service unit tests

- **ID**: E1
- **Title**: Create personalization service unit tests (TDD — must fail)
- **Files Affected**:
  - CREATE `backend/tests/test_personalization_service.py`
- **Acceptance Criteria**:
  - [X] Tests cover: `build_personalization_prompt()` includes all 5 profile fields and chapter content
  - [X] Tests cover: `personalize_chapter()` returns `{"personalized_content": str}`
  - [X] Tests cover: missing background fields default to beginner values (FR-037)
  - [X] Tests cover: returned content preserves code blocks from original (FR-033)
  - [X] All tests use type hints, pass `ruff check`
  - [X] Tests FAIL when run (no implementation yet)

### E2 — Implement personalization service

- **ID**: E2
- **Title**: Implement personalization service with Gemini prompt
- **Dependencies**: E1
- **Files Affected**:
  - CREATE `backend/services/personalization_service.py`
- **Acceptance Criteria**:
  - [X] `build_personalization_prompt(chapter_md: str, profile: dict) -> str` constructs prompt per FR-033 (prose-only adaptation, code unchanged)
  - [X] `personalize_chapter(chapter_slug: str, user_id: int) -> dict` reads chapter file, fetches user background from DB, calls Gemini, returns result
  - [X] If background missing/incomplete: uses defaults (beginner, none, high_school, False, "") per FR-037
  - [X] All functions have type hints, pass `ruff check`
  - [X] E1 tests now PASS

### E3 — TDD: Create personalize endpoint tests

- **ID**: E3
- **Title**: Create /api/personalize endpoint contract tests (TDD — must fail)
- **Dependencies**: E1, D4 (needs auth_utils for JWT validation in tests)
- **Files Affected**:
  - CREATE `backend/tests/test_personalize_api.py`
- **Acceptance Criteria**:
  - [X] Tests cover: POST /api/personalize with valid JWT cookie → 200 + `personalized_content`
  - [X] Tests cover: POST /api/personalize without JWT → 401
  - [X] Tests cover: POST /api/personalize with invalid slug → 400
  - [X] Tests cover: POST /api/personalize when background missing → 200 (uses defaults)
  - [X] All tests use type hints, pass `ruff check`
  - [X] Tests FAIL when run (no route yet)

### E4 — Add POST /api/personalize route

- **ID**: E4
- **Title**: Add personalize endpoint to FastAPI
- **Dependencies**: E2, E3, D6 (needs auth routes registered for JWT validation)
- **Files Affected**:
  - CREATE `backend/routes/personalize.py`
  - MODIFY `backend/main.py` — register personalize router
- **Acceptance Criteria**:
  - [X] POST /api/personalize requires valid JWT cookie → extracts user_id
  - [X] Validates chapter_slug, reads chapter markdown, fetches user background
  - [X] Calls `personalization_service.personalize_chapter()`, returns `{"personalized_content": str}`
  - [X] Returns 401 if no/invalid JWT, 400 if invalid slug
  - [X] All functions have type hints, pass `ruff check`
  - [X] E3 endpoint tests now PASS

### E5 — Create PersonalizeButton.tsx (auth-gated)

- **ID**: E5
- **Title**: Create "Personalize This Chapter" button component
- **Dependencies**: D7 (needs AuthProvider for `useAuth()`)
- **Files Affected**:
  - CREATE `website/src/components/PersonalizeButton.tsx`
- **Acceptance Criteria**:
  - [X] Renders "Personalize This Chapter" button ONLY when `useAuth().isAuthenticated` is true
  - [X] When not authenticated: button hidden (or disabled with tooltip "Sign in to personalize content")
  - [X] On click: calls POST /api/personalize with current chapter slug and `credentials: 'include'`
  - [X] Shows loading spinner during request
  - [X] Passes TypeScript strict mode

### E6 — Create PersonalizedContent.tsx

- **ID**: E6
- **Title**: Create personalized content renderer with "Show Original" toggle
- **Dependencies**: E5
- **Files Affected**:
  - CREATE `website/src/components/PersonalizedContent.tsx`
- **Acceptance Criteria**:
  - [X] Renders personalized markdown content replacing default chapter view
  - [X] Shows "Show Original" button to restore default content
  - [X] On Gemini error: shows toast "Personalization failed, showing default content"
  - [X] Passes TypeScript strict mode

### E7 — Inject PersonalizeButton into DocItem Layout

- **ID**: E7
- **Title**: Inject PersonalizeButton + PersonalizedContent into chapter page layout
- **Dependencies**: E5, E6, C7 (DocItem Layout already modified for Urdu)
- **Files Affected**:
  - MODIFY `website/src/theme/DocItem/Layout/index.tsx`
- **Acceptance Criteria**:
  - [X] PersonalizeButton renders on every doc page (visibility controlled by auth state)
  - [X] When personalized content active, replaces default prose
  - [X] Coexists with UrduTranslateButton without layout conflicts
  - [X] `npm run build` succeeds

**Checkpoint**: Full personalization flow works for logged-in users, code examples unchanged, auth-gated, falls back gracefully

---

## Execution Order Validation

- [X] **No forward dependencies**: Every task depends only on earlier tasks or no tasks
  - A1–A12: independent (parallel)
  - A13: depends on A1–A12
  - B1–B4: independent (parallel), no dependency on Phase A
  - C1: no dependencies
  - C2 depends on C1
  - C3 depends on C1
  - C4 depends on C2, C3
  - C5: no dependencies on backend (can parallel with C1–C4)
  - C6 depends on C5
  - C7 depends on C5, C6
  - C8: independent (parallel with C5–C7)
  - C9 depends on C4, C5
  - D1: no dependencies
  - D2: no dependencies
  - D3: no dependencies
  - D4 depends on D2
  - D5 depends on D2
  - D6 depends on D3, D4, D5
  - D7: no backend dependency (parallel with D1–D6)
  - D8 depends on D7
  - D9 depends on D7
  - D10 depends on D7, D8
  - E1: no dependencies
  - E2 depends on E1
  - E3 depends on E1, D4
  - E4 depends on E2, E3, D6
  - E5 depends on D7
  - E6 depends on E5
  - E7 depends on E5, E6, C7
- [X] **All backend logic has unit tests (TDD)**: C1→C2, D2→D4, E1→E2
- [X] **All endpoints have endpoint tests (TDD)**: C3→C4, D5→D6, E3→E4
- [X] **Rate limiting covered**: C4 (implementation), C3 (test for 429), C9 (end-to-end verification)
- [X] **Type hints enforced**: Every backend task acceptance criteria includes "type hints" + "ruff check"
- [X] **Linting covered**: Every backend task requires `ruff check` pass; every frontend task requires TypeScript strict mode + `npm run build`
- [X] **httpOnly cookies only**: D6 acceptance criteria explicitly states "No token in response body — JWT only in httpOnly cookie"
- [X] **Phase E tasks E3–E5 do not depend on any task after D5**: E3 depends on E1 + D4; E4 depends on E2 + E3 + D6; E5 depends on D7 — all within or before D range
- [X] **Code blocks unchanged in personalization**: E1, E2, FR-033 enforcement in acceptance criteria
- [X] **Code blocks unchanged in translation**: C1, C2, C4 acceptance criteria all verify code block preservation
