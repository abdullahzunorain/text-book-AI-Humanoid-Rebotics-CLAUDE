# Feature Specification: Fix Cookie-Based Auth Persistence

**Feature Branch**: `003-fix-auth-cookie-persistence`
**Created**: 2025-07-16
**Status**: Draft
**Input**: User description: "Fix cookie-based auth persistence: secure flag blocks cookies on localhost HTTP, causing 401 errors after signup/signout on dev environment"

## Problem Statement

After a user signs up successfully (receiving a 201 response with `show_questionnaire: true`), subsequent authenticated requests — such as saving background preferences (`POST /api/user/background`) or checking session status (`GET /api/auth/me`) — fail with HTTP 401 "Not authenticated". The root cause is that the JWT cookie is set with `secure=true`, which instructs the browser to **only transmit the cookie over HTTPS connections**. During local development the frontend runs on `http://localhost:3000` (plain HTTP), so the browser silently drops the cookie on every subsequent request. The same issue affects any non-HTTPS deployment.

### Root Cause Analysis

1. **`secure=True` on HTTP**: The `_set_token_cookie()` helper in `routes/auth.py` unconditionally sets `secure=True`. Browsers comply with RFC 6265 §5.4: a cookie with the Secure attribute is never attached to requests made over an insecure connection. On `http://localhost:*`, the cookie is received in the `Set-Cookie` header but never sent back.
2. **`samesite="lax"` in production (cross-site)**: With Lax, the cookie is sent on same-site navigations only. In production, the frontend (GitHub Pages: `abdullahzunorain.github.io`) and backend (Railway: different domain) are **cross-site**, meaning `SameSite=Lax` would block the cookie entirely on fetch/XHR. Production requires `SameSite=None` + `Secure=True`. In development, `localhost:3000` → `localhost:8000` is same-site, so `Lax` works. The current code uses `Lax` unconditionally, which is correct for dev but breaks production cross-site requests.
3. **CORS origin matching**: The backend allows `http://localhost:3000` and `http://localhost:3001`, with `allow_credentials=True`. This is correct for development — the issue is purely that the cookie never leaves the browser due to the Secure flag.
4. **Frontend `credentials: 'include'`**: All fetch calls correctly include `credentials: 'include'`, which is necessary for cross-origin cookie transmission. This is not the issue.

### Impact

- **All authenticated features are broken in local development**: background questionnaire, personalized content, translated content, `/api/auth/me` session checks.
- **Production (HTTPS) works correctly**: The `secure=True` flag is correct for production.
- **Developer experience is severely impacted**: Cannot test any authenticated workflow locally without workarounds.

## Clarifications

### Session 2025-07-16

- Q: What happens if APP_ENV=development accidentally leaks into a production (HTTPS) deployment — should there be a safety guard? → A: Auto-detect: if the request origin uses HTTPS or a known production domain is in CORS origins, force Secure=True regardless of APP_ENV. Log a warning if APP_ENV contradicts.
- Q: How should the frontend differentiate missing cookie vs expired JWT vs malformed token on 401? → A: Return different error detail strings in the 401 response: `not_authenticated` (no cookie), `session_expired` (expired JWT), `invalid_token` (malformed/tampered). All remain HTTP 401.
- Q: Should CORS origins be hardcoded (all envs combined) or environment-driven? → A: Environment-driven: read `CORS_ORIGINS` from env var (comma-separated). Dev `.env` lists localhost only; production lists the GitHub Pages domain only. FR-011 auto-detect inspects the actual runtime list.
- Q: Should SameSite stay Lax in both environments? → A: No. Production is true cross-site (GitHub Pages → Railway = different domains), so `SameSite=None` + `Secure=True` is required in production. Dev uses `SameSite=Lax` + `Secure=False` (localhost is same-site). Split config per environment.
- Q: Should the spec include frontend API_URL configuration, or is that out of scope? → A: In scope. The cookie fix is meaningless if the frontend talks to `http://localhost:8000` in production. `API_URL` MUST be configurable via Docusaurus `customFields` or build-time env var.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Signup and Save Background (Priority: P1)

A new user visits the textbook on their local development environment, signs up with email and password, is presented with the background questionnaire, fills it out, and saves their learning profile. Their session persists so they can access personalized features.

**Why this priority**: This is the core broken flow. Without this, no authenticated feature works during development, completely blocking testing and iteration of the entire auth system.

**Independent Test**: Sign up from `http://localhost:3000`, verify the questionnaire appears, fill in background fields, click save, and confirm a 200 response from `/api/user/background` (not 401).

