# Research: MVP2 — Complete Physical AI Textbook

**Feature**: 002-mvp2-complete-textbook  
**Date**: 2026-03-04  
**Status**: Complete

## Research Tasks

### R1: Neon Postgres + asyncpg Connection from FastAPI

**Context**: MVP1 had no relational database. MVP2 needs user accounts and background profiles stored in Neon Postgres. Need to understand asyncpg connection pooling with FastAPI's async lifecycle.

**Decision**: Use `asyncpg` with manual pool management via FastAPI lifespan events.

**Rationale**:
- asyncpg is the fastest Python async PostgreSQL driver (~3x faster than psycopg2 async)
- Neon Postgres supports standard PostgreSQL wire protocol — asyncpg connects natively
- FastAPI's `lifespan` context manager is the recommended pattern for connection pool lifecycle
- Pool created on startup, closed on shutdown — no leaked connections

**Implementation Pattern**:
```python
# backend/db.py
import asyncpg
from contextlib import asynccontextmanager

_pool: asyncpg.Pool | None = None

async def init_pool(dsn: str, min_size: int = 2, max_size: int = 10):
    global _pool
    _pool = await asyncpg.create_pool(dsn, min_size=min_size, max_size=max_size)

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()

async def get_pool() -> asyncpg.Pool:
    assert _pool is not None, "DB pool not initialized"
    return _pool
```

**Alternatives Considered**:
- **psycopg2 (sync)**: Rejected — blocks async event loop, incompatible with FastAPI's async nature
- **SQLAlchemy async**: Rejected — over-complex for 2 tables. Direct SQL with asyncpg is simpler and faster
- **Prisma Python**: Rejected — experimental Python client, immature ecosystem
- **Neon serverless driver (@neondatabase/serverless)**: JS-only, not applicable to Python backend

**Neon-Specific Notes**:
- Connection string format: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`
- Neon requires SSL (`sslmode=require`) — asyncpg handles this with `ssl=True` parameter
- Free tier: 0.5 GB storage, 500 MB data transfer/month — sufficient for MVP2 user base
- Connection pooling: Neon has built-in connection pooler on port 5432 (transaction mode)

---

### R2: JWT Authentication with python-jose + passlib

**Context**: Need stateless JWT authentication for personalization endpoints. Frontend sends JWT in HTTP-only cookie.

**Decision**: Use `python-jose[cryptography]` for JWT encoding/decoding and `passlib[bcrypt]` for password hashing.

**Rationale**:
- python-jose is the de facto Python JWT library, well-maintained, type-hinted
- passlib provides bcrypt with configurable cost factor — security best practice
- HTTP-only cookies prevent XSS token theft (cannot be read by JavaScript)
- HS256 algorithm is sufficient for single-backend architecture (no need for RS256 key pairs)

**Implementation Pattern**:
```python
# backend/auth_utils.py
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # min 256-bit
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**Cookie Strategy**:
- Set cookie: `Set-Cookie: token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800`
- Read cookie: FastAPI `Request.cookies.get("token")`
- Clear cookie on signout: Set `Max-Age=0`
- `SameSite=Lax` allows cookie to be sent on top-level navigations from GitHub Pages to API
- `Secure` flag requires HTTPS — enforce on production (Railway), skip on localhost dev

**CORS Update Required**:
- Add `allow_credentials=True` to CORS middleware (enables cookie sending)
- Change `allow_origins` from wildcard to explicit list (required when credentials=True)

**Alternatives Considered**:
- **PyJWT**: Viable but python-jose has better error handling and cryptography backend
- **localStorage token**: Rejected — vulnerable to XSS attacks
- **Session-based auth**: Rejected — requires server-side session state, violates stateless principle
- **OAuth/Passport**: Rejected — over-complex for email/password only auth

---

### R3: Gemini Translation with Code Block Preservation

**Context**: Need to translate chapter prose to Urdu while keeping code blocks in English. Must handle markdown structure without corrupting it.

**Decision**: Pre-extract code blocks → translate prose → re-insert code blocks. Use Gemini gemini-2.5-flash with structured prompt.

**Rationale**:
- Extracting code blocks before translation prevents Gemini from translating variable names, imports, etc.
- Regex extraction of fenced code blocks (```...```) is reliable for markdown
- Re-insertion by index preserves original code block order
- gemini-2.5-flash is fast (1-2s for translation) and cost-effective

**Implementation Pattern**:
```python
# backend/services/translation_service.py
import re
from google import genai

CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```')

