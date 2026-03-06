# Data Model: Physical AI & Humanoid Robotics Textbook Platform

**Feature Branch**: `004-physical-ai-textbook`  
**Date**: 2026-03-06  
**Status**: Complete

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    users     │       │ user_backgrounds │       │  content_cache   │
├──────────────┤       ├──────────────────┤       ├──────────────────┤
│ id PK        │──1:1─▶│ id PK            │       │ id PK            │
│ email UNIQUE │       │ user_id FK → users│◀──┐  │ user_id FK →users│
│ password_hash│       │ python_level     │   │  │ chapter_slug     │
│ created_at   │       │ robotics_exp     │   │  │ cache_type       │
│ updated_at   │       │ math_level       │   │  │ content          │
└──────┬───────┘       │ hardware_access  │   │  │ metadata JSONB   │
       │               │ learning_goal    │   │  │ created_at       │
       │               │ created_at       │   │  │ updated_at       │
       │               │ updated_at       │   │  └──────────────────┘
       │               └──────────────────┘   │     UNIQUE(user_id,
       │                                      │     chapter_slug,
       │               ┌──────────────────┐   │     cache_type)
       └──────1:N─────▶│  chat_messages   │   │
                       ├──────────────────┤   │
                       │ id PK            │   │
                       │ user_id FK →users│───┘
                       │ question TEXT    │
                       │ answer TEXT      │
                       │ selected_text    │
                       │ sources JSONB    │
                       │ created_at       │
                       └──────────────────┘
```

---

## Existing Tables

### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing user ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes**: `idx_users_email` on `email`

**Migration**: `001_create_auth_tables.sql` (exists)

---

### `user_backgrounds`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | INTEGER | FK → users(id) ON DELETE CASCADE, UNIQUE | One background per user |
| python_level | VARCHAR(20) | NOT NULL, CHECK IN ('beginner', 'intermediate', 'advanced') | Self-reported Python skill |
| robotics_experience | VARCHAR(20) | NOT NULL, CHECK IN ('none', 'hobbyist', 'student', 'professional') | Robotics background |
| math_level | VARCHAR(20) | NOT NULL, CHECK IN ('high_school', 'undergraduate', 'graduate') | Math proficiency |
| hardware_access | BOOLEAN | NOT NULL, DEFAULT FALSE | Access to physical hardware |
| learning_goal | TEXT | CHECK char_length ≤ 200 | Free-text learning goal |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Profile creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last profile update time |

**Indexes**: `idx_user_backgrounds_user_id` on `user_id`

**Migration**: `001_create_auth_tables.sql` (exists)

**State transitions**: Created on first `POST /api/user/background`. Updated via `INSERT ... ON CONFLICT DO UPDATE` (UPSERT) on subsequent submissions. When updated, triggers `DELETE FROM content_cache WHERE user_id = $1 AND cache_type = 'personalization'`.

---

## New Tables

### `content_cache`

Stores AI-generated personalized and translated chapter content per user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | INTEGER | FK → users(id) ON DELETE CASCADE, NOT NULL | Owning user |
| chapter_slug | VARCHAR(200) | NOT NULL | Chapter path (e.g., `module1-ros2/architecture`) |
| cache_type | VARCHAR(20) | NOT NULL, CHECK IN ('personalization', 'translation') | Type discriminator |
| content | TEXT | NOT NULL | Full AI-generated markdown content |
| metadata | JSONB | DEFAULT '{}' | Additional metadata (provider used, generation time, etc.) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Cache entry creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Unique constraint**: `UNIQUE(user_id, chapter_slug, cache_type)`

**Indexes**: `idx_content_cache_lookup` on `(user_id, chapter_slug, cache_type)`

**Validation rules**:
- `chapter_slug` must match `^[a-zA-Z0-9/_-]+$` (validated at route level)
- `cache_type` must be exactly `'personalization'` or `'translation'`
- `content` must not be empty

**Invalidation rules**:
- **Personalization**: Invalidated (DELETE) when user updates background profile
- **Translation**: Never invalidated (Urdu translation is profile-independent)

**Migration**: `002_add_cache_and_chat.sql` (NEW)

```sql
CREATE TABLE IF NOT EXISTS content_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_slug VARCHAR(200) NOT NULL,
    cache_type VARCHAR(20) NOT NULL CHECK (cache_type IN ('personalization', 'translation')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, chapter_slug, cache_type)
);

CREATE INDEX IF NOT EXISTS idx_content_cache_lookup 
    ON content_cache(user_id, chapter_slug, cache_type);
