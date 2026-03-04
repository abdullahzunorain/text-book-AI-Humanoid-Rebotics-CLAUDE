# Data Model: MVP2 — Complete Physical AI Textbook

**Feature**: 002-mvp2-complete-textbook  
**Date**: 2026-03-04  
**Database**: Neon Postgres (new), Qdrant Cloud (existing, unchanged)

## Entity Relationship Diagram

```text
┌─────────────────────┐       1:1       ┌──────────────────────────┐
│       users          │───────────────▶│    user_backgrounds       │
├─────────────────────┤                  ├──────────────────────────┤
│ id          SERIAL PK│                  │ id             SERIAL PK │
│ email    VARCHAR(255)│                  │ user_id     INT FK → users│
│ password_hash  VARCHAR│                  │ python_level   VARCHAR(20)│
│ created_at TIMESTAMP │                  │ robotics_exp   VARCHAR(20)│
│ updated_at TIMESTAMP │                  │ math_level     VARCHAR(20)│
└─────────────────────┘                  │ hardware_access   BOOLEAN │
                                          │ learning_goal      TEXT   │
                                          │ created_at     TIMESTAMP │
                                          │ updated_at     TIMESTAMP │
                                          └──────────────────────────┘

┌─────────────────────┐
│  Chapter (filesystem)│   ← Not a DB table; markdown files in website/docs/
├─────────────────────┤
│ slug (path-based)    │   e.g., "module2-simulation/chapter1-gazebo-basics"
│ content (markdown)   │   Read from website/docs/{slug}.md
│ frontmatter (YAML)   │   title, sidebar_position, etc.
└─────────────────────┘

┌─────────────────────┐
│  Qdrant: book_content│   ← Existing, 55+ points, COSINE distance
├─────────────────────┤
│ id (UUID)            │
│ vector (3072-dim)    │   gemini-embedding-001
│ payload.text         │
│ payload.section      │
│ payload.chapter      │
└─────────────────────┘
```

## SQL Schema (Neon Postgres)

```sql
-- Migration: 001_create_auth_tables.sql
-- Run with: psql $DATABASE_URL -f backend/migrations/001_create_auth_tables.sql

BEGIN;

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User backgrounds table (1:1 with users)
CREATE TABLE IF NOT EXISTS user_backgrounds (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  python_level VARCHAR(20) NOT NULL CHECK (python_level IN ('beginner', 'intermediate', 'advanced')),
  robotics_experience VARCHAR(20) NOT NULL CHECK (robotics_experience IN ('none', 'hobbyist', 'student', 'professional')),
  math_level VARCHAR(20) NOT NULL CHECK (math_level IN ('high_school', 'undergraduate', 'graduate')),
  hardware_access BOOLEAN NOT NULL DEFAULT FALSE,
  learning_goal TEXT CHECK (char_length(learning_goal) <= 200),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_user_backgrounds_user_id UNIQUE(user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_backgrounds_user_id ON user_backgrounds(user_id);

COMMIT;
```

## Entity Details

### users

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | Auto-increment |
| email | VARCHAR(255) | UNIQUE, NOT NULL | RFC 5322 validated in application layer |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash, cost factor 12 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Immutable after creation |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Updated on profile change |

**Validation Rules**:
- Email: Validated against RFC 5322 regex before INSERT
- Password: Minimum 8 characters, enforced in application layer (not DB constraint)
- Email uniqueness: Enforced at DB level (UNIQUE constraint) and application level (check before INSERT)

### user_backgrounds

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | Auto-increment |
| user_id | INTEGER | FK → users(id), UNIQUE, NOT NULL | 1:1 with users, CASCADE delete |
| python_level | VARCHAR(20) | CHECK IN ('beginner', 'intermediate', 'advanced'), NOT NULL | Enum-like |
| robotics_experience | VARCHAR(20) | CHECK IN ('none', 'hobbyist', 'student', 'professional'), NOT NULL | Enum-like |
| math_level | VARCHAR(20) | CHECK IN ('high_school', 'undergraduate', 'graduate'), NOT NULL | Enum-like |
| hardware_access | BOOLEAN | NOT NULL, DEFAULT FALSE | Simple boolean flag |
| learning_goal | TEXT | max 200 chars | Free-form text |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Immutable |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Updated on re-submission |

**Validation Rules**:
- python_level: Must be one of 3 enum values (DB CHECK constraint)
- robotics_experience: Must be one of 4 enum values (DB CHECK constraint)
- math_level: Must be one of 3 enum values (DB CHECK constraint)
- learning_goal: Max 200 characters (DB CHECK constraint)
- user_id: Unique constraint ensures one background per user

### Chapter (Filesystem Entity)

| Property | Source | Notes |
|----------|--------|-------|
| slug | File path relative to `website/docs/` | e.g., `module2-simulation/chapter1-gazebo-basics` |
| title | Frontmatter `title` field | e.g., "Gazebo Basics" |
| sidebar_position | Frontmatter `sidebar_position` field | Ordering within module |
| content | Full markdown text | Read via `open()` |

**No database table** — chapters are static markdown files. Slug is the unique identifier derived from file path.

### Qdrant: book_content (Existing — Unchanged)

| Property | Type | Notes |
|----------|------|-------|
| id | UUID | Generated during indexing |
| vector | float[3072] | gemini-embedding-001 embeddings |
| payload.text | string | Chunk text content |
| payload.section | string | Section heading |
| payload.chapter | string | Chapter name |

**Change in MVP2**: `index_content.py` will be re-run to add new Module 2, 3, 4 chunks. Existing Module 1 data is preserved. Collection grows from ~55 to ~150+ points.

## State Transitions

### User Account Lifecycle
```text
[Anonymous] → signup → [Registered, No Background]
[Registered, No Background] → submit questionnaire → [Registered, Has Background]
[Registered, Has Background] → can personalize chapters
```

### Translation Flow (Stateless)
```text
[Chapter slug] → read file → extract code blocks → Gemini translate prose → re-insert blocks → return
No state persisted. Fresh translation on every request.
```

### Personalization Flow (Stateless per request)
```text
[Chapter slug + JWT] → validate JWT → fetch user_backgrounds → read chapter file → Gemini personalize → return
No state persisted. Fresh personalization on every request.
```
