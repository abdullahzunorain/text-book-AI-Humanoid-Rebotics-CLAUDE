# Feature Specification: MVP2 - Complete Physical AI Textbook

**Feature Branch**: `002-mvp2-complete-textbook`  
**Created**: 2026-03-04  
**Status**: Draft  
**Input**: User description: "Complete the Physical AI textbook with 12 new pages across 3 modules (Gazebo/Unity, NVIDIA Isaac, VLA), add 4 Claude subagents, Urdu translation button, authentication with better-auth, and personalization features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Complete Textbook Content (Priority: P1)

A robotics student visits the textbook site to learn about simulation environments and Vision-Language-Action models. They navigate through all 4 complete modules, finding comprehensive content on ROS 2, Gazebo/Unity, NVIDIA Isaac, and VLA, with code examples and exercises in each chapter.

**Why this priority**: Core content delivery is the primary value proposition. Without complete modules, the textbook cannot fulfill its educational mission. This represents the foundation that all other features build upon.

**Independent Test**: Navigate to each of the 18 total pages (6 existing + 12 new), verify each contains minimum 600 words, 2 code examples, learning objectives, and key takeaways. Test without authentication or any advanced features.

**Acceptance Scenarios**:

1. **Given** a user visits the Module 2 section, **When** they click on any of the 4 Gazebo/Unity pages, **Then** each page loads with complete formatted content including code examples
2. **Given** a user reads Module 3, **When** they navigate through NVIDIA Isaac chapters, **Then** they find practical examples for Isaac Sim and Isaac Gym
3. **Given** a user explores Module 4, **When** they read VLA content, **Then** they understand Vision-Language-Action models through working code samples
4. **Given** a user is on any chapter page, **When** they scroll through the content, **Then** they see learning objectives at the top and key takeaways at the bottom

---

### User Story 2 - Read Content in Urdu (Priority: P2)

A Pakistani student who is more comfortable reading in Urdu visits any chapter. They click the "اردو میں پڑھ یں" button at the top of the page. The prose content is immediately translated to Urdu and displayed in an RTL layout with appropriate Urdu fonts, while code blocks remain in English. They can toggle back to English at any time.

**Why this priority**: Accessibility for Urdu-speaking learners significantly expands the textbook's reach. This feature requires no authentication, making education accessible to anyone regardless of account status.

**Independent Test**: Navigate to any chapter, click the Urdu button, verify translated prose appears in RTL layout with Urdu fonts, code blocks remain in English, and translate back to English works correctly.

**Acceptance Scenarios**:

1. **Given** a user is reading Chapter 1.1, **When** they click "اردو میں پڑھیں", **Then** the page prose translates to Urdu within 3 seconds
2. **Given** content is displayed in Urdu, **When** user examines code blocks, **Then** all code remains in English with original syntax highlighting
3. **Given** Urdu content is showing, **When** user clicks "Read in English" button, **Then** original English prose is restored
4. **Given** any chapter with RTL Urdu text, **When** viewed on mobile, **Then** text flows correctly right-to-left and is fully readable

---

### User Story 3 - Create Account and Share Background (Priority: P3)

A new user decides to create an account for personalized learning. They click "Sign Up", enter email and password, complete signup, and are immediately shown a 5-question background questionnaire about their Python level, robotics experience, math background, hardware access, and learning goals. After submitting, they're redirected to the homepage with a "Logged In" indicator.

**Why this priority**: User accounts enable personalization and future features like progress tracking. The background questionnaire provides essential data for tailoring content to each learner's needs.

**Independent Test**: Complete signup flow from homepage, verify email/password authentication works, verify background questionnaire appears post-signup with all 5 questions, submit responses, confirm data is saved to database.

**Acceptance Scenarios**:

1. **Given** a user on the homepage, **When** they click "Sign Up" and enter valid email/password, **Then** account is created and they're shown the background questionnaire
2. **Given** the background questionnaire is displayed, **When** user submits all 5 answers, **Then** data is saved to `user_backgrounds` table and user is redirected to homepage
3. **Given** a user with an existing account, **When** they click "Sign In" with correct credentials, **Then** they're logged in without seeing the questionnaire again
4. **Given** a logged-in user, **When** they navigate to any page, **Then** they see their logged-in status and a "Sign Out" option

