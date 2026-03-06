# Implementation Plan: Fix Cookie-Based Auth Persistence

**Branch**: `003-fix-auth-cookie-persistence` | **Date**: 2026-03-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-fix-auth-cookie-persistence/spec.md`

## Summary

JWT cookies are set with hardcoded `secure=True` and `samesite="lax"` in `routes/auth.py`, breaking authentication on HTTP localhost (browser silently drops the cookie) and on production cross-site requests (GitHub Pages → Railway requires `SameSite=None`). The fix introduces a centralized `cookie_config.py` module that resolves cookie attributes dynamically based on `APP_ENV` and an HTTPS origin auto-detect guard. CORS origins move from a hardcoded list to the `CORS_ORIGINS` env var. The `decode_token` path distinguishes expired vs malformed JWTs for distinct 401 detail codes.

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI 0.115+, python-jose (JWT HS256), bcrypt, asyncpg, Docusaurus 3.9.2, React 19
**Storage**: Neon PostgreSQL (asyncpg), Qdrant Cloud (vector DB — unaffected by this change)
**Testing**: pytest + pytest-asyncio (7 test files, ~47 tests). TestClient + AsyncMock pattern.
**Target Platform**: Linux server (Railway, HTTPS) + static site (GitHub Pages, HTTPS)
**Project Type**: Web application (API backend + static frontend)
**Performance Goals**: No performance impact — configuration-only change at startup + per-response cookie header
**Constraints**: Must not break existing 47 tests. Must not regress production security. Must be test-driven.
**Scale/Scope**: 5 backend files touched, 1 new module, 1 new test file, 0-1 frontend files touched

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. MVP-First | **PASS** | Bug fix — unblocks authenticated features already shipped in MVP2 |
| II. No Auth | **N/A** | Auth was added post-constitution in MVP2. This fixes a bug in that addition |
| III. Content Scope | **PASS** | No content changes |
| IV. Chatbot Omnipresence | **PASS** | Chatbot unaffected |
| V. Deployability | **PASS** | Smallest viable diff — environment-driven config, no new services |
| VI. No Over-Engineering | **PASS** | One new module (cookie_config.py), no custom frameworks, no new dependencies |
| Tech Stack | **PASS** | Python + FastAPI, no new languages or frameworks |
| No Hardcoded Secrets | **PASS** | All config via `.env` / env vars |

**Result**: All gates PASS. No constitution violations requiring justification.

**Post-Phase 1 Re-check**: PASS — design introduces exactly one new Python module and reads existing env vars. No architectural drift.

---

## Implementation Scope

### Task Table

| ID | Task | Files | Type |
|----|------|-------|------|
| T1 | Environment-aware cookie config module | `backend/cookie_config.py` (new) | Core |
| T2 | Environment-driven CORS origins | `backend/main.py` | Core |
| T3 | HTTPS auto-detect guard (FR-011) | `backend/cookie_config.py` | Safety |
| T4 | Cookie set/clear use shared config | `backend/routes/auth.py` | Core |
| T5 | Distinct 401 error details | `backend/routes/auth.py`, `backend/auth_utils.py` | Core |
| T6 | Frontend `credentials: 'include'` audit | `website/src/components/*.tsx` | Verify |
| T7 | Frontend API_URL config audit | `website/src/components/*.tsx`, `docusaurus.config.ts` | Verify |
| T8 | Unit tests: cookie_config | `backend/tests/test_cookie_config.py` (new) | Test |
| T9 | Unit tests: auth API cookie attrs | `backend/tests/test_auth_api.py` | Test |
| T10 | Update .env with CORS_ORIGINS | `backend/.env` | Config |
| T11 | Documentation & quickstart | `specs/003-*/quickstart.md` | Docs |

### Environment Configuration

#### Development (`backend/.env`)

```env
APP_ENV=development
JWT_SECRET=<secret>
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Cookie result: `Secure=False`, `SameSite=Lax`, `HttpOnly=True`, `Path=/`, `Max-Age=604800`

#### Production (Railway env vars)

```env
APP_ENV=production
JWT_SECRET=<production-secret>
CORS_ORIGINS=https://abdullahzunorain.github.io
```

Cookie result: `Secure=True`, `SameSite=None`, `HttpOnly=True`, `Path=/`, `Max-Age=604800`

#### Auto-Detect Override (FR-011)

