# API Contracts: Physical AI & Humanoid Robotics Textbook Platform

**Feature Branch**: `004-physical-ai-textbook`  
**Date**: 2026-03-06  
**Base URL**: `https://<railway-app>.up.railway.app` (production) | `http://localhost:8000` (dev)
**Auth**: JWT in httpOnly cookie named `token`

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Request**:
```json
{
  "email": "student@example.com",
  "password": "securepass123"
}
```

**Validation**:
- `email`: valid email format (Pydantic `EmailStr`)
- `password`: minimum 8 characters

**Response 201**:
```json
{
  "user_id": 1,
  "email": "student@example.com",
  "has_background": false
}
```
Sets `token` httpOnly cookie (JWT, 7-day expiry).

**Response 400**: `{"detail": "Email already registered"}`  
**Response 422**: Validation error (invalid email, short password)

---

### POST /api/auth/signin

Authenticate an existing user.

**Request**:
```json
{
  "email": "student@example.com",
  "password": "securepass123"
}
```

**Response 200**:
```json
{
  "user_id": 1,
  "email": "student@example.com",
  "has_background": true
}
```
Sets `token` httpOnly cookie.

**Response 401**: `{"detail": "Invalid email or password"}`

---

### POST /api/auth/signout

End the current session.

**Auth**: Required (JWT cookie)

**Response 200**:
```json
{"message": "Signed out"}
```
Clears `token` cookie.

---

### GET /api/auth/me

Get current authenticated user.

**Auth**: Required (JWT cookie)

**Response 200**:
```json
{
  "user_id": 1,
  "email": "student@example.com",
  "has_background": true
}
```

**Response 401**: `{"detail": "not_authenticated"}` | `{"detail": "session_expired"}` | `{"detail": "invalid_token"}`

---

### POST /api/user/background

Save or update user background profile. **Triggers personalization cache invalidation.**

**Auth**: Required (JWT cookie)

**Request**:
```json
{
  "python_level": "beginner",
  "robotics_experience": "none",
  "math_level": "high_school",
  "hardware_access": false,
  "learning_goal": "Prepare for robotics internship"
}
```

**Validation**:
- `python_level`: one of `beginner`, `intermediate`, `advanced`
- `robotics_experience`: one of `none`, `hobbyist`, `student`, `professional`
- `math_level`: one of `high_school`, `undergraduate`, `graduate`
- `hardware_access`: boolean
- `learning_goal`: string, max 200 characters

**Response 200**:
```json
{"message": "Background saved"}
```

**Side effect**: `DELETE FROM content_cache WHERE user_id = $1 AND cache_type = 'personalization'`

**Response 401**: Not authenticated  
**Response 422**: Validation error

---

## RAG Chatbot Endpoints

### POST /api/chat

Ask the RAG chatbot a question about the textbook.

**Auth**: Optional (if authenticated, chat history is saved)

**Request**:
```json
{
  "question": "What is ROS 2?",
  "selected_text": null
}
```

**Validation**:
- `question`: 1-2000 characters, non-empty after trim
- `selected_text`: nullable, max 2000 characters

**Response 200**:
```json
{
  "answer": "ROS 2 (Robot Operating System 2) is an open-source middleware framework...",
  "sources": [
    "ROS 2 Architecture — What is ROS 2?",
    "ROS 2 Architecture — Key Features"
  ]
}
```

**Response 400**: `{"detail": "Question cannot be empty"}`  
**Response 429**: `{"detail": "AI service rate limit reached. Please wait a moment and try again."}` (includes `Retry-After: 60` header)  
**Response 503**: `{"detail": "Service temporarily unavailable. Please try again later."}` (all LLM providers exhausted)

**Side effect (when authenticated)**: Inserts row into `chat_messages` with question, answer, selected_text, sources.

---

### GET /api/chat/history — **NEW**

Retrieve chat history for the authenticated user.

**Auth**: Required (JWT cookie)

**Query Parameters**:
- `limit`: integer, default 50, max 100
- `offset`: integer, default 0