---

### User Story 4 - Get Personalized Chapter Content (Priority: P4)

A logged-in user with saved background information is reading a chapter on ROS 2 nodes. They click "Personalize This Chapter" button. The system fetches their profile (intermediate Python, beginner robotics, no hardware access, goal: learn for university project), sends it with the chapter content to Gemini, and returns a personalized version. The content now includes extra explanations for concepts, suggests online simulators instead of hardware labs, and connects ROS concepts to university CS coursework.

**Why this priority**: Personalization is the killer feature that differentiates this textbook. However, it depends on auth (P3) and base content (P1) being complete first. This is the capstone feature of MVP2.

**Independent Test**: Log in as a user with specific background (e.g., beginner Python, no hardware), navigate to any chapter, click "Personalize This Chapter", verify returned content is tailored to that user profile and differs from the default content.

**Acceptance Scenarios**:

1. **Given** a logged-in user with profile data on a chapter page, **When** they click "Personalize This Chapter", **Then** personalized markdown appears within 5 seconds
2. **Given** personalized content is shown, **When** user compares it to default, **Then** explanations are adjusted to their stated Python/robotics level
3. **Given** a user with "no hardware access" in their profile, **When** content is personalized, **Then** hardware exercises are replaced with simulator-based alternatives
4. **Given** a user whose goal is "prepare for robotics job interview", **When** they personalize a VLA chapter, **Then** content includes interview-focused examples and common questions

---

### User Story 5 - Leverage Claude Subagents for Development (Priority: P5)

A content contributor working on the project opens VS Code with Claude Code. They need to write a new chapter on NVIDIA Isaac Gym. They invoke the `content-writer` subagent, which provides a structured markdown template with learning objectives, 600+ word prose sections, and placeholders for code examples. Next, they use the `code-example-generator` subagent to create 2 working Python examples for Isaac Gym tasks. The generated code runs without errors and follows project conventions.

**Why this priority**: Subagents accelerate content creation and maintain consistency, but are tools for contributors, not end users. This priority is lower because it's a productivity enhancement rather than core functionality.

**Independent Test**: In VS Code with Claude Code, invoke each of the 4 subagents with sample inputs, verify they generate appropriate outputs following their defined behaviors.

**Acceptance Scenarios**:

1. **Given** a contributor in VS Code with Claude Code extension, **When** they invoke `content-writer` subagent for Module 3 Chapter 2, **Then** a structured markdown file is generated with learning objectives and section headings
2. **Given** a contributor needs Isaac Gym code, **When** they invoke `code-example-generator` with task description, **Then** working Python code is generated with comments and follows PEP 8
3. **Given** a finished English chapter, **When** contributor tests `urdu-translator` subagent on a paragraph, **Then** accurate Urdu translation is provided
4. **Given** review feedback on a chapter, **When** contributor invokes `content-personalizer` subagent with user profile, **Then** personalization suggestions are generated

---

### Edge Cases

- What happens when a user clicks "اردو میں پڑھیں" but translation API times out? → Show error toast: "Translation unavailable, please try again", keep English content visible
- What happens when a logged-in user personalizes a chapter but their background data is incomplete? → System uses default values for missing fields and still generates personalization
- What happens when an unauthenticated user tries to click "Personalize This Chapter"? → Show tooltip: "Sign in to personalize content", button is disabled/hidden for non-authenticated
- What happens when two users with identical backgrounds personalize the same chapter? → Both receive the same personalized content (responses are deterministic given same inputs)
- What happens when database is down during signup? → Show error: "Unable to create account. Please try again later", do not create partial account
- What happens when a user signs up with an email that already exists? → Show error: "Email already registered. Please sign in or use another email"
- What happens if Gemini API returns incomplete/malformed content for personalization? → Log error, show toast: "Personalization failed, showing default content", display original chapter

## Requirements *(mandatory)*

### Functional Requirements

#### Content Delivery (P1)