If `CORS_ORIGINS` contains any `https://` origin AND `APP_ENV=development`:
- Force `Secure=True`, `SameSite=None`
- Log warning: `"HTTPS origin detected with APP_ENV=development — forcing Secure cookies"`

---

## Detailed Design

### T1: `backend/cookie_config.py` (new module)

```python
# Public API
def get_cookie_config() -> dict:
    """Returns {secure: bool, samesite: str, httponly: bool, path: str, max_age: int}"""
```

**Logic**:
1. Read `APP_ENV` from `os.getenv("APP_ENV", "development")`
2. Read `CORS_ORIGINS` from `os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")`
3. Parse origins: `[o.strip() for o in cors_origins.split(",") if o.strip()]`
4. HTTPS auto-detect: `has_https = any(o.startswith("https://") for o in origins)`
5. If `app_env == "production"` OR `has_https`: `secure=True, samesite="none"`
6. Else: `secure=False, samesite="lax"`
7. If `has_https` and `app_env != "production"`: `logger.warning(...)`
8. Always: `httponly=True, path="/", max_age=604800`

### T2: CORS origins from env var (`backend/main.py`)

Replace hardcoded list (lines 44-48):
```python
import os
_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
```

### T3: Auto-detect guard

Integrated into `get_cookie_config()` (see T1 logic step 4-7). Logged at startup via module-level initialization or first call.

### T4: Cookie set/clear use shared config (`backend/routes/auth.py`)

```python
from cookie_config import get_cookie_config

def _set_token_cookie(response: Response, token: str) -> None:
    cfg = get_cookie_config()
    response.set_cookie(
        key=_COOKIE_NAME, value=token,
        httponly=cfg["httponly"], secure=cfg["secure"],
        samesite=cfg["samesite"], path=cfg["path"], max_age=cfg["max_age"],
    )

def _clear_token_cookie(response: Response) -> None:
    cfg = get_cookie_config()
    response.set_cookie(
        key=_COOKIE_NAME, value="",
        httponly=cfg["httponly"], secure=cfg["secure"],
        samesite=cfg["samesite"], path=cfg["path"], max_age=0,
    )
```

### T5: Distinct 401 details

**`backend/auth_utils.py`** — no changes needed. Already re-raises `JWTError`. python-jose raises `ExpiredSignatureError` (subclass of `JWTError`) for expired tokens.

**`backend/routes/auth.py`** — `_get_user_id_from_cookie()`:
```python
from jose import ExpiredSignatureError, JWTError

def _get_user_id_from_cookie(request: Request) -> int:
    token = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="not_authenticated")
    try:
        payload = decode_token(token)
        return payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="session_expired")
    except (JWTError, Exception):
        raise HTTPException(status_code=401, detail="invalid_token")
```

### T6: Frontend `credentials: 'include'` audit

**Status: Already correct.** All 6 fetch calls in 3 components include `credentials: 'include'`:
- `AuthProvider.tsx` (4 calls: me, signup, signin, signout)
- `BackgroundQuestionnaire.tsx` (1 call: save background)
- `PersonalizeButton.tsx` (1 call: personalize)

**Missing**: `UrduTranslateButton.tsx` and `ChatbotWidget.tsx` do NOT use `credentials: 'include'` — but these endpoints don't require authentication, so this is correct.

### T7: Frontend API_URL config audit

**Status: Already correct.** Two patterns in use:
1. `window.__DOCUSAURUS_CUSTOM_FIELDS__?.apiUrl` — used by AuthProvider, BackgroundQuestionnaire, PersonalizeButton, UrduTranslateButton (works in any JS context)
2. `useDocusaurusContext().siteConfig.customFields?.apiUrl` — used by ChatbotWidget (React hook pattern)

Both resolve `docusaurus.config.ts` → `customFields: { apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000' }`.

**Action**: No code changes needed. Production CI must set `REACT_APP_API_URL` at build time.

---

## Testing Plan

### New: `backend/tests/test_cookie_config.py`