```

---

### `chat_messages`

Stores persistent chat history (questions and AI answers) per user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing message ID |
| user_id | INTEGER | FK → users(id) ON DELETE CASCADE, NOT NULL | Owning user |
| question | TEXT | NOT NULL | User's question |
| answer | TEXT | NOT NULL | AI-generated answer |
| selected_text | TEXT | NULLABLE | Text the user highlighted (for selected-text Q&A) |
| sources | JSONB | DEFAULT '[]' | Array of source references from RAG retrieval |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Message timestamp |

**Indexes**: `idx_chat_messages_user` on `(user_id, created_at DESC)` — optimized for newest-first retrieval

**Validation rules**:
- `question` must not be empty (validated at route level, max 2000 chars per FR-008)
- `answer` must not be empty
- `selected_text` max 2000 chars (validated at route level)
- `sources` must be valid JSON array

**Retention**: Indefinite — no TTL, no expiry, no cleanup (per clarification session)

**Migration**: `002_add_cache_and_chat.sql` (NEW)

```sql
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    selected_text TEXT,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user 
    ON chat_messages(user_id, created_at DESC);
```

---

## Vector Store (Qdrant Cloud)

### Collection: `book_content`

| Property | Value |
|----------|-------|
| Vector size | 3072 (gemini-embedding-001 output) |
| Distance | Cosine |
| Score threshold | 0.4 (retrieval filter) |
| Max results | 5 per query |

### Point Payload Schema

| Field | Type | Description |
|-------|------|-------------|
| text | string | Chunk text content (≤500 tokens) |
| chapter | string | Chapter filename without .md extension |
| module | string | Module identifier (e.g., `module1-ros2`) |
| page_title | string | Extracted from frontmatter `title:` |
| heading | string | H2/H3 heading for this chunk |
| chapter_slug | string | **NEW** — Relative path for cache key matching |

---

## Complete Migration: `002_add_cache_and_chat.sql`

```sql
-- Migration: 002_add_cache_and_chat.sql
-- Purpose: Add content caching and chat history tables
-- Run with: psql $DATABASE_URL -f backend/migrations/002_add_cache_and_chat.sql

BEGIN;

-- Content cache: stores AI-generated personalized/translated chapter content
CREATE TABLE IF NOT EXISTS content_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_slug VARCHAR(200) NOT NULL,
    cache_type VARCHAR(20) NOT NULL CHECK (cache_type IN ('personalization', 'translation')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, chapter_slug, cache_type)
);

-- Chat messages: persistent chat history per user
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    selected_text TEXT,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_content_cache_lookup 
    ON content_cache(user_id, chapter_slug, cache_type);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user 
    ON chat_messages(user_id, created_at DESC);

COMMIT;
```

---

## Data Flow Summary

### Personalization Flow (with cache)

```
POST /api/personalize {chapter_slug}
    │
    ├─ Auth: extract user_id from JWT cookie
    │
    ├─ Cache check: SELECT content FROM content_cache
    │  WHERE user_id=$1 AND chapter_slug=$2 AND cache_type='personalization'
    │
    ├─ [CACHE HIT] → Return cached content
    │
    └─ [CACHE MISS] → 
       ├─ Fetch user background from user_backgrounds
       ├─ Read chapter markdown from website/docs/
       ├─ Build prompt → LLMClient.generate()
       ├─ INSERT INTO content_cache (UPSERT)
       └─ Return fresh content
```

### Profile Update → Cache Invalidation

```
POST /api/user/background {profile_data}
    │
    ├─ Auth: extract user_id from JWT cookie
    │
    ├─ UPSERT into user_backgrounds
    │
    ├─ DELETE FROM content_cache 
    │  WHERE user_id=$1 AND cache_type='personalization'
    │
    └─ Return success
```

### Chat with History Persistence

```
POST /api/chat {question, selected_text?}
    │
    ├─ RAG pipeline: embed → retrieve → generate (via LLMClient)
    │
    ├─ [If authenticated] → INSERT INTO chat_messages
    │  (user_id, question, answer, selected_text, sources)
    │
    └─ Return {answer, sources}


GET /api/chat/history?limit=50&offset=0
    │
    ├─ Auth: extract user_id from JWT cookie
    │
    ├─ SELECT * FROM chat_messages
    │  WHERE user_id=$1
    │  ORDER BY created_at DESC
    │  LIMIT $2 OFFSET $3
    │
    └─ Return [{id, question, answer, selected_text, sources, created_at}, ...]
```
