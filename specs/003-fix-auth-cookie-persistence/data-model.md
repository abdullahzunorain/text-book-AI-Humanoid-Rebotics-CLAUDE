# Data Model: Fix Cookie-Based Auth Persistence

**Feature**: `003-fix-auth-cookie-persistence` | **Date**: 2026-03-05 | **Updated**: 2026-03-05

## Schema Changes

**None.** This feature modifies HTTP cookie attributes and CORS configuration only. No database tables, columns, or indexes are added, removed, or altered.

---

## New Configuration Entity: `CookieConfig`

A runtime-only configuration object (not persisted). Lives in `backend/cookie_config.py`.

| Field       | Type   | Dev Value          | Prod Value         | Description                                  |
|-------------|--------|--------------------|--------------------|----------------------------------------------|
| `secure`    | `bool` | `False`            | `True`             | Whether cookie requires HTTPS transport      |
| `samesite`  | `str`  | `"lax"`            | `"none"`           | SameSite attribute for cross-site behavior   |
| `httponly`   | `bool` | `True`             | `True`             | Always true — prevents JS access             |
| `path`      | `str`  | `"/"`              | `"/"`              | Cookie path scope                            |
| `max_age`   | `int`  | `604800`           | `604800`           | 7 days in seconds (matches JWT expiry)       |

### Resolution Logic

```
IF any(origin.startswith("https://") for origin in CORS_ORIGINS):
    secure = True, samesite = "none"         # HTTPS auto-detect guard (FR-011)
ELIF APP_ENV == "production":
    secure = True, samesite = "none"
ELSE:
    secure = False, samesite = "lax"
```

### Security Invariants

| Invariant | Enforcement |
|-----------|-------------|
| `SameSite=None` only when `Secure=True` | Ensured by logic — both set in same branch |
| `HttpOnly=True` always | Not configurable — hardcoded in config dict |
| `Secure=True` on HTTPS | Auto-detect guard + production branch |
| No hardcoded production URLs | All origins from `CORS_ORIGINS` env var |

---

## Modified Entity: CORS Configuration

Current state: hardcoded list in `main.py` lines 44-48.
New state: read from `CORS_ORIGINS` environment variable.

| Field           | Type        | Source                    | Default                                          |
|-----------------|-------------|---------------------------|--------------------------------------------------|
| `allow_origins` | `list[str]` | `os.getenv("CORS_ORIGINS")` | `["http://localhost:3000", "http://localhost:3001"]` |

---

## Existing Entities (unchanged)

### `users` table
| Column          | Type      | Notes          |
|-----------------|-----------|----------------|
| `id`            | `SERIAL`  | PK             |
| `username`      | `VARCHAR` | Unique         |
| `email`         | `VARCHAR` | Unique         |
| `password_hash` | `VARCHAR` | bcrypt         |

### `user_backgrounds` table
| Column          | Type      | Notes          |
|-----------------|-----------|----------------|
| `id`            | `SERIAL`  | PK             |
| `user_id`       | `INTEGER` | FK → users.id  |
| `education`     | `VARCHAR` |                |
| `interests`     | `TEXT[]`  |                |
| `experience`    | `VARCHAR` |                |

### JWT Token (cookie value)
| Claim | Type  | Notes                       |
|-------|-------|-----------------------------|
| `sub` | `str` | User ID                     |
| `exp` | `int` | Expiration (7 days from now) |
| `iat` | `int` | Issued-at timestamp          |

---

## State Transitions

### Cookie Lifecycle (unchanged flow, fixed attributes)

```
[No Cookie] --login/register--> [Cookie Set (secure/samesite per env)]
[Cookie Set] --API request--> [Cookie Sent by Browser]
[Cookie Set] --logout--> [Cookie Cleared (max_age=0, matching attrs)]
[Cookie Set] --expired JWT--> [401 "session_expired"]
[Cookie Set] --malformed JWT--> [401 "invalid_token"]
[No Cookie] --API request--> [401 "not_authenticated"]
```

### Multi-Tab State

```
[Tab A: Sign In] --> Browser cookie jar updated
[Tab B: API call] --> Same cookie sent (shared jar) --> 200 OK
[Tab A: Sign Out] --> Cookie cleared in jar
[Tab B: Next API call] --> No cookie --> 401 "not_authenticated"
```

### Environment Transition (deployment)

```
[Dev: HTTP localhost] -- deploy --> [Prod: HTTPS Railway]
  Cookie: Lax/False               Cookie: None/True
  CORS: localhost:3000,3001        CORS: abdullahzunorain.github.io
```

### Edge Case: Mixed CORS Origins (auto-detect)

```
[APP_ENV=development] + [CORS_ORIGINS contains https://...]
  --> Auto-detect forces Secure=True, SameSite=None
  --> Log warning: "HTTPS origin detected with APP_ENV=development"
```
