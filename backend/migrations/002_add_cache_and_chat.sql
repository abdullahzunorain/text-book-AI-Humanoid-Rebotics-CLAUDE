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