**Acceptance Scenarios**:

1. **Given** the backend runs on `http://localhost:8000` and the frontend on `http://localhost:3000`, **When** a user signs up with valid credentials, **Then** the JWT cookie is set and subsequent requests to `/api/auth/me` return 200 with the user's information.
2. **Given** a user just signed up on localhost, **When** they submit the background questionnaire, **Then** `/api/user/background` receives the cookie, authenticates the user, and returns 200.
3. **Given** a user just signed up on localhost, **When** they refresh the page, **Then** `/api/auth/me` still returns 200 (cookie persists across page reloads).

---

### User Story 2 - Sign In After Previous Sign Out (Priority: P1)

A returning user who previously signed out opens the textbook, signs in with their credentials, and immediately has a valid session. Their authentication cookie is correctly set and sent on all subsequent requests.

**Why this priority**: Sign-in is equally critical as signup — both must produce a persistent cookie. Previously, signing out cleared the cookie, and signing back in would set a cookie that again could not be sent back over HTTP.

**Independent Test**: Sign in from `http://localhost:3000`, then call `GET /api/auth/me` and confirm it returns 200 with user data.

**Acceptance Scenarios**:

1. **Given** a registered user on localhost, **When** they sign in, **Then** the JWT cookie is set and `GET /api/auth/me` returns their user info.
2. **Given** a user is signed in on localhost, **When** they sign out and then sign back in, **Then** a new valid cookie is set and authenticated endpoints work without error.

---

### User Story 3 - Production HTTPS Cookie Security (Priority: P1)

When the application is deployed to a production environment served over HTTPS (e.g., on a hosting platform), the authentication cookie must retain the `Secure` flag to prevent cookie theft via man-in-the-middle attacks.

**Why this priority**: Security cannot regress. The fix for localhost must not remove the Secure flag in production, which would be a security vulnerability.

**Independent Test**: Deploy to an HTTPS environment, sign up, and verify via browser DevTools that the `Set-Cookie` header includes `Secure` and `HttpOnly` attributes.

**Acceptance Scenarios**:

1. **Given** the app is deployed to an HTTPS production domain, **When** a user signs up, **Then** the `Set-Cookie` header contains `Secure; HttpOnly; SameSite=None; Path=/`.
2. **Given** a production HTTPS environment, **When** authenticated requests are made, **Then** the cookie is transmitted on every request and the user stays authenticated.

---

### User Story 4 - Personalize Chapter After Auth (Priority: P2)

An authenticated user browses to a chapter page and clicks "Personalize This Chapter". The system recognizes the user's session, reads their background profile, and returns personalized content.

**Why this priority**: This is a downstream consumer of the auth fix. Once cookies persist correctly, personalization should work without additional changes. This story validates the end-to-end flow.

**Independent Test**: Sign in, navigate to a chapter, click "Personalize This Chapter", and confirm the personalized content renders (not a 401 error message).

**Acceptance Scenarios**:

1. **Given** an authenticated user with a saved background on localhost, **When** they click "Personalize This Chapter", **Then** the `/api/personalize` endpoint receives the cookie and returns personalized content.
2. **Given** an authenticated user on localhost, **When** the personalize request is made, **Then** the response does not contain a 401 error.

---

### Edge Cases

