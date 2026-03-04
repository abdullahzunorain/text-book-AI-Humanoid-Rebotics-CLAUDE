# Tasks: Docusaurus RAG Textbook

**Input**: Design documents from `/specs/001-docusaurus-rag-textbook/`
**Prerequisites**: plan.md (required), spec.md (required), research.md (available)

**Tests**: Tests are NOT explicitly requested. Only contract tests for the API endpoint are included (minimal validation per constitution).

**Organization**: Tasks are grouped by user story (P1 → P2 → P3) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `website/` (Docusaurus 3 project)
- **Backend**: `backend/` (FastAPI)
- Paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize both projects, configure tooling, set up deployment pipelines

- [X] T001 Initialize Docusaurus 3 project in website/ with `npx create-docusaurus@latest website classic --typescript`
- [X] T002 Configure docusaurus.config.ts with site title, url, baseUrl `/Hack-I-Copilot/`, organizationName, projectName, and trailingSlash false in website/docusaurus.config.ts
- [X] T003 [P] Create backend/ directory with requirements.txt (fastapi, uvicorn[standard], openai, qdrant-client, python-dotenv) in backend/requirements.txt
- [X] T004 [P] Create backend/.env.example with GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY placeholders in backend/.env.example
- [X] T005 [P] Create website/.env.example with REACT_APP_API_URL placeholder in website/.env.example
- [X] T006 [P] Create GitHub Actions deploy workflow for Docusaurus to GitHub Pages in .github/workflows/deploy.yml
- [X] T007 [P] Create backend/Procfile with `web: uvicorn main:app --host 0.0.0.0 --port $PORT` in backend/Procfile
- [X] T008 Create root README.md with quickstart instructions (clone, install, run both projects, deploy) in README.md

**Checkpoint**: Both projects initialized, dependency files in place, deploy pipeline defined

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that MUST be complete before any user story can be fully tested

**⚠️ CRITICAL**: The chatbot backend (US2, US3) and content indexing depend on this phase

- [X] T009 Create FastAPI app skeleton with CORS middleware (allow GitHub Pages origin + localhost) in backend/main.py
- [X] T010 Create RAG service module with embed(), retrieve(), and generate() functions (stubs first) in backend/rag_service.py
- [X] T011 Create markdown chunking script that splits docs by H2/H3 headings (max 400 tokens), extracts metadata (chapter, module, page_title, heading), embeds via Gemini text-embedding-004, and upserts to Qdrant collection `book_content` in backend/index_content.py
- [X] T012 [P] Create contract test for POST /api/chat (valid request → 200 with answer field, empty question → 400, malformed body → 422) in backend/tests/test_chat_api.py
- [X] T013 Configure sidebar navigation structure with Introduction and Module 1 (ROS 2) category grouping in website/sidebars.ts

**Checkpoint**: Backend skeleton running locally, sidebar configured, indexing script ready (needs content from Phase 3)

---

## Phase 3: User Story 1 — Browse the Textbook (Priority: P1) 🎯 MVP

**Goal**: A learner can visit the site, see the home page, and navigate through all 7 pages with complete content, code examples, and exercises

**Independent Test**: Run `npm run build && npm run serve` in website/, visit every page via sidebar, verify text renders, code highlights, and exercises display. Zero broken links.

### Implementation for User Story 1

- [X] T014 [P] [US1] Create home/landing page with course title, description, hero section, and "Start Reading" CTA linking to Introduction in website/src/pages/index.tsx
- [X] T015 [P] [US1] Create Introduction chapter: What is Physical AI, sensor systems overview, one Python code example (sensor data reading), one exercise in website/docs/intro/index.md
- [X] T016 [P] [US1] Create Chapter 1: ROS 2 Architecture — explanation of graph model, DDS middleware, one Python example (rclpy init), one exercise in website/docs/module1-ros2/01-architecture.md
- [X] T017 [P] [US1] Create Chapter 2: Nodes, Topics & Services — publishers/subscribers, service clients, one Python example (minimal publisher), one exercise in website/docs/module1-ros2/02-nodes-topics-services.md
- [X] T018 [P] [US1] Create Chapter 3: Python Packages — package structure, setup.py, entry points, one Python example (create package), one exercise in website/docs/module1-ros2/03-python-packages.md
- [X] T019 [P] [US1] Create Chapter 4: Launch Files — launch system, Python launch files, composable nodes, one Python example (launch file), one exercise in website/docs/module1-ros2/04-launch-files.md
- [X] T020 [P] [US1] Create Chapter 5: URDF — robot description format, links/joints, visualization, one Python/XML example (simple URDF), one exercise in website/docs/module1-ros2/05-urdf.md
- [X] T021 [US1] Add Open Graph meta tags (title, description, image) to docusaurus.config.ts metadata section in website/docusaurus.config.ts
- [X] T022 [US1] Run `npm run build` in website/ and verify zero build errors, all 7 pages render, sidebar navigation works, no broken links
- [X] T023 [US1] Run backend/index_content.py to chunk all markdown content, embed, and upsert to Qdrant collection `book_content`