def extract_code_blocks(markdown: str) -> tuple[str, list[str]]:
    """Replace code blocks with placeholders, return prose + blocks."""
    blocks = CODE_BLOCK_PATTERN.findall(markdown)
    prose = CODE_BLOCK_PATTERN.sub('{{CODE_BLOCK}}', markdown)
    return prose, blocks

def translate_to_urdu(chapter_markdown: str) -> dict:
    prose, code_blocks = extract_code_blocks(chapter_markdown)
    
    prompt = f"""Translate the following educational text to Urdu.
    Rules:
    - Translate all prose to natural, readable Urdu
    - Keep technical terms (ROS 2, Gazebo, Python, etc.) in English
    - Keep {{{{CODE_BLOCK}}}} placeholders exactly as-is, do not translate them
    - Maintain markdown formatting (headers, bold, lists)
    
    Text:
    {prose}"""
    
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={'max_output_tokens': 4096, 'temperature': 0.3}
    )
    
    translated = response.text
    # Re-insert code blocks
    for block in code_blocks:
        translated = translated.replace('{{CODE_BLOCK}}', block, 1)
    
    return {"translated_content": translated, "original_code_blocks": code_blocks}
```

**RTL Rendering Strategy**:
- Load Noto Nastaliq Urdu via Google Fonts CDN (no self-hosting needed)
- Scoped CSS class `.urdu-content` with `direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif;`
- Code blocks within RTL div keep `direction: ltr` override (code reads left-to-right always)
- Dark mode: Same font, Docusaurus dark theme handles background/foreground switching

**Alternatives Considered**:
- **Google Translate API**: Rejected — worse quality for technical Urdu than Gemini, requires separate API key
- **Full-page translation (no extraction)**: Rejected — Gemini translates code comments, variable names
- **Pre-translated static pages**: Rejected — spec says dynamic translation, 12+ pages would be unmaintainable
- **Client-side translation**: Rejected — exposes API key, slow on mobile

---

### R4: better-auth Client Integration with Docusaurus

**Context**: Need authentication UI in Docusaurus React app. better-auth is a modern auth client library.

**Decision**: Use better-auth client library for frontend auth flows, backed by our custom FastAPI JWT endpoints (not better-auth server).

**Rationale**:
- better-auth provides pre-built React hooks for auth state management
- It can work with any backend that follows standard auth patterns (our FastAPI JWT)
- Reduces frontend auth boilerplate (signup forms, token management, auth context)

**Risk Finding**: better-auth is designed to work with its own server-side package. Using it as a pure client against custom FastAPI endpoints may require configuration workarounds.

**Fallback Plan**: If better-auth integration proves difficult, build a lightweight custom `AuthProvider.tsx` with React Context that:
- Stores auth state (user, token) in memory
- Provides `signup()`, `signin()`, `signout()` methods that call FastAPI endpoints
- Reads JWT from HTTP-only cookie (cookie set by backend, not readable by JS — presence checked via `/api/auth/me` endpoint)
- This is ~100 lines of code and avoids any library dependency issues

**Decision Update**: **Prefer the custom AuthProvider approach** as the primary implementation. better-auth adds a dependency with uncertain compatibility. The custom approach is:
- Fully controlled, no version risk
- ~100 LOC vs library + config
- Directly matches our FastAPI JWT contract

**Alternatives Considered**:
- **Auth0/Firebase Auth**: Rejected — external dependency, overkill for email/password
- **NextAuth**: Rejected — Next.js only
- **Supabase Auth**: Rejected — requires Supabase backend, we use Neon Postgres

---

### R5: Gemini Personalization Prompt Engineering

**Context**: Need to send chapter content + user background profile to Gemini and get adapted educational content back.

**Decision**: Use a structured prompt with explicit adaptation instructions keyed to user profile fields.

**Rationale**:
- Structured prompts with field-specific instructions produce consistent, targeted output
- Temperature 0.3 keeps output focused and deterministic
- max_output_tokens=4096 is sufficient for a full chapter (~1000 words)
- Including the original chapter as context ensures personalization stays on-topic

**Prompt Template**:
```text
You are an educational content adapter for a Physical AI & Humanoid Robotics textbook.

Student Profile:
- Python Level: {python_level}
- Robotics Experience: {robotics_experience}
- Math Level: {math_level}
- Hardware Access: {hardware_access}
- Learning Goal: {learning_goal}

Adaptation Rules:
1. If python_level is "beginner": add inline code comments, explain imports, show expected output
2. If python_level is "advanced": focus on architecture patterns, skip basic syntax
3. If robotics_experience is "none": add analogies to everyday objects, explain jargon
4. If hardware_access is false: replace hardware exercises with simulator alternatives
5. If math_level is "high_school": avoid matrix notation, use intuitive explanations
6. If learning_goal mentions "job" or "career": add industry context, interview tips
7. Maintain ALL code examples, headers, and learning objectives from original
8. Keep key takeaways section but adapt to student's context
9. Output complete markdown, not a diff