- **Mixed protocol transitions**: User bookmarks an HTTP URL but the server later enforces HTTPS redirect — the cookie should still work once on HTTPS.
- **Multiple tabs**: User signs in on one tab, opens the textbook in another tab — both tabs should share the same cookie and session.
- **Cookie expiry**: After 7 days (max_age), the cookie expires. The backend returns `401 "session_expired"` and the frontend shows "Your session has expired, please sign in again" rather than a generic 401.
- **Sign-out clears cookie completely**: After sign-out, no stale cookie remnants should remain that could cause confusion on the next sign-in.
- **Port mismatch**: If the frontend runs on an unexpected port (e.g., `3001` due to port conflict), the CORS origin list must include it and cookies must still work.
- **Browser cookie storage limits**: If the user has cookies disabled or has hit browser storage limits, the system should gracefully show a "please enable cookies" message rather than a cryptic 401.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST set the cookie `Secure` flag based on the deployment environment — enabled for HTTPS, disabled for HTTP (localhost development).
- **FR-002**: System MUST use a single environment-aware configuration that controls all cookie attributes (`Secure`, `SameSite`, `Domain`, `Path`) consistently across set, clear, and refresh operations.
- **FR-003**: System MUST preserve `HttpOnly=true` on all authentication cookies in every environment to prevent XSS-based cookie theft.
- **FR-004**: System MUST set `SameSite=None` on authentication cookies in production (cross-site: GitHub Pages → Railway) paired with `Secure=True`. In development (same-site: localhost → localhost), system MUST set `SameSite=Lax` with `Secure=False`.
- **FR-005**: System MUST use environment-aware SameSite configuration: `Lax` for development (same-site localhost), `None` for production (cross-site GitHub Pages → Railway). `SameSite=None` MUST always be paired with `Secure=True` as required by browser specifications.
- **FR-006**: System MUST return HTTP 401 with distinct `detail` strings for each authentication failure mode: `"not_authenticated"` (no cookie present), `"session_expired"` (JWT expired), `"invalid_token"` (malformed or tampered JWT). The frontend MUST use these to show contextual UI messages.
- **FR-007**: System MUST accept a configuration value (environment variable) that determines whether the application is running in development or production mode. No code changes should be required to switch environments.
- **FR-008**: System MUST ensure that the `Set-Cookie` response header is sent with correct attributes after signup, signin, and cookie refresh operations.
- **FR-009**: System MUST ensure sign-out fully clears the cookie by setting the same attributes (path, domain, secure, samesite) used when setting it, plus `max_age=0`.
- **FR-010**: System MUST read allowed CORS origins from a `CORS_ORIGINS` environment variable (comma-separated). The origin list MUST match the deployment context: localhost origins for development, production domain(s) for production. `allow_credentials=True` requires explicit origins (no wildcards).
- **FR-011**: System MUST auto-detect HTTPS context by inspecting the runtime `CORS_ORIGINS` list for any non-localhost (production) domains. If production domains are present, force `Secure=True` on cookies regardless of `APP_ENV`. If `APP_ENV=development` contradicts the detection, log a warning but still enforce `Secure=True`.
- **FR-012**: Frontend MUST read the backend API URL from Docusaurus `customFields.apiUrl` (configured via environment variable at build time). The hardcoded `http://localhost:8000` fallback MUST only apply when no `customFields.apiUrl` is set. Production builds MUST inject the production backend URL.

### Key Entities

- **JWT Cookie (`token`)**: The authentication credential. Attributes: `HttpOnly`, `Secure` (conditional), `SameSite` (conditional: `Lax` in dev, `None` in prod), `Path=/`, `max_age=604800`. Stored by the browser and sent on every request when attributes permit.
- **Environment Configuration**: A runtime setting (e.g., `APP_ENV`) that governs whether the app operates in development mode (relaxed cookie security for HTTP) or production mode (strict cookie security for HTTPS).
- **CORS Policy**: Origins read from `CORS_ORIGINS` env var (comma-separated). Dev default: `http://localhost:3000,http://localhost:3001`. Production: `https://abdullahzunorain.github.io`. Must align with cookie credential requirements — `allow_credentials=True` requires explicit origins (no wildcards).

## Assumptions

- The primary development environment is `http://localhost` (ports 3000 for frontend, 8000 for backend).
- Production is served over HTTPS with a proper domain (e.g., `abdullahzunorain.github.io` for frontend, deployed backend with HTTPS).
- The environment mode defaults to `development` if not explicitly set, ensuring safe behavior for local testing without additional configuration.
- Even if `APP_ENV` is misconfigured, the auto-detect guard (FR-011) prevents Secure-flag omission on HTTPS deployments.
- No reverse proxy or TLS terminator sits between the dev frontend and backend.
- Modern browsers (Chrome, Firefox, Safari, Edge) are the target — all support SameSite cookie attributes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the full signup → questionnaire → personalize flow on `http://localhost` without encountering 401 errors — 100% of requests to authenticated endpoints succeed when a valid session exists.
- **SC-002**: Users can sign out and sign back in on localhost and maintain a valid session — cookie is re-set and all authenticated endpoints respond correctly.
- **SC-003**: On a production HTTPS deployment, the cookie retains `Secure; HttpOnly; SameSite=None` attributes — verified by inspecting `Set-Cookie` headers.
- **SC-004**: Switching between development and production mode requires only changing a single environment variable — no code modifications.
- **SC-005**: All existing backend tests continue to pass (47 tests, 0 failures, 0 warnings) after the change.
- **SC-006**: The fix introduces no new security vulnerabilities — the Secure flag is always enabled when the app runs over HTTPS.
- **SC-007**: Frontend production builds point to the correct backend URL (not `localhost:8000`) — verified by inspecting network requests in browser DevTools after deployment.
