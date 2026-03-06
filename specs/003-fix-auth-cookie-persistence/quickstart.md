# Quickstart: Fix Cookie-Based Auth Persistence

**Feature**: `003-fix-auth-cookie-persistence` | **Branch**: `003-fix-auth-cookie-persistence` | **Updated**: 2026-03-05

## Prerequisites

- Python 3.13+, Node 18+, npm
- Backend `.env` file with `JWT_SECRET`, `DATABASE_URL`
- Frontend Docusaurus project in `website/`

---

## 1. Environment Setup

### Backend `.env` (add/update these vars)

```env
# Existing
APP_ENV=development
JWT_SECRET=<your-secret>

# New — required for this feature
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Production Environment (Railway)

```env
APP_ENV=production
CORS_ORIGINS=https://abdullahzunorain.github.io
JWT_SECRET=<production-secret>
```

### Frontend Build (GitHub Pages CI)

```env
REACT_APP_API_URL=https://<your-railway-app>.up.railway.app
```

---

## 2. New File: `backend/cookie_config.py`

This module centralizes cookie attribute resolution. Implementation will be driven by tests.

**Key export**: `get_cookie_config() -> dict` returns `{secure, samesite, httponly, path, max_age}`.

---

## 3. Run Tests (TDD workflow)

```bash
# From repo root
cd backend

# Run all tests (should be 47 passing before changes)
python -m pytest tests/ -v

# Run only cookie config tests (will be added)
python -m pytest tests/test_cookie_config.py -v

# Run only auth API tests
python -m pytest tests/test_auth_api.py -v
```

---

## 4. Verify Cookie Behavior Locally

### Start backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start frontend

```bash
cd website
npm start
```

### Browser verification steps

1. Open `http://localhost:3000`
2. Register or log in
3. Open DevTools → Application → Cookies → `localhost:8000`
4. Verify cookie `token` exists with:
   - `HttpOnly`: ✓
   - `Secure`: ✗ (unchecked — HTTP localhost)
   - `SameSite`: `Lax`
   - `Path`: `/`
5. Refresh the page → user should remain logged in
6. Click Logout → cookie should be removed

---

## 5. Verify Production Behavior

After deploying to Railway:

1. Visit `https://abdullahzunorain.github.io`
2. Log in
3. Open DevTools → Application → Cookies → `<railway-app>.up.railway.app`
4. Verify cookie `token` exists with:
   - `HttpOnly`: ✓
   - `Secure`: ✓
   - `SameSite`: `None`
5. Refresh → user remains logged in (cross-site cookie sent)

---

## 6. Files Modified (summary)

| File | Change |
|------|--------|
| `backend/cookie_config.py` | **New** — environment-aware cookie attribute resolver |
| `backend/routes/auth.py` | Use `get_cookie_config()` in set/clear/validate functions |
| `backend/auth_utils.py` | Distinct `ExpiredSignatureError` handling in `decode_token()` |
| `backend/main.py` | Read `CORS_ORIGINS` from env var |
| `backend/.env` | Add `CORS_ORIGINS` |
| `backend/tests/test_cookie_config.py` | **New** — unit tests for cookie config |
| `backend/tests/test_auth_api.py` | Updated — test cookie attributes + 401 detail codes |
| `website/docusaurus.config.ts` | No change needed (already configured) |

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cookie not set on localhost | `Secure=True` on HTTP | Check `APP_ENV=development` in `.env` |
| Cookie not sent cross-site in prod | `SameSite=Lax` | Check `APP_ENV=production` and `CORS_ORIGINS` contains HTTPS origin |
| CORS error in browser | Origin not in allowed list | Add origin to `CORS_ORIGINS` env var |
| 401 on refresh after login | Cookie attributes mismatch between set/clear | Ensure both functions use `get_cookie_config()` |

---

## 8. Environment Variables Reference

### `APP_ENV`

| Value | Effect | Default |
|-------|--------|---------|
| `development` | `Secure=False`, `SameSite=Lax`. Cookies work on HTTP localhost. | Yes (if unset) |
| `production` | `Secure=True`, `SameSite=None`. Cookies work cross-site over HTTPS. | No |

**Usage**: Set in `.env` for local dev. Set as Railway env var for production.

### `CORS_ORIGINS`

Comma-separated list of allowed origins for CORS.

| Environment | Value | Notes |
|-------------|-------|-------|
| Development | `http://localhost:3000,http://localhost:3001` | Default if unset. Port 3001 for fallback. |
| Production | `https://abdullahzunorain.github.io` | Must match your GitHub Pages domain exactly. |

**Important**: `allow_credentials=True` requires explicit origins — wildcards (`*`) are not allowed.

### `REACT_APP_API_URL` (frontend build-time)

| Environment | Value | Notes |
|-------------|-------|-------|
| Development | Not set | Falls back to `http://localhost:8000` via `docusaurus.config.ts` |
| Production | `https://<app>.up.railway.app` | Set in GitHub Actions / Netlify build env |

**Usage**: Read by Docusaurus at build time via `process.env.REACT_APP_API_URL`. Exposed to components via `customFields.apiUrl`.

### `JWT_SECRET`

Secret key for HS256 JWT signing/verification. **Never commit to git.** Use `.env` locally, Railway env vars in production.

---

## 9. Running Dev and Production Locally

### Development (default)

```bash
# Terminal 1: Backend
cd backend
cp .env.example .env  # or verify .env has APP_ENV=development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd website
npm start
# Opens http://localhost:3000
```

Cookie behavior: `HttpOnly; SameSite=Lax; Path=/; Max-Age=604800` (no Secure flag).

### Simulating Production Locally

To test production cookie behavior locally, you need HTTPS. Quick approach with mkcert:

```bash
# Install mkcert (one-time)
brew install mkcert  # or apt install mkcert
mkcert -install
mkcert localhost

# Start backend with HTTPS
uvicorn main:app --ssl-keyfile localhost-key.pem --ssl-certfile localhost.pem --port 8000

# Set env vars
APP_ENV=production
CORS_ORIGINS=https://localhost:3000
```

Cookie behavior: `HttpOnly; Secure; SameSite=None; Path=/; Max-Age=604800`.

### Production Deployment (Railway + GitHub Pages)

```bash
# Railway env vars (set via dashboard or CLI)
APP_ENV=production
JWT_SECRET=<strong-random-secret>
CORS_ORIGINS=https://abdullahzunorain.github.io
DATABASE_URL=<neon-postgres-url>

# GitHub Pages build env (set in GitHub Actions)
REACT_APP_API_URL=https://<app>.up.railway.app
```