Original Chapter:
{chapter_markdown}

Generate the personalized version:
```

**Alternatives Considered**:
- **Fine-tuned model**: Rejected — requires training data, maintenance overhead, overkill for MVP
- **Multiple small prompts (per-section)**: Rejected — more API calls, higher latency, context loss between sections
- **RAG-based personalization**: Rejected — adds complexity, user profile is small enough to fit in prompt context

---

### R6: Docusaurus Chapter Slug Resolution

**Context**: API endpoints receive `chapter_slug` (e.g., "module2-simulation/chapter1-gazebo-basics") and need to find the corresponding markdown file on disk. Backend reads file content for translation/personalization.

**Decision**: Direct filesystem path mapping from slug to markdown file.

**Rationale**:
- Docusaurus docs are markdown files in `website/docs/` directory
- Slug directly maps to file path: `website/docs/{slug}.md`
- No database lookup needed — filesystem is the source of truth
- Backend already has access to repository root (same machine or Docker volume)

**Implementation**:
```python
import os
DOCS_ROOT = os.path.join(os.path.dirname(__file__), '..', 'website', 'docs')

def read_chapter(slug: str) -> str:
    """Read chapter markdown by slug. Raises FileNotFoundError if not found."""
    safe_slug = slug.replace('..', '').strip('/')  # prevent path traversal
    path = os.path.join(DOCS_ROOT, f"{safe_slug}.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Chapter not found: {slug}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

**Security**: Path traversal prevention via `..` stripping. Slug is validated against `^[a-zA-Z0-9/_-]+$` regex.

---

### R7: Claude Code Subagent Best Practices

**Context**: Need 4 subagent definition files in `.claude/agents/` directory for content creation workflows.

**Decision**: Each subagent is a markdown file with structured sections: Role, Input Format, Output Format, Behavioral Guidelines, Examples.

**Rationale**:
- Claude Code agents are driven by markdown instruction files
- Structured format ensures consistent agent behavior
- Version numbers enable tracking of prompt improvements
- Examples in the definition help Claude generate on-pattern outputs

**Agent Specifications**:

1. **content-writer.md**: Generates full chapter markdown with learning objectives, prose (600+ words), 2 code examples, key takeaways. Input: module name + chapter topic. Output: complete .md file.

2. **code-example-generator.md**: Creates working Python/Bash code snippets for robotics topics. Input: topic + framework (ROS 2, Isaac, etc.). Output: fenced code blocks with comments and expected output.

3. **urdu-translator.md**: Translates educational prose to Urdu while preserving markdown and code blocks. Input: English markdown text. Output: Urdu markdown with RTL formatting notes.

4. **content-personalizer.md**: Adapts chapter content for a specific learner profile. Input: chapter markdown + user profile fields. Output: personalized chapter markdown.

---

### R8: Neon Postgres Free Tier Limits

**Context**: Using Neon Postgres for new auth tables. Need to ensure free tier is sufficient.

**Decision**: Neon free tier is adequate for MVP2.

**Findings**:
- Storage: 0.5 GB free — users + user_backgrounds tables will use <1 MB for 10,000 users
- Compute: 0.25 vCPU, suspends after 5 min idle — acceptable for MVP (cold start ~1-2s on first query)
- Branching: 1 branch free — use for dev/staging
- Connection limit: 100 concurrent — more than sufficient for ~100 concurrent users
- Data transfer: 5 GB/month free — well within budget for auth queries

**Connection String Setup**:
- Environment variable: `DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`
- Add to `.env` (local) and Railway environment variables (production)

---

## Summary of Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| Database | asyncpg + Neon Postgres | Async-native, fastest Python PG driver, Neon free tier sufficient |
| Authentication | python-jose JWT + passlib bcrypt | Stateless, HTTP-only cookies, no external auth service |
| Translation | Code-block extraction + Gemini prompt | Preserves code in English, reliable placeholder-based approach |
| Auth UI | Custom AuthProvider.tsx (not better-auth) | Simpler, fully controlled, no compatibility risk |
| Personalization | Single structured Gemini prompt | Profile-keyed adaptation rules, consistent output |
| Chapter Resolution | Direct filesystem path mapping | No DB needed, slug → file path, path traversal protected |
| Subagents | Structured markdown definitions | Claude Code convention, versioned, with examples |
| Database hosting | Neon Postgres free tier | 0.5 GB storage, 100 connections, sufficient for MVP2 |