- **FR-001**: System MUST add 12 new markdown chapter pages across 3 modules with exact file paths:
  - Module 2 - Gazebo & Unity Simulation:
    - `website/docs/module2-simulation/chapter1-gazebo-basics.md`
    - `website/docs/module2-simulation/chapter2-gazebo-ros2-integration.md`
    - `website/docs/module2-simulation/chapter3-unity-robotics.md`
    - `website/docs/module2-simulation/chapter4-unity-ml-agents.md`
  - Module 3 - NVIDIA Isaac:
    - `website/docs/module3-isaac/chapter1-isaac-sim-intro.md`
    - `website/docs/module3-isaac/chapter2-isaac-gym.md`
    - `website/docs/module3-isaac/chapter3-isaac-ros2-bridge.md`
    - `website/docs/module3-isaac/chapter4-isaac-reinforcement-learning.md`
  - Module 4 - Vision-Language-Action (VLA):
    - `website/docs/module4-vla/chapter1-vla-intro.md`
    - `website/docs/module4-vla/chapter2-multimodal-models.md`
    - `website/docs/module4-vla/chapter3-action-chunking.md`
    - `website/docs/module4-vla/chapter4-vla-robotics.md`

- **FR-002**: Each new chapter page MUST contain minimum 600 words of educational prose

- **FR-003**: Each new chapter page MUST include exactly 2 code examples with syntax highlighting (Python, YAML, or Bash)

- **FR-004**: Each new chapter page MUST include a "Learning Objectives" section at the start

- **FR-005**: Each new chapter page MUST include a "Key Takeaways" section at the end

- **FR-006**: System MUST update `website/sidebars.ts` to include all 3 new modules in navigation

#### Claude Subagents (P5)

- **FR-007**: Project MUST include 4 Claude Code subagent definition files:
  - `.claude/agents/content-writer.md` - Generates markdown chapter structure with learning objectives
  - `.claude/agents/code-example-generator.md` - Creates working code examples for chapters
  - `.claude/agents/urdu-translator.md` - Translates educational prose to Urdu
  - `.claude/agents/content-personalizer.md` - Suggests personalization adjustments based on user profile

- **FR-008**: Each subagent definition MUST specify its role, input format, output format, and behavioral guidelines

#### Urdu Translation (P2)

- **FR-009**: System MUST display an "اردو میں پڑھیں" (Read in Urdu) button at the top of every chapter page

- **FR-010**: Button MUST be visible to all users (no authentication required)

- **FR-011**: When button is clicked, system MUST send POST request to `/api/translate` endpoint with `{chapter_slug: string}`

- **FR-012**: Backend MUST call Gemini API to translate prose content while preserving code blocks in English

- **FR-013**: Backend MUST return `{translated_content: string, original_code_blocks: Array<string>}`

- **FR-014**: Frontend MUST render translated content in an RTL (right-to-left) div with Urdu font family

- **FR-015**: Translated view MUST include a "Read in English" button to toggle back to original

- **FR-016**: Code blocks MUST remain in English with original syntax highlighting within Urdu-translated content

- **FR-016a**: Backend MUST enforce IP-based rate limiting of 10 requests/minute per IP on `/api/translate` endpoint. Requests exceeding the limit MUST return 429 Too Many Requests with `{"detail": "Rate limit exceeded. Try again in 60 seconds."}`

#### Authentication System (P3)

- **FR-017**: System MUST implement a custom `AuthProvider.tsx` using React Context for frontend auth state management (signup, signin, signout methods calling FastAPI JWT endpoints)

- **FR-018**: Backend MUST implement JWT token generation and validation using FastAPI

- **FR-019**: System MUST provide "Sign Up" and "Sign In" buttons in the main navigation header

- **FR-020**: Sign Up flow MUST collect email and password, create user in `users` table, and return JWT token

- **FR-021**: After successful signup, system MUST immediately display a 5-question background questionnaire

- **FR-022**: Questionnaire MUST collect these fields:
  - `python_level`: beginner | intermediate | advanced
  - `robotics_experience`: none | hobbyist | student | professional
  - `math_level`: high_school | undergraduate | graduate
  - `hardware_access`: boolean (Do you have access to robot hardware?)
  - `learning_goal`: text (free-form, max 200 chars)

- **FR-023**: Questionnaire responses MUST be saved to `user_backgrounds` table linked to user ID

- **FR-024**: System MUST store JWT token in HTTP-only cookie for authenticated requests

