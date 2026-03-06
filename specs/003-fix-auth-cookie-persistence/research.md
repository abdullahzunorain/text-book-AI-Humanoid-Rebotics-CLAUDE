# Research: Fix Cookie-Based Auth Persistence

**Feature**: `003-fix-auth-cookie-persistence` | **Date**: 2026-03-05 | **Updated**: 2026-03-05

## Research Tasks

### R1: FastAPI `response.set_cookie()` SameSite=None + Secure behavior

**Decision**: Use `samesite="none"` (lowercase string) with `secure=True` in production.

**Rationale**: FastAPI/Starlette's `Response.set_cookie()` accepts `samesite` as a string (`"lax"`, `"strict"`, `"none"`, or `False` to omit). When `samesite="none"`, browsers require `Secure=True` or they reject the cookie entirely (Chrome 80+). This is the standard pattern for cross-site cookie transmission.

**Alternatives considered**:
- Omitting SameSite entirely (`samesite=False`): Browsers default to `Lax`, which would fail cross-site. Rejected.
- Using `SameSite=Strict`: Blocks all cross-site requests including top-level navigations. Too restrictive. Rejected.

**Verification**: Starlette source confirms string values are passed directly to `Set-Cookie` header. No special handling needed.

---

### R2: Browser behavior for `Secure` cookies on localhost

**Decision**: Set `Secure=False` for development (localhost HTTP).

**Rationale**: RFC 6265bis §5.4 specifies that Secure-flagged cookies are only sent over HTTPS. While Chrome has a special exception allowing `Secure` cookies on `localhost` (since Chrome 89), Firefox and Safari do NOT. Since we target all modern browsers, `Secure=False` is the safe choice for HTTP localhost development.

**Alternatives considered**:
- Keep `Secure=True` on localhost and rely on Chrome's exception: Breaks Firefox/Safari. Rejected.
- Use HTTPS on localhost (mkcert): Adds dev setup complexity. Rejected for a bug fix.

---

### R3: CORS origins from environment variable — parsing pattern

**Decision**: Read `CORS_ORIGINS` as a comma-separated string from `.env`, split on `,`, strip whitespace.

**Rationale**: This is the standard pattern for FastAPI CORS configuration. Example: `CORS_ORIGINS=http://localhost:3000,http://localhost:3001` in dev, `CORS_ORIGINS=https://abdullahzunorain.github.io` in prod. `python-dotenv` loads the value, `os.getenv().split(",")` parses it.

**Alternatives considered**:
- JSON array in env var: Non-standard for `.env` files, quoting issues. Rejected.
- Separate `CORS_ORIGIN_1`, `CORS_ORIGIN_2` vars: Inflexible. Rejected.
- hardcoded list per APP_ENV: Works but less flexible. Rejected per spec (FR-010).

**Default**: If `CORS_ORIGINS` is not set, fall back to `http://localhost:3000,http://localhost:3001` (safe dev default).

---

### R4: HTTPS auto-detect guard (FR-011) implementation

**Decision**: Check at startup whether any origin in `CORS_ORIGINS` starts with `https://`. If so, force `Secure=True` and `SameSite=None` regardless of `APP_ENV`. Log a warning if `APP_ENV=development`.

**Rationale**: This prevents accidental cookie insecurity if someone deploys with `APP_ENV=development` but HTTPS origins. The check is a single `any(o.startswith("https://") for o in origins)` at startup — negligible cost, significant safety benefit.

**Alternatives considered**:
- Runtime per-request scheme detection via `request.url.scheme`: Unreliable behind reverse proxies (may report HTTP even when TLS-terminated). Rejected.
- Trust `APP_ENV` fully: No safety net for misconfiguration. Rejected per spec.

---

### R5: python-jose `JWTError` subclass for expired tokens

**Decision**: Catch `jose.ExpiredSignatureError` specifically (subclass of `JWTError`) to distinguish expired from malformed tokens.

**Rationale**: python-jose raises `ExpiredSignatureError` when `exp` claim is in the past, and `JWTClaimsError` or `JWTError` for other failures (malformed, wrong algorithm, bad signature). This allows the `_get_user_id_from_cookie()` function to return distinct error details: `session_expired` vs `invalid_token`.

**Verification**: `from jose import ExpiredSignatureError` — confirmed available in python-jose 3.3.0+.

**Alternatives considered**:
- Decode without verification first, check `exp` manually: More code, same result. Rejected.
- Return generic 401 for all cases: Doesn't meet FR-006. Rejected.

---

### R6: Docusaurus `customFields` access pattern in components

**Decision**: Keep the existing `window.__DOCUSAURUS_CUSTOM_FIELDS__?.apiUrl` pattern for components that can't use hooks (non-React-component modules). Use `useDocusaurusContext()` where hooks are available.

