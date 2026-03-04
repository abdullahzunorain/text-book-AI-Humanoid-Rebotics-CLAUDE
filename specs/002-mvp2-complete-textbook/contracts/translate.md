# API Contract: POST /api/translate

**Feature**: 002-mvp2-complete-textbook  
**Phase**: C (Urdu Translation)  
**Authentication**: None (public endpoint)

## Endpoint

```
POST /api/translate
Content-Type: application/json
```

## Request Schema

```json
{
  "chapter_slug": "string"
}
```

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| chapter_slug | string | Yes | Regex: `^[a-zA-Z0-9/_-]+$`, no `..` | `"module2-simulation/chapter1-gazebo-basics"` |

## Response Schemas

### 200 OK — Translation successful

```json
{
  "translated_content": "# گیزبو کی بنیادیں\n\n## سیکھنے کے مقاصد\n...\n\n```python\nimport rclpy\n```\n\n...",
  "original_code_blocks": [
    "```python\nimport rclpy\nfrom rclpy.node import Node\n```",
    "```bash\nros2 run my_pkg my_node\n```"
  ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| translated_content | string | Full chapter in Urdu with code blocks in English. Markdown format. |
| original_code_blocks | string[] | List of original fenced code blocks extracted before translation |

### 400 Bad Request — Invalid slug

```json
{
  "detail": "Invalid chapter_slug format"
}
```

### 404 Not Found — Chapter file missing

```json
{
  "detail": "Chapter not found: module99-fake/chapter1"
}
```

### 500 Internal Server Error — Translation service failure

```json
{
  "detail": "Translation service temporarily unavailable"
}
```

### 429 Too Many Requests — Rate limit exceeded

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

Headers: `Retry-After: 60`

## Rate Limiting

- **Limit**: 10 requests/minute per IP address
- **Implementation**: In-memory counter keyed by client IP (reset every 60s)
- **Scope**: `/api/translate` only

## Behavior

1. Validate `chapter_slug` format (regex check, path traversal prevention)
2. Read markdown file from `website/docs/{chapter_slug}.md`
3. Extract fenced code blocks (```...```) → replace with `{{CODE_BLOCK}}` placeholders
4. Send prose to Gemini gemini-2.5-flash for Urdu translation
5. Re-insert code blocks at placeholder positions
6. Return translated content + original code blocks list

## Performance

- Target: < 3 seconds p95
- Gemini call is the bottleneck (~1-2s)

## Test Cases

```python
# test_translate_api.py
def test_translate_valid_slug():
    """POST /api/translate with valid slug → 200 + has translated_content"""

def test_translate_invalid_slug():
    """POST /api/translate with '..' in slug → 400"""

def test_translate_missing_chapter():
    """POST /api/translate with nonexistent slug → 404"""

def test_translate_preserves_code_blocks():
    """Translated content contains original code blocks unchanged"""
```