**Response 200**:
```json
{
  "messages": [
    {
      "id": 42,
      "question": "What is ROS 2?",
      "answer": "ROS 2 is an open-source middleware...",
      "selected_text": null,
      "sources": ["ROS 2 Architecture — What is ROS 2?"],
      "created_at": "2026-03-06T14:30:00Z"
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

Messages are ordered newest-first (`created_at DESC`).

**Response 401**: Not authenticated

---

## Content Endpoints

### POST /api/personalize

Personalize a chapter for the authenticated user based on their background profile.

**Auth**: Required (JWT cookie)

**Request**:
```json
{
  "chapter_slug": "module1-ros2/architecture"
}
```

**Validation**:
- `chapter_slug`: 1-200 characters, matches `^[a-zA-Z0-9/_-]+$`

**Response 200**:
```json
{
  "personalized_content": "# ROS 2 Architecture\n\nSince you're just starting with Python..."
}
```

Serves from `content_cache` on cache hit; generates fresh on cache miss.

**Response 401**: Not authenticated  
**Response 404**: `{"detail": "Chapter not found"}`  
**Response 429**: `{"detail": "AI service rate limit reached. Please wait a moment and try again."}`  
**Response 500**: `{"detail": "Personalization service temporarily unavailable"}`

---

### POST /api/translate

Translate a chapter to Urdu.

**Auth**: Required (JWT cookie) — per FR-022

**Request**:
```json
{
  "chapter_slug": "module1-ros2/architecture"
}
```

**Validation**:
- `chapter_slug`: 1-200 characters, matches `^[a-zA-Z0-9/_-]+$`

**Response 200**:
```json
{
  "translated_content": "# ROS 2 فن تعمیر\n\nROS 2 ایک اوپن سورس مڈل ویئر...",
  "original_code_blocks": [
    "```python\nimport rclpy\n```"
  ]
}
```

Serves from `content_cache` on cache hit; generates fresh on cache miss. IP-based rate limit: 10 req/min.

**Response 401**: Not authenticated  
**Response 429**: Rate limit exceeded (IP-based or LLM rate limit)  
**Response 503**: AI service unavailable

---

## Utility Endpoints

### GET /

API information.

**Response 200**:
```json
{
  "service": "Physical AI Textbook RAG API",
  "version": "2.0.0",
  "endpoints": {
    "health": "GET /health",
    "chat": "POST /api/chat",
    "chat_history": "GET /api/chat/history",
    "translate": "POST /api/translate",
    "auth": "POST /api/auth/signup | /signin | /signout, GET /api/auth/me",
    "personalize": "POST /api/personalize",
    "background": "POST /api/user/background"
  }
}
```

### GET /health

**Response 200**: `{"status": "ok"}`

---

## Error Taxonomy

| HTTP Status | Code | Meaning |
|-------------|------|---------|
| 400 | Bad Request | Invalid input (empty question, invalid slug format, etc.) |
| 401 | Unauthorized | `not_authenticated` / `session_expired` / `invalid_token` |
| 404 | Not Found | Chapter slug doesn't resolve to a file |
| 422 | Unprocessable Entity | Pydantic validation failure (wrong types, out-of-range values) |
| 429 | Too Many Requests | IP rate limit or LLM rate limit. Includes `Retry-After` header |
| 500 | Internal Server Error | Unexpected failure in AI service |
| 503 | Service Unavailable | All LLM providers exhausted after retries |

---

## Cookie Contract

| Attribute | Development | Production |
|-----------|-------------|------------|
| Name | `token` | `token` |
| HttpOnly | `true` | `true` |
| Secure | `false` | `true` |
| SameSite | `lax` | `none` |
| Path | `/` | `/` |
| Max-Age | 604800 (7 days) | 604800 (7 days) |

Environment determined by `APP_ENV` environment variable (`production` or default `development`).

---

## Versioning

- Current API version: implicit (no URL prefix versioning)
- Breaking changes: not expected at hackathon scale
- Future: consider `/api/v2/` prefix if public API is exposed

## Idempotency

- `POST /api/auth/signup`: NOT idempotent (returns 400 on duplicate email)
- `POST /api/user/background`: Idempotent (UPSERT semantics)
- `POST /api/chat`: NOT idempotent (generates new answer each time unless cached)
- `POST /api/personalize`: Effectively idempotent when cache hit
- `POST /api/translate`: Effectively idempotent when cache hit
- `GET /api/chat/history`: Idempotent (read-only)

## Timeouts

- Client-side: 30s timeout on all fetch requests (frontend)
- Backend-to-LLM: 60s timeout per provider attempt
- Backend-to-Qdrant: 60s timeout (configured in `QdrantClient`)
- Backend-to-Neon: connection pool with 10s timeout (asyncpg default)
