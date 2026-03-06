import re

path = "/mnt/c/Users/MY PC/Desktop/Hack-I-Copilot/specs/003-fix-auth-cookie-persistence/spec.md"
with open(path, "r") as f:
    content = f.read()

# 1. Add ## Clarifications section after Impact block (before ## User Scenarios)
clarifications = """## Clarifications

### Session 2025-07-16

- Q: What happens if APP_ENV=development accidentally leaks into a production (HTTPS) deployment - should there be a safety guard? -> A: Auto-detect: if the request origin uses HTTPS or a known production domain is in CORS origins, force Secure=True regardless of APP_ENV. Log a warning if APP_ENV contradicts.

"""
content = content.replace(
    "## User Scenarios & Testing",
    clarifications + "## User Scenarios & Testing"
)

# 2. Add FR-011 after FR-010
old_fr010 = "- **FR-010**: System MUST include all frontend origin URLs in the CORS allowed-origins list when credentials mode is enabled."
new_fr010 = old_fr010 + "\n- **FR-011**: System MUST auto-detect HTTPS context (via request scheme or presence of non-localhost production domains in CORS origins) and force `Secure=True` on cookies regardless of `APP_ENV`. If `APP_ENV=development` contradicts HTTPS detection, the system MUST log a warning but still enforce `Secure=True`."
content = content.replace(old_fr010, new_fr010)

# 3. Update Assumptions
old_assumption = "- The environment mode defaults to `development` if not explicitly set, ensuring safe behavior for local testing without additional configuration."
new_assumption = old_assumption + "\n- Even if `APP_ENV` is misconfigured, the auto-detect guard (FR-011) prevents Secure-flag omission on HTTPS deployments."
content = content.replace(old_assumption, new_assumption)

with open(path, "w") as f:
    f.write(content)

print(f"DONE: written {len(content)} chars")
