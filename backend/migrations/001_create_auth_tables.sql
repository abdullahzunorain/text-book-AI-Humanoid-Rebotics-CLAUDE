-- Migration: 001_create_auth_tables.sql
-- Purpose: Create users and user_backgrounds tables for authentication and personalization
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