- **FR-025**: Sign In flow MUST validate email/password, return JWT token on success

- **FR-026**: Invalid credentials MUST return 401 error with message "Invalid email or password"

- **FR-027**: Backend MUST create database tables with SQL schema:

```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User backgrounds table
CREATE TABLE user_backgrounds (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  python_level VARCHAR(20) CHECK (python_level IN ('beginner', 'intermediate', 'advanced')),
  robotics_experience VARCHAR(20) CHECK (robotics_experience IN ('none', 'hobbyist', 'student', 'professional')),
  math_level VARCHAR(20) CHECK (math_level IN ('high_school', 'undergraduate', 'graduate')),
  hardware_access BOOLEAN DEFAULT FALSE,
  learning_goal TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id)
);

-- Index for faster lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_backgrounds_user_id ON user_backgrounds(user_id);
```

#### Personalization (P4)

- **FR-028**: System MUST display a "Personalize This Chapter" button on every chapter page

- **FR-029**: Button MUST be visible ONLY to authenticated users (JWT cookie present)

- **FR-030**: When clicked, system MUST send POST request to `/api/personalize` with `{chapter_slug: string}` and JWT in cookie

- **FR-031**: Backend MUST validate JWT, extract user_id, fetch user background from database

- **FR-032**: Backend MUST construct a prompt with chapter content + user profile, send to Gemini API

- **FR-033**: Gemini prompt MUST include:
  - Original chapter markdown
  - User's python_level, robotics_experience, math_level, hardware_access, learning_goal
  - Instruction: "Adapt the prose of this educational content for a learner with this background. Adjust complexity, add/remove explanations. Keep ALL code examples exactly as-is — do not modify code logic, imports, or variable names."

- **FR-034**: Backend MUST return `{personalized_content: string}` as markdown

- **FR-035**: Frontend MUST replace chapter display with personalized markdown, maintaining all formatting

- **FR-036**: Personalized view MUST include a "Show Original" button to restore default content

- **FR-037**: If user background data is missing/incomplete, system MUST still attempt personalization using defaults (beginner for all levels)

### API Contracts

#### POST /api/translate

**Purpose**: Translate chapter prose to Urdu while preserving code blocks

**Authentication**: None (public endpoint)

**Request**:
```json
{
  "chapter_slug": "module1-ros2/chapter1-architecture"
}
```

**Response (200 OK)**:
```json
{
  "translated_content": "ROS 2 آرکیٹیکچر کی تعارف...",
  "original_code_blocks": [
    "```python\nimport rclpy\n```",
    "```bash\nros2 run demo_nodes_cpp talker\n```"
  ]
}
```

**Response (400 Bad Request)**:
```json
{
  "detail": "Invalid chapter_slug format"
}
```

**Response (500 Internal Server Error)**:
```json
{
  "detail": "Translation service temporarily unavailable"
}
```

---

#### POST /api/auth/signup

**Purpose**: Create new user account

**Authentication**: None

**Request**:
```json
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

**Response (201 Created)**:
```json
{
  "user_id": 42,
  "email": "student@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "show_questionnaire": true
}
```
**Note**: Token is also set as HTTP-only cookie

**Response (400 Bad Request)**:
```json
{
  "detail": "Email already registered"
}
```

**Response (422 Unprocessable Entity)**:
```json
{
  "detail": "Password must be at least 8 characters"
}
```

---

#### POST /api/auth/signin

**Purpose**: Authenticate existing user

**Authentication**: None

**Request**:
```json
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "user_id": 42,
  "email": "student@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "has_background": true
}
```
**Note**: Token is also set as HTTP-only cookie

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid email or password"
}
```

---

#### POST /api/user/background

**Purpose**: Save user background questionnaire responses

**Authentication**: Required (JWT in cookie)

**Request**:
```json
{
  "python_level": "intermediate",
  "robotics_experience": "student",
  "math_level": "undergraduate",
  "hardware_access": false,
  "learning_goal": "Prepare for robotics internship at tech company"
}
```

**Response (200 OK)**:
```json
{
  "message": "Background saved successfully",
  "user_id": 42
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Authentication required"
}
```