**Checkpoint**: At this point, all 7 pages are browsable with complete content. Chatbot knowledge base is indexed. US1 is fully functional and testable independently. Deploy to GitHub Pages to verify SC-001, SC-002, SC-006.

---

## Phase 4: User Story 2 — Ask the Chatbot a Question (Priority: P2)

**Goal**: A learner clicks the floating chatbot button on any page, types a question, and receives a relevant RAG-powered answer from the book content

**Independent Test**: Open any page, click chatbot button, ask "What is a ROS 2 node?", verify answer references book content, arrives within 5 seconds, and chatbot handles errors gracefully

### Implementation for User Story 2

- [X] T024 [US2] Implement RAG service: embed user question via text-embedding-004, search Qdrant top-5, build system prompt with retrieved chunks, call Gemini 2.0 Flash, return answer in backend/rag_service.py
- [X] T025 [US2] Implement POST /api/chat endpoint that accepts `{ question: string, selected_text?: string }`, calls rag_service, returns `{ answer: string, sources: [] }`, handles errors (empty question → 400, service error → 503) in backend/main.py
- [X] T026 [P] [US2] Create ChatbotWidget React component: floating button (bottom-right), toggleable chat panel, message input, scrollable message list, loading state, error display in website/src/components/ChatbotWidget.tsx
- [X] T027 [P] [US2] Create chatbot CSS styles: floating button, chat panel overlay, message bubbles (user vs bot), input area, mobile-responsive layout in website/src/components/chatbot.css
- [X] T028 [US2] Create swizzled DocItem/Layout wrapper that injects ChatbotWidget on every docs page in website/src/theme/DocItem/Layout/index.tsx
- [X] T029 [US2] Wire ChatbotWidget to call POST /api/chat with user question, display streaming-like response, show error messages for failures in website/src/components/ChatbotWidget.tsx
- [X] T030 [US2] Add empty-query validation (client-side: disable send on empty input) and off-topic graceful response (backend system prompt instructs Gemini to stay on topic) in backend/rag_service.py and website/src/components/ChatbotWidget.tsx
- [X] T031 [US2] Verify chatbot appears on all 7 pages, answers 3+ sample questions correctly, handles backend-down scenario with friendly error message

**Checkpoint**: Chatbot is functional on every page. User can ask questions and get relevant RAG answers. US2 is independently testable. Verify SC-003, SC-004.

---

## Phase 5: User Story 3 — Ask About Selected Text (Priority: P3)

**Goal**: A learner highlights text on a chapter page, sees an "Ask about this" popup, clicks it, and the chatbot opens with the selected text as context and answers about that specific passage

**Independent Test**: Open any chapter, highlight a paragraph, verify popup appears, click it, chatbot opens with context, answer references the highlighted text specifically

### Implementation for User Story 3

- [X] T032 [P] [US3] Create SelectedTextHandler React component: listen for mouseup/selectionchange on document, show "Ask about this" popup positioned near selection via getBoundingClientRect(), dispatch CustomEvent with selected text in website/src/components/SelectedTextHandler.tsx
- [X] T033 [US3] Add SelectedTextHandler to swizzled DocItem/Layout wrapper alongside ChatbotWidget in website/src/theme/DocItem/Layout/index.tsx
- [X] T034 [US3] Wire ChatbotWidget to listen for `askAboutSelection` CustomEvent, open panel, prefill selected text as context message, and send to /api/chat with `selected_text` field in website/src/components/ChatbotWidget.tsx
- [X] T035 [US3] Update backend RAG service to include `selected_text` in the LLM prompt as additional context ("The user highlighted the following passage: ...") when present in backend/rag_service.py
- [X] T036 [US3] Add popup dismiss logic: hide popup on mousedown outside selection, handle very long selections (>2000 chars → truncate with notice), handle code block selections in website/src/components/SelectedTextHandler.tsx
- [X] T037 [US3] Verify selected-text flow on 3+ chapter pages: select text → popup appears → click → chatbot answers about that passage. Test on desktop and simulate mobile.

