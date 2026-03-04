# API Contract: User Background

**Feature**: 002-mvp2-complete-textbook  
**Phase**: E (Personalization)  
**Authentication**: Required (JWT cookie)

---

## POST /api/user/background

**Purpose**: Save user's educational background for personalized AI responses

### Request

```
POST /api/user/background
Content-Type: application/json
Cookie: token=<jwt>
```

```json
{
  "python_level": "intermediate",
  "robotics_experience": "student",
  "math_level": "undergraduate",
  "hardware_access": false,
  "learning_goal": "Prepare for robotics internship at tech company"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| python_level | string (enum) | Yes | One of: `beginner`, `intermediate`, `advanced` |
| robotics_experience | string (enum) | Yes | One of: `none`, `hobbyist`, `student`, `professional` |
| math_level | string (enum) | Yes | One of: `high_school`, `undergraduate`, `graduate` |
| hardware_access | boolean | Yes | `true` or `false` |
| learning_goal | string | No | Free-form text, max 200 chars |

### Responses

**200 OK** — Background saved (upsert)

```json
{
  "user_id": 42,
  "python_level": "intermediate",
  "robotics_experience": "student",
  "math_level": "undergraduate",
  "hardware_access": false,
  "learning_goal": "Prepare for robotics internship at tech company",
  "updated_at": "2026-03-04T10:30:00Z"
}
```

**401 Unauthorized** — No valid JWT

```json
{
  "detail": "Not authenticated"
}
```

**422 Unprocessable Entity** — Invalid enum value

```json
{
  "detail": "Invalid value for python_level: 'expert'. Must be one of: beginner, intermediate, advanced"
}
```

### Behavior

1. Extract user_id from JWT cookie
2. Validate enum fields against allowed values, learning_goal length ≤200 chars
3. UPSERT into `user_backgrounds` table:
   - If no row exists for user_id → INSERT
   - If row exists → UPDATE fields + set `updated_at = NOW()`
4. Return complete background record

### Performance

- **p95 latency**: <100ms (single DB upsert)

---

## GET /api/user/background

**Purpose**: Retrieve current user's background (used by frontend to skip questionnaire)

### Request

```
GET /api/user/background
Cookie: token=<jwt>
```

### Responses

**200 OK** — Background exists

```json
{
  "user_id": 42,
  "python_level": "intermediate",
  "robotics_experience": "student",
  "math_level": "undergraduate",
  "hardware_access": false,
  "learning_goal": "Prepare for robotics internship at tech company",
  "updated_at": "2026-03-04T10:30:00Z"
}
```

**401 Unauthorized** — No valid JWT

```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found** — No background saved yet

```json
{
  "detail": "Background not found"
}
```

---

## Test Cases

```python
# test_background_api.py
def test_save_background_valid():
    """POST /api/user/background with valid 5 fields → 200 + saved record"""

def test_save_background_upsert():
    """POST /api/user/background twice → 200 on both, second updates existing"""

def test_save_background_invalid_enum():
    """POST /api/user/background with bad python_level → 422"""

def test_save_background_learning_goal_too_long():
    """POST /api/user/background with 250-char learning_goal → 422"""

def test_save_background_unauthenticated():
    """POST /api/user/background without JWT → 401"""

def test_get_background_exists():
    """GET /api/user/background when saved → 200 + record"""

def test_get_background_not_found():
    """GET /api/user/background when not saved → 404"""

def test_get_background_unauthenticated():
    """GET /api/user/background without JWT → 401"""
```
