# API Contract: Authentication Endpoints

**Feature**: 002-mvp2-complete-textbook  
**Phase**: D (Auth)  
**Authentication**: None (public endpoints)

---

## POST /api/auth/signup

**Purpose**: Create new user account

### Request

```
POST /api/auth/signup
Content-Type: application/json
```

```json
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email (RFC 5322), max 255 chars |
| password | string | Yes | Min 8 characters |

### Responses

**201 Created** — Account created, JWT cookie set

```json
{
  "user_id": 42,
  "email": "student@example.com",
  "show_questionnaire": true
}
```
Headers: `Set-Cookie: token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800`

**400 Bad Request** — Email already exists

```json
{
  "detail": "Email already registered"
}
```

**422 Unprocessable Entity** — Validation failed

```json
{
  "detail": "Password must be at least 8 characters"
}
```

### Behavior

1. Validate email format and password length
2. Check email uniqueness in `users` table
3. Hash password with bcrypt (cost 12)
4. INSERT into `users` table
5. Generate JWT token (HS256, 7-day expiry)
6. Set HTTP-only cookie with token
7. Return user_id, email, show_questionnaire=true

---

## POST /api/auth/signin

**Purpose**: Authenticate existing user

### Request

```
POST /api/auth/signin
Content-Type: application/json
```

```json
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

### Responses

**200 OK** — Authenticated, JWT cookie set

```json
{
  "user_id": 42,
  "email": "student@example.com",
  "has_background": true
}
```
Headers: `Set-Cookie: token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800`

**401 Unauthorized** — Invalid credentials

```json
{
  "detail": "Invalid email or password"
}
```

### Behavior

1. Lookup user by email in `users` table
2. Verify password against stored bcrypt hash
3. Check if `user_backgrounds` row exists for user
4. Generate JWT token (HS256, 7-day expiry)
5. Set HTTP-only cookie with token
6. Return user_id, email, has_background flag

---

## POST /api/auth/signout

**Purpose**: Clear JWT cookie

### Request

```
POST /api/auth/signout
```

### Response

**200 OK** — Cookie cleared

```json
{
  "message": "Signed out"
}
```
Headers: `Set-Cookie: token=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`

---

## GET /api/auth/me

**Purpose**: Check current auth status (used by frontend AuthProvider)

**Authentication**: JWT cookie (optional)

### Responses

**200 OK** — Authenticated

```json
{
  "user_id": 42,
  "email": "student@example.com",
  "has_background": true
}
```

**401 Unauthorized** — No valid token

```json
{
  "detail": "Not authenticated"
}
```

---

## Test Cases

```python
# test_auth_api.py
def test_signup_valid():
    """POST /api/auth/signup with valid email/password → 201 + user_id + cookie"""

def test_signup_duplicate_email():
    """POST /api/auth/signup with existing email → 400"""

def test_signup_short_password():
    """POST /api/auth/signup with 3-char password → 422"""

def test_signin_valid():
    """POST /api/auth/signin with correct credentials → 200 + cookie"""

def test_signin_wrong_password():
    """POST /api/auth/signin with wrong password → 401"""

def test_signin_nonexistent_email():
    """POST /api/auth/signin with unknown email → 401"""

def test_signout():
    """POST /api/auth/signout → 200 + clears cookie"""

def test_me_authenticated():
    """GET /api/auth/me with valid cookie → 200 + user info"""

def test_me_unauthenticated():
    """GET /api/auth/me without cookie → 401"""
```
