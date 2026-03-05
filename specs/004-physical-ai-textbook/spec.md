# Feature Specification: Physical AI & Humanoid Robotics Textbook Platform

**Feature Branch**: `004-physical-ai-textbook`  
**Created**: 2026-03-05  
**Status**: Draft  
**Input**: User description: "Hackathon I: Create a Textbook for Teaching Physical AI & Humanoid Robotics Course"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Reader Browses the Textbook (Priority: P1)

A student or self-learner navigates to the published textbook website to study Physical AI & Humanoid Robotics. They browse an Introduction chapter, then drill into modules covering ROS 2, simulation environments, NVIDIA Isaac, and Vision-Language-Action models. Each module contains multiple chapters presented in a logical, progressive order.

**Why this priority**: Without the textbook content itself, no other feature (chatbot, personalization, translation) has value. The book is the core deliverable.

**Independent Test**: Visit the deployed site → sidebar shows all 4 modules with chapters in order → click any chapter → content renders with text, code blocks, and images.

**Acceptance Scenarios**:

1. **Given** a reader visits the textbook URL, **When** the page loads, **Then** they see a landing page with a sidebar listing all modules and chapters.
2. **Given** a reader clicks a chapter in the sidebar, **When** the page loads, **Then** the chapter content renders correctly with headings, body text, code blocks, and diagrams.
3. **Given** a reader finishes a chapter, **When** they look at the bottom or sidebar, **Then** they see navigation to the next/previous chapter.
4. **Given** a reader visits on a mobile device, **When** the page loads, **Then** the layout is responsive and readable.

---

### User Story 2 — Reader Asks the RAG Chatbot a Question (Priority: P1)

A reader has a question about the book's content. They open the embedded chatbot widget and type a question. The chatbot answers based on the textbook's content using Retrieval-Augmented Generation.

**Why this priority**: The RAG chatbot is a core deliverable that makes the textbook interactive and AI-native. Together with the book content, this forms the minimum viable product.

**Independent Test**: Open any chapter → click the chatbot → type "What is ROS 2?" → receive an answer that references textbook content.

**Acceptance Scenarios**:

1. **Given** a reader is on any chapter page, **When** they click the chatbot widget, **Then** a chat interface opens.
2. **Given** the chat is open, **When** the reader types a question about the book's content, **Then** the chatbot returns a relevant answer sourced from the textbook.
3. **Given** the reader selects a passage of text on the page and asks a question, **When** the question is submitted, **Then** the chatbot answers specifically about the selected text.
4. **Given** the reader asks a question unrelated to the textbook, **When** the response is generated, **Then** the chatbot indicates it can only answer questions about the book's content.

---

### User Story 3 — Reader Signs Up and Provides Background (Priority: P2)

A new reader creates an account to unlock personalized features. Immediately after signup, the system asks them about their software and hardware background (Python level, robotics experience, math level, hardware access, learning goal). This background information enables content personalization.

**Why this priority**: Authentication and user profiling are prerequisites for content personalization and translation — both bonus-point features. Without knowing who the reader is and what they know, personalization cannot work.

**Independent Test**: Click "Sign In" → switch to "Sign Up" tab → enter email/password → submit → see the background questionnaire → fill it out → submit successfully.

**Acceptance Scenarios**:

1. **Given** a new reader clicks "Sign In" and switches to "Sign Up," **When** they enter a valid email and password (8+ characters), **Then** the account is created and an auth session begins.
2. **Given** the reader just signed up, **When** the signup flow completes, **Then** a background questionnaire appears automatically.
3. **Given** the questionnaire is displayed, **When** the reader fills in their Python level, robotics experience, math level, hardware access, and learning goal and submits, **Then** the background is saved and the questionnaire closes.
4. **Given** a returning reader signs in and has never completed the questionnaire, **When** they sign in, **Then** the questionnaire appears.
5. **Given** a returning reader signs in and has already completed the questionnaire, **When** they sign in, **Then** the questionnaire does not appear.
6. **Given** a reader enters an email that is already registered, **When** they try to sign up, **Then** they see an error message indicating the email is already in use.

---

### User Story 4 — Logged-In Reader Personalizes Chapter Content (Priority: P2)

A signed-in reader navigates to any chapter and presses a "Personalize" button at the top of the chapter. The system uses their background profile to adapt the content — adjusting complexity, adding/removing prerequisite explanations, and tailoring examples to their experience level.

**Why this priority**: Personalization is a key differentiator that demonstrates the AI-native nature of the textbook. It depends on auth and background (User Story 3).

**Independent Test**: Sign in (with background profile completed) → open any chapter → click "Personalize" → see the chapter content adapted to reported experience level.

**Acceptance Scenarios**:

1. **Given** a signed-in reader with a beginner Python level is on a chapter with code examples, **When** they click "Personalize," **Then** the content is adapted with more detailed explanations and simpler examples.
2. **Given** a signed-in reader with an advanced background, **When** they click "Personalize," **Then** the content is adapted to skip basic explanations and include deeper technical details.
3. **Given** a reader who is not signed in, **When** they see the chapter page, **Then** the "Personalize" button either prompts them to sign in or is not shown.
4. **Given** personalization is in progress, **When** the reader waits, **Then** they see a loading indicator until the personalized content is ready.
5. **Given** a signed-in reader with no background profile, **When** they click "Personalize," **Then** the system uses sensible beginner defaults.

---

### User Story 5 — Logged-In Reader Translates Chapter to Urdu (Priority: P2)

A signed-in reader navigates to any chapter and presses a "Translate to Urdu" button at the top of the chapter. The system translates the chapter content to Urdu and displays it in place of the English version.

**Why this priority**: Urdu translation is a bonus feature that expands accessibility for a significant portion of the target audience. It depends on auth (User Story 3).

**Independent Test**: Sign in → open any chapter → click "Translate to Urdu" → see the chapter content rendered in Urdu script.

**Acceptance Scenarios**:

1. **Given** a signed-in reader is on any chapter, **When** they click "Translate to Urdu," **Then** the chapter content is translated and rendered in Urdu (right-to-left text) properly.
2. **Given** translation is in progress, **When** the reader waits, **Then** they see a loading indicator.
3. **Given** the translated content is displayed, **When** the reader wants the English version back, **Then** they can switch back to the original content.
4. **Given** a reader who is not signed in, **When** they see the chapter page, **Then** the translate button prompts them to sign in.

---

### User Story 6 — Reader Asks Chatbot About Selected Text (Priority: P2)

A reader highlights a passage of text on the current chapter and uses the chatbot to ask questions specifically about that selection. The chatbot answer is scoped to the highlighted text.

**Why this priority**: Selected-text Q&A is a core chatbot differentiator mentioned in the hackathon requirements. It makes the chatbot contextually aware.

**Independent Test**: Open any chapter → select a paragraph → open chatbot → ask a question → the answer references the selected text.

**Acceptance Scenarios**:

1. **Given** a reader selects text on a chapter page, **When** a selection handler detects the highlight, **Then** the selected text is captured and available to the chatbot.
2. **Given** the chatbot is open with selected text context, **When** the reader asks a question about that text, **Then** the chatbot answer is specifically about the selected passage.
3. **Given** no text is selected, **When** the reader asks the chatbot a general question, **Then** the chatbot answers using the full textbook knowledge base -- (RAG System).

---

### Edge Cases

- What happens when the reader submits the chatbot with an empty question? → A validation message prompts them to enter a question.
- What happens when the chatbot backend is unavailable? → An error message is shown; the textbook content remains fully accessible.
- What happens when personalization or translation times out? → A timeout error is shown with an option to retry.
- What happens when a reader signs up with a password shorter than 8 characters? → A validation error is shown before submission.
- What happens when the reader's session expires? → They are prompted to sign in again; and any unsaved data (questionnaire in progress) is preserved in Neon database.
- What happens when a chapter has no content yet? → A placeholder page indicates the chapter is coming soon.

---

## Requirements *(mandatory)*

### Functional Requirements

**Textbook Content & Delivery**

- **FR-001**: System MUST serve a multi-module textbook covering Physical AI & Humanoid Robotics with at least 4 modules and 17 chapters.
- **FR-002**: System MUST present chapters in a navigable sidebar organized by module with sequential ordering.
- **FR-003**: System MUST support rich content rendering: headings, body text, code blocks with syntax highlighting, images, and tables.
- **FR-004**: System MUST deploy the textbook as a static site accessible via a public URL on github.
- **FR-005**: System MUST provide next/previous chapter navigation.

**RAG Chatbot**

- **FR-006**: System MUST embed an AI chatbot widget accessible from every chapter page.
- **FR-007**: Chatbot MUST answer user questions using Retrieval-Augmented Generation sourced from the textbook's content.
- **FR-008**: Chatbot MUST accept a natural-language question of up to 2,000 characters.
- **FR-009**: Chatbot MUST support a "selected text" mode where the answer is scoped to a user-highlighted passage.
- **FR-010**: Chatbot MUST display a clear loading state while generating answers.
- **FR-011**: System MUST save the previous chats of a user in Neon Database.
- **FR-011**: System Must use Configure Retry Options for Gemini API rate limit's


**Authentication & User Profile**