**Response (422 Unprocessable Entity)**:
```json
{
  "detail": "Invalid python_level value. Must be: beginner, intermediate, or advanced"
}
```

---

#### POST /api/personalize

**Purpose**: Generate personalized chapter content based on user background

**Authentication**: Required (JWT in cookie)

**Request**:
```json
{
  "chapter_slug": "module2-simulation/chapter1-gazebo-basics"
}
```

**Response (200 OK)**:
```json
{
  "personalized_content": "# Gazebo Basics\n\n## Learning Objectives\n...[content tailored to user's intermediate Python level and no hardware access]..."
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Authentication required"
}
```

**Response (404 Not Found)**:
```json
{
  "detail": "User background not found. Please complete the questionnaire."
}
```

**Response (500 Internal Server Error)**:
```json
{
  "detail": "Personalization service temporarily unavailable"
}
```

---

### Key Entities

- **User**: Represents a registered learner with email/password credentials and unique identifier. Links to background profile for personalization.

- **User Background**: Stores learning context for a user including skill levels (Python, robotics, math), hardware availability, and learning goals. One-to-one relationship with User.

- **Chapter**: A markdown page containing educational content, code examples, learning objectives, and key takeaways. Identified by unique slug (e.g., "module2-simulation/chapter1-gazebo-basics").

- **Translation**: A transient entity (not persisted) representing Urdu-translated chapter content with preserved code blocks. Generated on-demand via Gemini API.

- **Personalized Content**: A transient entity (not persisted) representing chapter content adapted to a specific user's background. Generated dynamically when user requests personalization.

- **Subagent**: A Claude Code agent definition file that encodes specialized behavior for content creation tasks. Not a database entity, stored as markdown files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 18 chapter pages (6 existing + 12 new) are accessible and load within 2 seconds on desktop/mobile

- **SC-002**: Every new chapter contains minimum 600 words (measured by word count tool)

- **SC-003**: Every new chapter contains exactly 2 or more code examples with syntax highlighting

- **SC-004**: Urdu translation completes within 3 seconds for 95% of requests

- **SC-005**: Translated Urdu text displays correctly in RTL layout on Chrome, Firefox, Safari (desktop + mobile)

- **SC-006**: Users can complete signup + background questionnaire flow in under 90 seconds

- **SC-007**: Background questionnaire data successfully saves to database with 100% accuracy (no dropped fields)

- **SC-008**: Personalization generates adapted content within 5 seconds for 90% of requests

- **SC-009**: Personalized content differs measurably from default (e.g., beginner users get 30%+ more explanatory text than advanced users)

- **SC-010**: All 4 Claude subagents successfully generate outputs when invoked in VS Code with proper inputs

- **SC-011**: Code examples generated by subagents execute without syntax errors

- **SC-012**: JWT authentication prevents unauthorized access to personalization endpoint (returns 401 for invalid/missing tokens)

- **SC-013**: System handles 100 concurrent translation requests without errors or timeouts

- **SC-014**: Mobile users can read Urdu content, sign up, and personalize chapters with identical functionality to desktop

## Clarifications

### Session 2026-03-04

- Q: Which questionnaire fields schema is canonical — spec's 5 fields (python_level, robotics_experience, math_level, hardware_access, learning_goal) or contracts' 3 fields (education_level, field_of_study, robotics_experience)? → A: Spec's 5 fields are canonical. Contracts updated to match.
- Q: Should personalization modify code examples or only prose? (FR-033 said "modify examples", R5 said "maintain ALL code examples") → A: Prose only. Code examples remain unchanged to avoid introducing bugs. FR-033 updated.
- Q: Should the public /api/translate endpoint have rate limiting to prevent Gemini API abuse? → A: Yes, IP-based rate limit of 10 req/min per IP. Returns 429 on excess. Added FR-016a.
- Q: FR-017 still references "better-auth" but research R4 decided on custom AuthProvider.tsx. Which is canonical? → A: Custom AuthProvider.tsx. FR-017 updated to match R4 decision.
- Q: How are the 12 new chapter pages created given Phase A (Content) precedes Phase B (Subagents)? → A: Pages are written manually in Phase A with AI in-chat assistance. Subagents (Phase B) serve as tools for future content maintenance and expansion, not initial creation.