**Checkpoint**: All 3 user stories are complete and independently functional. Verify SC-005.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final deployment verification, mobile testing, documentation, cleanup

- [X] T038 [P] Verify mobile responsiveness: chatbot panel, popup, sidebar, code blocks render correctly on 375px and 768px viewports
- [X] T039 [P] Run Docusaurus production build (`npm run build`) and verify zero warnings, all assets load, no console errors
- [X] T040 Deploy backend to Render: render.yaml created, code pushed to GitHub, configure GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY env vars in Render dashboard, get public URL
- [X] T041 Update GitHub Actions vars.API_URL with Render production URL, redeploy to GitHub Pages
- [X] T042 End-to-end smoke test on deployed site: visit all 7 pages, ask chatbot 5+ questions, test selected-text query on 3+ pages, verify <3s page load and <5s chatbot response
- [X] T043 [P] Review all pages for typos, broken links, broken images, rendering issues
- [X] T044 Finalize README.md with actual deployed URLs, quickstart instructions verified working

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (sidebar configured, indexing script ready)
- **US2 (Phase 4)**: Depends on Foundational (backend skeleton) + US1 (content indexed in Qdrant)
- **US3 (Phase 5)**: Depends on US2 (chatbot widget must exist to receive selected text)
- **Polish (Phase 6)**: Depends on all 3 user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational → produces content + indexed knowledge base
- **User Story 2 (P2)**: Can start after Foundational for backend work; needs US1 for indexed content to answer questions
- **User Story 3 (P3)**: Needs US2 complete (ChatbotWidget must exist to listen for selection events)

### Within Each User Story

- Content (markdown) before indexing
- Backend RAG service before frontend widget wiring
- Core implementation before error handling/edge cases
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1**: T003, T004, T005, T006, T007 can all run in parallel (independent files)
**Phase 3**: T014–T020 can ALL run in parallel (7 independent markdown files)
**Phase 4**: T026 + T027 can run in parallel with T024 (frontend & backend independence)
**Phase 5**: T032 can run in parallel with T035 (frontend component & backend update)
**Phase 6**: T038, T039, T043 can run in parallel (independent verification tasks)

---

## Parallel Example: User Story 1

```text
# All 7 content files can be written simultaneously:
T014: website/src/pages/index.tsx          (home page)
T015: website/docs/intro/index.md          (introduction)
T016: website/docs/module1-ros2/01-architecture.md
T017: website/docs/module1-ros2/02-nodes-topics-services.md
T018: website/docs/module1-ros2/03-python-packages.md
T019: website/docs/module1-ros2/04-launch-files.md
T020: website/docs/module1-ros2/05-urdf.md

# Then sequentially:
T021: Add meta tags (depends on docusaurus.config.ts existing)
T022: Build verification (depends on all content)
T023: Index content (depends on all markdown + backend/index_content.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (all content + build + index)
4. **STOP and VALIDATE**: Deploy to GitHub Pages, verify all 7 pages work
5. Demo: "Here's a deployed textbook with 7 pages of ROS 2 content"

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. User Story 1 → Content browsable, indexed → Deploy (MVP!)
3. User Story 2 → Chatbot answers questions → Redeploy (Enhanced MVP)
4. User Story 3 → Selected-text queries work → Redeploy (Full MVP)
5. Polish → Mobile verified, README finalized → Final deploy

### Parallel Team Strategy

With multiple developers after Foundational phase:

- **Developer A** (content): T014–T020 (all 7 pages of content)
- **Developer B** (backend): T024–T025 (RAG service + API endpoint)
- **Developer C** (frontend): T026–T028 (ChatbotWidget + CSS + swizzle)
- After all three converge: T029–T031 (wire together), then US3

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total: 44 tasks across 6 phases
- **MVP scope**: Phases 1–3 (T001–T023) deliver a deployable book with indexed content
- No TDD cycle was requested — tests are limited to backend contract tests (T012)