- **FR-011**: System MUST allow users to create an account with email and password (minimum 8 characters).
- **FR-012**: System MUST allow users to sign in with email and password.
- **FR-013**: System MUST maintain authenticated sessions via httpOnly cookies.
- **FR-014**: System MUST allow users to sign out, clearing their session.
- **FR-015**: System MUST present a background questionnaire to users who have not completed it (after signup or signin).
- **FR-016**: Background questionnaire MUST collect: Python level (beginner/intermediate/advanced), robotics experience (none/hobbyist/student/professional), math level (high school/undergraduate/graduate), hardware access (yes/no), and learning goal (free text, max 200 characters).
- **FR-017**: System MUST persist user background profiles for use in personalization.

**Content Personalization**

- **FR-018**: System MUST provide a "Personalize" action on each chapter page for signed-in users.
- **FR-019**: Personalization MUST adapt chapter content based on the user's stored background profile — adjusting complexity, explanations, and examples.
- **FR-020**: System MUST use sensible beginner defaults when a user has no saved background profile.
- **FR-021**: System MUST display a loading indicator during personalization.

**Urdu Translation**

- **FR-022**: System MUST provide a "Translate to Urdu" action on each chapter page for signed-in users.
- **FR-023**: Translation MUST render the full chapter content in Urdu with appropriate right-to-left text direction.
- **FR-024**: System MUST allow the reader to switch back to the original English content after viewing the Urdu translation.
- **FR-025**: System MUST display a loading indicator during translation.

**Deployment & Infrastructure**

- **FR-026**: System MUST be deployable to GitHub Page for the frontend.
- **FR-027**: Backend MUST support the textbook content as source files (Markdown).
- **FR-028**: System MUST use a serverless PostgreSQL database(Neon) for user data storage.
- **FR-029**: System MUST use a vector database for RAG document retrieval.

### Key Entities

- **User**: A registered reader with email, hashed password, and authentication state.
- **Background Profile**: A user's self-reported learning context — Python level, robotics experience, math level, hardware access, learning goal. One per user.
- **Chapter**: A Markdown document within a module. Has a title, sidebar position, and module association.
- **Module**: A thematic grouping of chapters (e.g., "ROS 2 Fundamentals"). Contains 4-5 chapters.
- **Chat Message**: A user question and AI-generated answer pair, optionally scoped to selected text.
- **Personalized Content**: An AI-generated adaptation of a chapter, tailored to a user's background profile.
- **Translated Content**: An AI-generated Urdu translation of a chapter.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 4 modules and at least 17 chapters are accessible and render correctly in the deployed textbook.
- **SC-002**: The RAG chatbot returns a relevant, textbook-sourced answer within 10 seconds for 90% of questions about covered topics.
- **SC-003**: Users can complete the signup → questionnaire flow in under 2 minutes.
- **SC-004**: Personalized content is delivered to the reader within 15 seconds of clicking "Personalize."
- **SC-005**: Urdu translation is delivered within 15 seconds of clicking "Translate to Urdu."
- **SC-006**: The chatbot accurately answers selected-text questions 80% of the time (answer references the selected passage).
- **SC-007**: The textbook is accessible via a public URL with no authentication required for reading content.
- **SC-008**: 95% of first-time users can locate and use the chatbot without instructions.
- **SC-009**: The entire signup → sign-in → personalize → translate journey completes without errors for 90% of sessions.

---

## Assumptions

- The target audience is primarily English-speaking students/professionals who may also read Urdu.
- The textbook content is authored in Markdown and stored in the repository alongside the code.
- AI-powered features (personalization, translation, RAG) rely on external LLM APIs (e.g., Google Gemini, OpenAI, Groq) and may incur per-request costs.
- The deployment environment does not require HTTPS for local development (HTTP on localhost).
- Session persistence uses httpOnly cookies with environment-aware Secure and SameSite attributes.
- The background questionnaire fields (Python level, robotics experience, etc.) are sufficient to drive meaningful personalization.

---

## Scope

### In Scope

- 4-module textbook with 17+ chapters on Physical AI & Humanoid Robotics
- Docusaurus-based static site with sidebar navigation
- RAG chatbot embedded in every chapter (supports general and selected-text questions)
- Email/password signup and signin with session cookies
- Background questionnaire (collected post-signup/signin if incomplete)
- Per-chapter content personalization based on user background
- Per-chapter Urdu translation
- Deployment to GitHub Pages

### Out of Scope

- OAuth or social login (only email/password)
- Real-time collaborative features (comments, annotations, forums)
- Offline reading or PWA capabilities
- Content authoring tools for external authors
- Payment or subscription systems
- Physical hardware provisioning (Jetson kits, robots, etc.)
- Automated textbook content generation (content is pre-authored)
- Multi-language translation beyond Urdu
