# Feature Specification: Docusaurus RAG Textbook

**Feature Branch**: `001-docusaurus-rag-textbook`  
**Created**: 2026-03-03  
**Status**: Draft  
**Input**: User description: "Build a minimal deployed Docusaurus textbook with an embedded RAG chatbot"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Browse the Textbook (Priority: P1)

A learner visits the site to study Physical AI and ROS 2. They land on the home page, see an overview of the course, and navigate to chapters using a sidebar. Each chapter presents explanatory text, a working Python code example, and a short practice exercise. The learner reads sequentially from the Introduction through all five Module 1 chapters.

**Why this priority**: Without readable, navigable book content, nothing else (chatbot, deployment) has value. The book is the core product.

**Independent Test**: Open the deployed site, navigate every page via the sidebar, verify all text renders, code examples display with syntax highlighting, and exercises are readable.

**Acceptance Scenarios**:

1. **Given** the site is deployed, **When** a user visits the root URL, **Then** a home/landing page displays with course title, brief description, and navigation to chapters.
2. **Given** the home page is loaded, **When** the user clicks "Introduction" in the sidebar, **Then** the Introduction chapter loads with content about Physical AI and sensor systems overview.
3. **Given** the user is on any chapter page, **When** they view the chapter content, **Then** they see explanatory text, at least one Python code example with syntax highlighting, and one exercise with clear instructions.
4. **Given** the user is on any chapter, **When** they use the sidebar, **Then** they can navigate to any other chapter without page errors or broken links.
5. **Given** the user accesses the site on a mobile device, **When** any page loads, **Then** the content is readable, the sidebar is accessible, and code examples don't overflow the viewport.

---

### User Story 2 — Ask the Chatbot a Question (Priority: P2)

A learner is reading a chapter and has a question about the content. They click the floating chatbot button in the bottom-right corner, type their question in the chat panel, and receive a relevant answer drawn from the book's content.

**Why this priority**: The chatbot is the primary differentiator beyond a static textbook. It turns passive reading into interactive learning. It depends on book content existing (P1) but is independently testable once content is present.

**Independent Test**: Open any page, click the chatbot button, type a question about book content (e.g., "What is a ROS 2 node?"), and verify the answer is relevant and sourced from book material.

**Acceptance Scenarios**:

1. **Given** any page is fully loaded, **When** the user looks at the bottom-right corner, **Then** a floating chatbot button is visible and clickable.
2. **Given** the chatbot button is visible, **When** the user clicks it, **Then** a chat panel opens with a text input field and a welcome message or placeholder prompt.
3. **Given** the chat panel is open, **When** the user types a question about book content and submits, **Then** the chatbot returns a relevant answer within a reasonable time.
4. **Given** the chat panel is open, **When** the user types a question unrelated to book content, **Then** the chatbot responds gracefully (e.g., "I can only answer questions about the textbook content").
5. **Given** the chatbot panel is open on mobile, **When** the user interacts with it, **Then** the panel is usable—text input works, responses are readable, and the panel can be closed.

---

### User Story 3 — Ask About Selected Text (Priority: P3)

A learner is reading a chapter and encounters a difficult passage. They highlight/select the confusing text. A small popup appears saying "Ask about this." They click it, and the chatbot panel opens with the selected text pre-filled as context, then delivers an explanation.

**Why this priority**: Selected-text queries are a high-impact UX feature that makes the chatbot contextual rather than generic. It depends on both the book (P1) and chatbot (P2) working, so it's the last user story.

**Independent Test**: Open a chapter page, highlight a paragraph of text, verify the "Ask about this" popup appears, click it, and verify the chatbot opens with context and returns a relevant answer about that specific passage.

**Acceptance Scenarios**:

1. **Given** the user is on any chapter page, **When** they select/highlight text, **Then** a small popup (tooltip or floating button) appears near the selection saying "Ask about this."
2. **Given** the "Ask about this" popup is visible, **When** the user clicks it, **Then** the chatbot panel opens with the selected text shown as context in the conversation.
3. **Given** the chatbot has received selected text as context, **When** processing the query, **Then** the chatbot answers specifically about that highlighted passage using book knowledge.
4. **Given** the user selects text, **When** they click elsewhere to deselect without clicking "Ask about this," **Then** the popup dismisses gracefully without side effects.
5. **Given** the user is on a mobile device, **When** they long-press to select text, **Then** the "Ask about this" popup appears and works the same as on desktop.

---

### Edge Cases