**Rationale**: The current frontend already has both patterns:
- `ChatbotWidget.tsx` uses `useDocusaurusContext()` (correct for functional components with hooks)
- `AuthProvider.tsx`, `BackgroundQuestionnaire.tsx`, `PersonalizeButton.tsx`, `UrduTranslateButton.tsx` use `window.__DOCUSAURUS_CUSTOM_FIELDS__?.apiUrl` (works in any JS context)

Both approaches correctly resolve the same `customFields.apiUrl` value. The `window.__DOCUSAURUS_CUSTOM_FIELDS__` global is set by Docusaurus at runtime and available before React hydration.

**Alternatives considered**:
- Refactor all to `useDocusaurusContext()`: Would require wrapping non-hook contexts. Over-engineering for a bug fix. Rejected.
- Environment variable at build time injected via webpack DefinePlugin: Docusaurus doesn't support custom webpack DefinePlugin easily. The `customFields` approach is the Docusaurus-idiomatic way. Rejected.

**Key finding**: `docusaurus.config.ts` already reads `process.env.REACT_APP_API_URL || 'http://localhost:8000'`. This means production builds just need `REACT_APP_API_URL` set at build time. No code changes needed in the config itself — only ensure the env var is set in the CI/CD pipeline.

---

### R7: Cookie clearing — attribute matching requirement

**Decision**: `_clear_token_cookie()` must use identical attributes (`path`, `samesite`, `secure`) as `_set_token_cookie()`, with `max_age=0` and empty value.

**Rationale**: Browsers identify cookies by `(name, domain, path)`. To clear a cookie, the response must set the same `name` + `path` + `domain` combination with `max_age=0`. If the `Secure` or `SameSite` attributes don't match, the browser may treat it as a different cookie and fail to clear. Both functions must share the same config source.

**Verification**: Confirmed in MDN Web Docs and RFC 6265 §5.3. The current code already uses matching attributes (both hardcode `secure=True, samesite="lax"`), but after making them dynamic, both must read from the same config object.

---

### R8: Frontend `credentials: 'include'` audit

**Decision**: No changes needed. All authenticated fetch calls already include `credentials: 'include'`.

**Findings**:
- `AuthProvider.tsx`: 4 fetch calls (me, signup, signin, signout) — all include `credentials: 'include'` ✓
- `BackgroundQuestionnaire.tsx`: 1 fetch call (save background) — includes `credentials: 'include'` ✓
- `PersonalizeButton.tsx`: 1 fetch call (personalize) — includes `credentials: 'include'` ✓
- `UrduTranslateButton.tsx`: 1 fetch call (translate) — does NOT include credentials. Correct: this endpoint is unauthenticated.
- `ChatbotWidget.tsx`: 1 fetch call (chat) — does NOT include credentials. Correct: this endpoint is unauthenticated.

**Rationale**: `credentials: 'include'` is required for cross-origin cookie transmission. It tells the browser to attach cookies even when the request is to a different origin. Without it, the `Set-Cookie` response is received but the cookie is never sent back. All authenticated endpoints already have this.

---

### R9: Multiple tabs / shared cookie state

**Decision**: No special handling needed. Browser cookies are shared across all tabs for the same origin.

**Rationale**: When a user signs in on Tab A, the `Set-Cookie` header stores the cookie in the browser's cookie jar. Tab B making a request to the same backend origin will automatically include the same cookie. Sign-out from any tab clears the cookie for all tabs (next request from other tabs will get 401). This is standard browser behavior per RFC 6265.

**Edge case**: If Tab A signs out while Tab B is mid-session, Tab B's next API call returns `not_authenticated`. The frontend `AuthProvider` already handles 401 by redirecting to login.

---

### R10: Mixed protocol (HTTP → HTTPS) transition

**Decision**: The auto-detect guard (FR-011) handles this. If CORS_ORIGINS switches from HTTP to HTTPS origins, the cookie config automatically upgrades to `Secure=True`.

**Rationale**: In practice, this transition happens at deployment time (dev→prod), not at runtime. The env vars change when deploying to Railway. If someone accidentally uses HTTPS origins in dev, the auto-detect guard forces Secure cookies and logs a warning, preventing silent cookie loss.

---

### R11: Browser cookies disabled scenario

**Decision**: No backend change needed. When cookies are disabled, the browser simply ignores `Set-Cookie` headers. The backend receives no cookie → returns `401 "not_authenticated"`.

**Rationale**: The frontend should handle this gracefully. The `AuthProvider` already catches 401 responses and shows the login UI. A dedicated "please enable cookies" message is a nice-to-have but out of scope for this bug fix (would require JS cookie detection with `navigator.cookieEnabled`).

---

### R12: Port mismatch handling

**Decision**: Include `http://localhost:3001` in the default `CORS_ORIGINS` alongside `http://localhost:3000`.

**Rationale**: When port 3000 is busy, Docusaurus falls back to 3001. Both ports are same-site with `localhost:8000`, so `SameSite=Lax` cookies still work. The only potential issue is CORS — the browser blocks the response if the origin isn't allowed. Including both ports in the default covers this common dev scenario.

Default: `CORS_ORIGINS=http://localhost:3000,http://localhost:3001`
