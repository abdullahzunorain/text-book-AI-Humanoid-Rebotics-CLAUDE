# Data Model: OpenAI Agents SDK with Gemini Models

**Feature**: 005-openai-agents-gemini  
**Date**: 2026-03-06

## Overview

This feature does NOT introduce new database tables or modify existing schemas. The data model describes the in-memory agent architecture that replaces the old `LLMClient` failover chain.

## Entities

### Agent Configuration (in-memory)

Each agent is a configured `agents.Agent` instance. Three agents exist at module level as singletons.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique agent identifier (`tutor`, `personalizer`, `translator`) |
| `instructions` | `str` | System prompt defining agent behavior |
| `model` | `OpenAIChatCompletionsModel` | Model instance pointing at Gemini via OpenAI compat |
| `model_settings` | `ModelSettings` | Temperature, max_tokens per agent |

### Shared OpenAI Client (singleton)

One `AsyncOpenAI` client shared by all agents.

| Field | Type | Source |
|-------|------|--------|
| `api_key` | `str` | `GOOGLE_API_KEY` env var |
| `base_url` | `str` | `https://generativelanguage.googleapis.com/v1beta/openai/` |

### Agent Run Result (per-request)

Returned by `Runner.run()` for each agent invocation.

| Field | Type | Description |
|-------|------|-------------|
| `final_output` | `str` | Generated text (answer, personalized content, or translation) |
| `new_items` | `list` | Conversation items (not used in our single-turn pattern) |
| `usage` | `Usage` | Token usage stats (for logging/monitoring) |

## Existing Database Tables (unchanged)

| Table | Purpose | Modified? |
|-------|---------|-----------|
| `users` | User accounts | No |
| `user_backgrounds` | Learning profiles for personalization | No |
| `content_cache` | Cached personalization/translation results | No |
| `chat_messages` | Chat history storage | No |

## Relationships

```
AsyncOpenAI(Gemini) ──shared──▶ OpenAIChatCompletionsModel
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              TutorAgent        PersonalizationAgent   TranslationAgent
                    │                   │                   │
                    ▼                   ▼                   ▼
             Runner.run()         Runner.run()        Runner.run()
                    │                   │                   │
                    ▼                   ▼                   ▼
              final_output        final_output        final_output
                    │                   │                   │
                    ▼                   ▼                   ▼
           POST /api/chat     POST /api/personalize  POST /api/translate
```

## State Transitions

No new state transitions. Existing cache logic (check → miss → generate → store) remains identical. The only change is the "generate" step now goes through `Runner.run(agent, input=prompt)` instead of `llm_client.generate(prompt=..., system=...)`.