- **Chatbot service unavailable**: If the chatbot backend is unreachable, the widget displays a friendly error message (e.g., "Chatbot is temporarily unavailable. Please try again later.") instead of failing silently or crashing the page.
- **Empty or nonsensical query**: If the user submits an empty message or gibberish, the chatbot responds with a helpful prompt (e.g., "Try asking a question about the textbook content.").
- **Very long text selection**: If the user selects an extremely large block of text (e.g., an entire page), the system truncates or summarizes the selection before sending to the chatbot, and informs the user.
- **Code block selection**: If the user selects a code example, the chatbot should still handle it and explain the code in context.
- **Rapid successive queries**: If the user sends multiple messages quickly, responses arrive in order without interleaving or dropping messages.
- **Browser back/forward navigation**: Navigating between pages preserves chatbot open/closed state but clears conversation history (stateless per constitution).
- **No matching content in knowledge base**: If the chatbot cannot find relevant content, it says so honestly rather than hallucinating an answer.

## Requirements *(mandatory)*

### Functional Requirements

**Book & Content**

- **FR-001**: Site MUST display a home/landing page with course title, description, and navigation to all chapters.
- **FR-002**: Site MUST display an Introduction chapter covering "What is Physical AI" and a sensor systems overview.
- **FR-003**: Site MUST display five Module 1 (ROS 2) chapters: (1) Architecture, (2) Nodes/Topics/Services, (3) Python Packages, (4) Launch Files, (5) URDF.
- **FR-004**: Each chapter MUST include explanatory text, at least one working Python code example with syntax highlighting, and one exercise with clear instructions.
- **FR-005**: Site MUST provide sidebar navigation showing all chapters in logical order, grouped by Introduction and Module 1.
- **FR-006**: Site MUST be publicly accessible via a URL with no login or authentication required.
- **FR-007**: Site MUST render correctly on mobile, tablet, and desktop viewports.
- **FR-008**: Site MUST include basic metadata (page titles, descriptions) for link sharing and discoverability.

**Chatbot**

- **FR-009**: A floating chatbot button MUST appear in the bottom-right corner of every page.
- **FR-010**: Clicking the chatbot button MUST open a chat panel overlay.
- **FR-011**: The chat panel MUST include a text input field for typing questions and a scrollable area for conversation history.
- **FR-012**: The chatbot MUST answer questions by retrieving relevant content from the book's knowledge base (RAG pattern).
- **FR-013**: The chatbot MUST NOT require any login, account, or authentication.
- **FR-014**: The chatbot MUST gracefully handle errors (service unavailable, empty queries, off-topic questions) with user-friendly messages.
- **FR-015**: Chat conversations MUST NOT persist across page reloads or navigation (stateless).

**Selected-Text Queries**

- **FR-016**: When a user selects/highlights text on any chapter page, a popup MUST appear near the selection with an "Ask about this" action.
- **FR-017**: Clicking "Ask about this" MUST open the chatbot panel with the selected text included as context.
- **FR-018**: The chatbot MUST use the selected text as additional context when generating its response.
- **FR-019**: The popup MUST dismiss when the user deselects text or clicks elsewhere.

### Key Entities

- **Chapter**: A unit of content with a title, body text, code examples, exercises, and a position in the navigation hierarchy. Chapters belong to either the Introduction section or Module 1.
- **Chat Message**: A single exchange in the chatbot conversation, containing the user's query text, optional selected-text context, and the chatbot's response.
- **Knowledge Chunk**: A segment of book content indexed for retrieval. Each chunk is derived from chapter text and is searchable by the chatbot when answering user questions.

## Assumptions

- Book content is written in English only (no i18n per constitution).
- No chat history is preserved across sessions—each page load starts a fresh conversation.
- Chatbot answers are best-effort; no guaranteed accuracy SLA for MVP. The chatbot may occasionally produce imperfect answers.
- The chatbot knowledge base is pre-built from the book content and does not update in real-time as content changes (re-indexing is a manual/deploy-time process).
- No rate limiting or abuse prevention on the chatbot in MVP.
- Code examples in chapters are illustrative; they are not executed in-browser (no interactive REPL).
- The "Ask about this" popup only appears on chapter content pages, not on the home/landing page (which has minimal selectable content).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 7 pages (home + Introduction + 5 Module 1 chapters) load successfully with complete content, zero broken links, and zero rendering errors.
- **SC-002**: Every page loads in under 3 seconds on a standard mobile connection (simulated 4G).
- **SC-003**: The chatbot widget appears and is functional on every page of the site.
- **SC-004**: Users receive relevant, book-sourced answers to content-related questions within 5 seconds of submitting.
- **SC-005**: The "Ask about this" selected-text workflow completes successfully on every chapter page—from text selection through receiving a contextual answer.
- **SC-006**: The site is publicly accessible via a single URL with no login, signup, or paywall.
- **SC-007**: The site is readable and navigable on mobile, tablet, and desktop devices without horizontal scrolling or overlapping elements.
- **SC-008**: A first-time visitor can navigate from the home page to any chapter and ask the chatbot a question within 2 minutes without instructions.