| Test | Env Vars | Expected |
|------|----------|----------|
| `test_dev_defaults` | `APP_ENV=development` (no CORS_ORIGINS) | `secure=False, samesite="lax"` |
| `test_dev_explicit_cors` | `APP_ENV=development, CORS_ORIGINS=http://localhost:3000` | `secure=False, samesite="lax"` |
| `test_prod_env` | `APP_ENV=production, CORS_ORIGINS=https://example.com` | `secure=True, samesite="none"` |
| `test_https_autodetect_overrides_dev` | `APP_ENV=development, CORS_ORIGINS=https://example.com` | `secure=True, samesite="none"` + warning logged |
| `test_mixed_origins_https_wins` | `APP_ENV=development, CORS_ORIGINS=http://localhost:3000,https://example.com` | `secure=True, samesite="none"` |
| `test_httponly_always_true` | Any | `httponly=True` |
| `test_path_always_root` | Any | `path="/"` |
| `test_max_age_7_days` | Any | `max_age=604800` |

### Updated: `backend/tests/test_auth_api.py`

| Test | Assertion |
|------|-----------|
| `test_signup_sets_cookie_with_dev_attrs` | Response has `Set-Cookie: token=...; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800` (no Secure) |
| `test_signin_sets_cookie_with_dev_attrs` | Same as above |
| `test_signout_clears_cookie_matching_attrs` | `Set-Cookie: token=; ... Max-Age=0` with matching samesite/secure |
| `test_401_no_cookie_returns_not_authenticated` | `detail == "not_authenticated"` |
| `test_401_expired_returns_session_expired` | `detail == "session_expired"` |
| `test_401_malformed_returns_invalid_token` | `detail == "invalid_token"` |

### Existing Tests (regression)

All 47 existing tests must continue to pass. The test environment uses `APP_ENV=development` (default), so cookie attrs in tests shift from `secure=True` to `secure=False` — this is the correct behavior.

### Edge Case Testing (manual)

| Case | Verification |
|------|-------------|
| Multiple tabs | Sign in tab A, open tab B — `/api/auth/me` returns 200 in both |
| Port mismatch | Frontend on `:3001` — add to CORS_ORIGINS, cookie still works |
| Cookie expiry | Create token with 1s expiry, wait, call `/api/auth/me` — get `session_expired` |
| Sign-out + sign-in cycle | Sign out, sign in, verify new token set and endpoints work |
| Cookies disabled | Browser returns no cookie → `not_authenticated` detail |

---

## Security Validation

| Check | Enforcement |
|-------|-------------|
| `Secure=True` on HTTPS | Auto-detect guard (FR-011) + `APP_ENV=production` logic |
| `HttpOnly=True` always | Hardcoded in `get_cookie_config()` — not configurable |
| `SameSite=None` only with `Secure=True` | Logic ensures `samesite="none"` only in the `secure=True` branch |
| No hardcoded production URLs | CORS_ORIGINS from env var. `docusaurus.config.ts` apiUrl from env var |
| No wildcards in CORS | `allow_credentials=True` + explicit origin list — no `*` |

---

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-auth-cookie-persistence/
├── spec.md              # Feature specification (149 lines, 12 FRs, 7 SCs)
├── plan.md              # This file
├── research.md          # Phase 0: technical research
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: developer setup guide
├── contracts/
│   └── cookie-contract.md  # Phase 1: cookie/CORS/401 contracts
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (files to modify/create)

```text
backend/
├── cookie_config.py         # NEW — get_cookie_config()
├── auth_utils.py            # UNCHANGED — already re-raises JWTError
├── main.py                  # MODIFY — CORS origins from env var
├── routes/
│   └── auth.py              # MODIFY — use get_cookie_config(), distinct 401 details
├── .env                     # MODIFY — add CORS_ORIGINS
└── tests/
    ├── test_cookie_config.py  # NEW — 8+ unit tests
    └── test_auth_api.py       # MODIFY — cookie attr + 401 detail assertions

website/
├── docusaurus.config.ts     # UNCHANGED — already reads REACT_APP_API_URL
└── src/components/
    ├── AuthProvider.tsx         # UNCHANGED — credentials: 'include' ✓
    ├── BackgroundQuestionnaire.tsx  # UNCHANGED — credentials: 'include' ✓
    ├── PersonalizeButton.tsx    # UNCHANGED — credentials: 'include' ✓
    ├── UrduTranslateButton.tsx  # UNCHANGED — no auth needed
    └── ChatbotWidget.tsx        # UNCHANGED — no auth needed
```

**Structure Decision**: Existing web-app layout (backend/ + website/). One new module (`cookie_config.py`) at backend root alongside existing `auth_utils.py`. No new directories needed.

## Complexity Tracking

No constitution violations requiring justification. Smallest viable diff: 1 new module, 3 modified files, 1 new test file, 1 env var addition.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
