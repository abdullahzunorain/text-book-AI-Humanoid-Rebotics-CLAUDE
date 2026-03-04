# API Contract: Personalized Chat

**Feature**: 002-mvp2-complete-textbook  
**Phase**: E (Personalization)  
**Authentication**: Required (JWT cookie)

---

## POST /api/personalize

**Purpose**: Enhanced RAG chat that adapts responses based on user's educational background

### Request

```
POST /api/personalize
Content-Type: application/json
Cookie: token=<jwt>
```

```json
{
  "question": "Explain inverse kinematics",
  "chapter_slug": "module-1/forward-kinematics"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| question | string | Yes | Non-empty, max 2000 chars |
| chapter_slug | string | No | Valid chapter slug (e.g. `intro/what-is-robotics`) |

### Responses

**200 OK** — Personalized response generated

```json
{
  "answer": "Since you're an undergraduate in computer science with beginner robotics experience, let me explain inverse kinematics starting from the programming perspective you're familiar with...",
  "sources": [
    {
      "title": "Forward Kinematics",
      "slug": "module-1/forward-kinematics",
      "score": 0.87
    }
  ],
  "personalization_applied": true,
  "profile_summary": "intermediate / student / undergraduate / no-hardware"
}
```

**200 OK** — Fallback (no background saved, acts like `/api/chat`)

```json
{
  "answer": "Inverse kinematics is the process of determining joint parameters...",
  "sources": [...],
  "personalization_applied": false,
  "profile_summary": null
}
```

**401 Unauthorized** — No valid JWT

```json
{
  "detail": "Not authenticated"
}
```

**422 Unprocessable Entity** — Validation failed

```json
{
  "detail": "Question must not be empty"
}
```

**500 Internal Server Error** — AI service failure

```json
{
  "detail": "Failed to generate personalized response"
}
```

### Behavior

1. Extract user_id from JWT cookie
2. Validate question (non-empty, max 2000 chars)
3. Lookup user's background from `user_backgrounds` table
4. Query Qdrant for relevant content (same as `/api/chat`):
   - Embed question with `gemini-embedding-001`
   - Search `book_content` collection (score threshold 0.4)
   - If chapter_slug provided, boost results matching that chapter
5. Build personalized system prompt:
   - If background exists: include education_level, field_of_study, robotics_experience in prompt
   - Adaptation rules per profile (from research.md R5):
     - `high_school` → simpler vocabulary, more analogies
     - `undergraduate` → standard technical depth
     - `graduate` → research-oriented, cite papers
     - `professional` → practical applications focus
   - If no background: use default system prompt (same as `/api/chat`)
6. Call Gemini 2.5 Flash with personalized prompt + context
7. Return response with personalization metadata

### Personalization Prompt Template

```text
You are an AI tutor for "AI and Humanoid Robotics" textbook.

Student Profile:
- Python Level: {python_level}
- Robotics Experience: {robotics_experience}
- Math Level: {math_level}
- Hardware Access: {hardware_access}
- Learning Goal: {learning_goal}

Adaptation Rules:
- If python_level is "beginner": add inline code comments, explain imports
- If python_level is "advanced": focus on architecture patterns, skip basic syntax
- If robotics_experience is "none": add analogies to everyday objects, explain jargon
- If hardware_access is false: replace hardware exercises with simulator alternatives
- If math_level is "high_school": avoid matrix notation, use intuitive explanations
- If learning_goal mentions "job" or "career": add industry context

Context from textbook:
{rag_context}

Question: {question}
```

### Performance

- **p95 latency**: <3s (Qdrant search + Gemini generation)
- Profile lookup adds <10ms overhead vs `/api/chat`

---

## Test Cases

```python
# test_personalize_api.py
def test_personalize_with_background():
    """POST /api/personalize with saved background → 200 + personalization_applied=true"""

def test_personalize_without_background():
    """POST /api/personalize without saved background → 200 + personalization_applied=false (fallback)"""

def test_personalize_with_chapter_slug():
    """POST /api/personalize with chapter_slug → 200 + relevant sources"""

def test_personalize_empty_question():
    """POST /api/personalize with empty question → 422"""

def test_personalize_unauthenticated():
    """POST /api/personalize without JWT → 401"""

def test_personalize_adapts_for_beginner_python():
    """POST /api/personalize for beginner python_level → response adds code comments and explanations"""

def test_personalize_adapts_for_no_hardware():
    """POST /api/personalize for hardware_access=false → hardware exercises replaced with simulator alternatives"""
```
