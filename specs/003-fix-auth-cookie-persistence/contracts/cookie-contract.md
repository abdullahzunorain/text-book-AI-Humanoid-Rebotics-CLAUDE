# Contract: Cookie Attributes

**Feature**: `003-fix-auth-cookie-persistence` | **Version**: 1.1 | **Updated**: 2026-03-05

## Cookie "token" — Set-Cookie Contract

The backend sets a single cookie named `token` on login (`POST /register`, `POST /login`) and clears it on logout (`POST /logout`).

### Set-Cookie Headers by Environment

#### Development (`APP_ENV=development`, HTTP origins)

```http
Set-Cookie: token=<jwt>; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800
```

| Attribute  | Value    |
|------------|----------|
| Name       | `token`  |
| Value      | JWT (HS256, `sub`=user_id, 7d expiry) |
| Path       | `/`      |
| HttpOnly   | `true`   |
| Secure     | _(omitted — false)_ |
| SameSite   | `Lax`    |
| Max-Age    | `604800` (7 days) |

#### Production (`APP_ENV=production`, HTTPS origins)

```http
Set-Cookie: token=<jwt>; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=604800
```

| Attribute  | Value    |
|------------|----------|
| Name       | `token`  |
| Value      | JWT (HS256, `sub`=user_id, 7d expiry) |
| Path       | `/`      |
| HttpOnly   | `true`   |
| Secure     | `true`   |
| SameSite   | `None`   |
| Max-Age    | `604800` (7 days) |

### Clear-Cookie Header (both environments)

```http
Set-Cookie: token=; Path=/; HttpOnly; [Secure]; [SameSite]; Max-Age=0
```

`Secure` and `SameSite` attributes MUST match the set call for the same environment.

---

## Error Response Contract (401 Unauthorized)

All protected endpoints return 401 with a JSON body containing a `detail` string.

| Condition           | `detail` value       | Description                              |
|---------------------|----------------------|------------------------------------------|
| No cookie present   | `"not_authenticated"` | Cookie header missing or `token` absent |
| JWT expired         | `"session_expired"`   | `exp` claim < current time              |
| JWT invalid/malformed | `"invalid_token"`   | Signature mismatch, decode error, etc.  |

### Response Format

```json
{
  "detail": "not_authenticated" | "session_expired" | "invalid_token"
}
```

HTTP status: `401`
Content-Type: `application/json`

---

## CORS Contract

### Request Headers (browser sends)

```http
Origin: <allowed-origin>
```

### Response Headers (backend sends)

```http
Access-Control-Allow-Origin: <requesting-origin>
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

### Allowed Origins

| Environment | `CORS_ORIGINS` value | Source |
|-------------|---------------------|--------|
| Development | `http://localhost:3000,http://localhost:3001` | `.env` file |
| Production  | `https://abdullahzunorain.github.io` | Railway env var |

If `CORS_ORIGINS` is unset, defaults to `http://localhost:3000,http://localhost:3001`.

---

## Auto-Detect Guard Contract (FR-011)

At application startup, if any origin in `CORS_ORIGINS` starts with `https://`:
- Force `secure=True`, `samesite="none"` regardless of `APP_ENV`
- Log warning: `"HTTPS origin detected with APP_ENV=development — forcing Secure cookies"`
  (only if `APP_ENV != "production"`)

This prevents silent cookie loss when HTTPS origins are configured but APP_ENV hasn't been updated.

---

## Security Validation Contract

All of the following MUST hold true at all times. Violation of any invariant is a critical bug.

| # | Invariant | Enforcement |
|---|-----------|-------------|
| S1 | `Secure=True` whenever backend serves HTTPS traffic | Auto-detect guard checks CORS_ORIGINS for `https://`; production branch forces `True` |
| S2 | `HttpOnly=True` on ALL cookies, ALL environments | Hardcoded in `get_cookie_config()` — not configurable via env var |
| S3 | `SameSite=None` ONLY when `Secure=True` | Both set in same conditional branch — impossible to have `None` without `Secure` |
| S4 | No wildcard (`*`) in CORS origins | `allow_credentials=True` requires explicit origins; list parsed from env var |
| S5 | No hardcoded production URLs in code | Origins from `CORS_ORIGINS` env var; frontend URL from `REACT_APP_API_URL` |
| S6 | Cookie clearing uses same attributes as setting | Both `_set_token_cookie()` and `_clear_token_cookie()` call `get_cookie_config()` |

---

## Edge Case Contract

| Case | Expected Behavior |
|------|-------------------|
| Multiple tabs (same user) | All tabs share the same cookie. Sign-out from any tab clears cookie for all. Other tabs get `401 "not_authenticated"` on next request. |
| Port mismatch (`:3001`) | Works if `http://localhost:3001` is in `CORS_ORIGINS`. Default includes both `:3000` and `:3001`. |
| Mixed protocol (HTTP→HTTPS) | Auto-detect guard forces `Secure=True` if any HTTPS origin present. Dev-to-prod is an env var swap, not runtime transition. |
| Cookie expiry after 7d | Browser stops sending cookie. Backend receives no cookie → `401 "not_authenticated"`. JWT `exp` check also returns `session_expired` if cookie is present but token has expired. |
| Cookies disabled in browser | Browser ignores `Set-Cookie`. Backend receives no cookie → `401 "not_authenticated"`. Frontend shows login UI. |
| APP_ENV=development + HTTPS origins | Auto-detect overrides to `Secure=True, SameSite=None`. Warning logged. |
| Empty CORS_ORIGINS | Falls back to default: `http://localhost:3000,http://localhost:3001` |
