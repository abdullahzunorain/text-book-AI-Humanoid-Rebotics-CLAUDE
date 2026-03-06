# Tasks: Fix Cookie-Based Auth Persistence

**Input**: Design documents from `specs/003-fix-auth-cookie-persistence/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cookie-contract.md, quickstart.md
**Branch**: `003-fix-auth-cookie-persistence`
**TDD**: Yes — Red → Green → Refactor for all implementation tasks

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in every task

## User Stories (from spec.md)

| Story | Title | Priority | Spec Section |
|-------|-------|----------|-------------|
| US1 | Signup and Save Background | P1 | User Story 1 |
| US2 | Sign In After Previous Sign Out | P1 | User Story 2 |
| US3 | Production HTTPS Cookie Security | P1 | User Story 3 |
| US4 | Personalize Chapter After Auth | P2 | User Story 4 |

---

## Phase 1: Setup (Project Configuration)

**Purpose**: Add required environment variables and create scaffolding for new files

- [x] T001 Add `CORS_ORIGINS=http://localhost:3000,http://localhost:3001` to backend/.env
- [x] T002 [P] Create empty backend/tests/test_cookie_config.py with imports and docstring
- [x] T003 [P] Create empty backend/cookie_config.py with module docstring

---

## Phase 2: Foundational — Cookie Config Module (TDD)

**Purpose**: Build the centralized cookie attribute resolver that ALL user stories depend on. MUST complete before any story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### RED: Failing Tests for Cookie Config

- [x] T004 [P] Write failing test `test_dev_defaults` asserting `secure=False, samesite="lax"` when `APP_ENV=development` in backend/tests/test_cookie_config.py
- [x] T005 [P] Write failing test `test_dev_explicit_cors` asserting `secure=False, samesite="lax"` when `APP_ENV=development, CORS_ORIGINS=http://localhost:3000` in backend/tests/test_cookie_config.py
- [x] T006 [P] Write failing test `test_prod_env` asserting `secure=True, samesite="none"` when `APP_ENV=production, CORS_ORIGINS=https://example.com` in backend/tests/test_cookie_config.py
- [x] T007 [P] Write failing test `test_https_autodetect_overrides_dev` asserting `secure=True, samesite="none"` and warning logged when `APP_ENV=development, CORS_ORIGINS=https://example.com` in backend/tests/test_cookie_config.py
- [x] T008 [P] Write failing test `test_mixed_origins_https_wins` asserting `secure=True, samesite="none"` when `CORS_ORIGINS=http://localhost:3000,https://example.com` in backend/tests/test_cookie_config.py
- [x] T009 [P] Write failing tests `test_httponly_always_true`, `test_path_always_root`, `test_max_age_7_days` asserting invariant values in backend/tests/test_cookie_config.py

### GREEN: Implement Cookie Config

- [x] T010 Implement `get_cookie_config()` returning `{secure, samesite, httponly, path, max_age}` with APP_ENV + HTTPS auto-detect logic in backend/cookie_config.py
- [x] T011 Add HTTPS auto-detect warning log when `APP_ENV != "production"` but HTTPS origin detected in backend/cookie_config.py

### GREEN: Implement CORS from Env Var

- [x] T012 Replace hardcoded CORS origins list with `CORS_ORIGINS` env var parsing (split on comma, strip whitespace, default to localhost) in backend/main.py

### REFACTOR: Simplify and Verify

- [x] T013 Run `pytest backend/tests/test_cookie_config.py -v` — all 8 tests must pass. Simplify any redundant conditional logic in backend/cookie_config.py

**Checkpoint**: `get_cookie_config()` returns correct attributes for dev/prod/auto-detect. CORS reads from env var. All 8 config tests green.

---

## Phase 3: User Story 1 — Signup and Save Background (Priority: P1) 🎯 MVP

**Goal**: A new user signs up on localhost, gets the questionnaire, saves their background — all without 401 errors. Cookie is set with correct dev attributes.

**Independent Test**: Sign up from `http://localhost:3000`, verify questionnaire appears, fill in background fields, click save, confirm 200 from `/api/user/background`.

### RED: Failing Tests for US1

- [x] T014 [P] [US1] Write failing test `test_signup_sets_cookie_with_dev_attrs` asserting `Set-Cookie` header contains `token=...; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800` (no `Secure`) in backend/tests/test_auth_api.py
- [x] T015 [P] [US1] Write failing test `test_401_no_cookie_returns_not_authenticated` asserting `detail == "not_authenticated"` when no cookie sent to `GET /api/auth/me` in backend/tests/test_auth_api.py

### GREEN: Implement US1

- [x] T016 [US1] Modify `_set_token_cookie()` to call `get_cookie_config()` and pass all attributes dynamically to `response.set_cookie()` in backend/routes/auth.py
- [x] T017 [US1] Update `_get_user_id_from_cookie()` to raise `HTTPException(401, detail="not_authenticated")` when no cookie present in backend/routes/auth.py

### REFACTOR: Verify US1

- [x] T018 [US1] Run `pytest backend/tests/test_auth_api.py -v` — T014 and T015 tests pass. Verify signup → `/api/auth/me` → `/api/user/background` flow returns 200 via TestClient in backend/tests/test_auth_api.py

**Checkpoint**: Signup sets cookie with dev attrs (`Secure=False`, `SameSite=Lax`). Missing cookie returns `"not_authenticated"`. US1 is independently testable.

---

## Phase 4: User Story 2 — Sign In After Previous Sign Out (Priority: P1)

**Goal**: A returning user signs out, signs back in, and immediately has a valid session. Cookie is cleared correctly on sign-out and re-set on sign-in.

**Independent Test**: Sign in from `http://localhost:3000`, call `GET /api/auth/me` → 200. Sign out → 200. Call `/api/auth/me` → 401. Sign in again → `/api/auth/me` → 200.

### RED: Failing Tests for US2

- [x] T019 [P] [US2] Write failing test `test_signout_clears_cookie_matching_attrs` asserting `Set-Cookie: token=; ... Max-Age=0` with same `SameSite` and `Secure` as set call in backend/tests/test_auth_api.py
- [x] T020 [P] [US2] Write failing test `test_signin_sets_cookie_with_dev_attrs` asserting `Set-Cookie` header on signin matches signup cookie attributes in backend/tests/test_auth_api.py

### GREEN: Implement US2

- [x] T021 [US2] Modify `_clear_token_cookie()` to call `get_cookie_config()` and pass matching attributes with `max_age=0` in backend/routes/auth.py

### REFACTOR: Verify US2

- [x] T022 [US2] Run `pytest backend/tests/test_auth_api.py -v` — T019 and T020 tests pass. Verify signout → signin → `/api/auth/me` cycle works via TestClient in backend/tests/test_auth_api.py

**Checkpoint**: Sign-out clears cookie with matching attributes. Sign-in re-sets cookie. Full sign-out → sign-in cycle works. US2 is independently testable.

---

## Phase 5: User Story 3 — Production HTTPS Cookie Security (Priority: P1)

**Goal**: On production HTTPS deployment, cookies retain `Secure=True; SameSite=None; HttpOnly`. The auto-detect guard prevents misconfigured `APP_ENV` from disabling security. Expired and malformed JWTs return distinct 401 detail strings.

**Independent Test**: Run tests with `APP_ENV=production`, verify cookie attributes include `Secure` and `SameSite=None`. Verify expired JWT → `"session_expired"`, malformed JWT → `"invalid_token"`.

### RED: Failing Tests for US3

- [x] T023 [P] [US3] Write failing test `test_401_expired_returns_session_expired` using a JWT with `exp` in the past, asserting `detail == "session_expired"` on `GET /api/auth/me` in backend/tests/test_auth_api.py
- [x] T024 [P] [US3] Write failing test `test_401_malformed_returns_invalid_token` using a corrupted JWT string, asserting `detail == "invalid_token"` on `GET /api/auth/me` in backend/tests/test_auth_api.py

### GREEN: Implement US3

- [x] T025 [US3] Add `from jose import ExpiredSignatureError` and catch it specifically in `_get_user_id_from_cookie()` to return `detail="session_expired"` in backend/routes/auth.py
- [x] T026 [US3] Add catch for `JWTError` and generic `Exception` in `_get_user_id_from_cookie()` to return `detail="invalid_token"` in backend/routes/auth.py

### REFACTOR: Verify US3

- [x] T027 [US3] Run `pytest backend/tests/test_auth_api.py backend/tests/test_cookie_config.py -v` — all US3 tests pass. Verify `test_prod_env` and `test_https_autodetect_overrides_dev` still green in backend/tests/test_cookie_config.py

**Checkpoint**: Expired JWT → `"session_expired"`. Malformed JWT → `"invalid_token"`. Production config returns `Secure=True, SameSite=None`. Auto-detect guard works. US3 is independently testable.

---

## Phase 6: User Story 4 — Personalize Chapter After Auth (Priority: P2)

**Goal**: An authenticated user clicks "Personalize This Chapter" and gets personalized content. This validates the end-to-end flow: cookie persistence → authentication → downstream feature.

**Independent Test**: Sign in, navigate to a chapter, click "Personalize This Chapter", confirm personalized content renders (not a 401).

### Audit & Verify for US4

- [x] T028 [P] [US4] Audit that all authenticated fetch calls include `credentials: 'include'` in website/src/components/AuthProvider.tsx (4 calls), BackgroundQuestionnaire.tsx (1 call), PersonalizeButton.tsx (1 call)
- [x] T029 [P] [US4] Audit that `API_URL` resolves from `customFields.apiUrl` with `http://localhost:8000` fallback in website/src/components/AuthProvider.tsx, BackgroundQuestionnaire.tsx, PersonalizeButton.tsx, UrduTranslateButton.tsx, ChatbotWidget.tsx
- [x] T030 [P] [US4] Verify `docusaurus.config.ts` reads `process.env.REACT_APP_API_URL || 'http://localhost:8000'` in website/docusaurus.config.ts
- [x] T031 [US4] Verify personalize endpoint receives cookie and returns content (not 401) via TestClient signup → save-background → personalize flow in backend/tests/test_personalize_api.py

**Checkpoint**: All frontend fetch calls audited. API_URL config correct. Personalize works end-to-end with cookie auth. US4 is independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Regression testing, edge case validation, security hardening, documentation

- [x] T032 Run full regression test suite: `pytest backend/tests/ -v` — all 47+ existing tests plus new tests must pass
- [x] T033 [P] Manual edge case testing per specs/003-fix-auth-cookie-persistence/contracts/cookie-contract.md: multi-tab session sharing, port mismatch (`:3001`), cookie expiry behavior, sign-out+sign-in cycle in browser
- [x] T034 [P] Security validation checklist (S1-S6 from contracts/cookie-contract.md): verify HttpOnly always true, Secure conditional, SameSite conditional, max-age enforced, sign-out clears cookie, CORS+credentials correct
- [x] T035 [P] Run quickstart.md validation: follow all steps in specs/003-fix-auth-cookie-persistence/quickstart.md and verify each works
- [x] T036 Commit all changes in backend/ and website/ with message `fix: environment-aware cookie config for auth persistence (#003)`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (T001) — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 completion (T013 checkpoint)
- **US2 (Phase 4)**: Depends on Phase 2 completion. Can run in parallel with US1 (different test functions)
- **US3 (Phase 5)**: Depends on Phase 2 completion. Can run in parallel with US1/US2
- **US4 (Phase 6)**: Depends on Phase 2 completion. Benefits from US1 being done first for e2e validation
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallel With | Blocks |
|-------|-----------|-------------------|--------|
| US1 (Phase 3) | Phase 2 | US2, US3 | — |
| US2 (Phase 4) | Phase 2 | US1, US3 | — |
| US3 (Phase 5) | Phase 2 | US1, US2 | — |
| US4 (Phase 6) | Phase 2 (+ US1 for e2e) | US3 | — |

### Within Each User Story (TDD Order)

1. **RED**: Write tests FIRST — they MUST fail
2. **GREEN**: Implement the minimum code to make tests pass
3. **REFACTOR**: Clean up, verify checkpoint, run regression

### Parallel Opportunities

- T002 + T003: Scaffold files in parallel
- T004–T009: All cookie config tests can be written in parallel (same file, no deps)
- T014 + T015: US1 tests can be written in parallel
- T019 + T020: US2 tests can be written in parallel
- T023 + T024: US3 tests can be written in parallel
- T028 + T029 + T030: All frontend audits in parallel
- T033 + T034 + T035: All polish validations in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Step 1: Write ALL cookie config tests in parallel (T004-T009)
# These all go in backend/tests/test_cookie_config.py — same file but independent test functions
Task T004: test_dev_defaults
Task T005: test_dev_explicit_cors
Task T006: test_prod_env
Task T007: test_https_autodetect_overrides_dev
Task T008: test_mixed_origins_https_wins
Task T009: test_httponly_always_true + test_path_always_root + test_max_age_7_days

# Step 2: Run tests — all FAIL (RED phase complete)
pytest backend/tests/test_cookie_config.py -v  # 8 failures expected

# Step 3: Implement get_cookie_config() (T010-T011)
# Step 4: Implement CORS env var (T012)
# Step 5: Run tests — all PASS (GREEN phase complete)
pytest backend/tests/test_cookie_config.py -v  # 8 passes expected
```

## Parallel Example: User Story 1

```bash
# Step 1: Write US1 tests in parallel (T014 + T015)
Task T014: test_signup_sets_cookie_with_dev_attrs
Task T015: test_401_no_cookie_returns_not_authenticated

# Step 2: Run tests — FAIL (RED)
pytest backend/tests/test_auth_api.py -k "dev_attrs or not_authenticated" -v

# Step 3: Implement (T016 + T017) — both modify backend/routes/auth.py (sequential)
# Step 4: Verify (T018) — all tests pass (GREEN)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational — cookie config + CORS (T004-T013)
3. Complete Phase 3: User Story 1 — signup + save background (T014-T018)
4. **STOP and VALIDATE**: Sign up on localhost, save background, verify no 401
5. If US1 works → proceed to US2, US3, US4

### Incremental Delivery

1. Setup + Foundational → Cookie config module works, CORS reads from env
2. Add US1 → Signup flow works on localhost → **MVP delivered!**
3. Add US2 → Sign-out + sign-in cycle works → **Auth fully functional on dev**
4. Add US3 → Production security validated, distinct 401 codes → **Production-safe**
5. Add US4 → Personalize flow verified end-to-end → **Feature complete**
6. Polish → Regression + edge cases + security checklist → **Ship-ready**

### File Change Summary

| File | Action | Tasks |
|------|--------|-------|
| backend/.env | MODIFY | T001 |
| backend/tests/test_cookie_config.py | NEW | T002, T004-T009, T013 |
| backend/cookie_config.py | NEW | T003, T010-T011, T013 |
| backend/main.py | MODIFY | T012 |
| backend/routes/auth.py | MODIFY | T016-T017, T021, T025-T026 |
| backend/tests/test_auth_api.py | MODIFY | T014-T015, T018-T020, T022-T024, T027 |
| website/src/components/*.tsx | AUDIT ONLY | T028-T029 |
| website/docusaurus.config.ts | AUDIT ONLY | T030 |

---

## Notes

- [P] tasks = different files or independent test functions, no blocking dependencies
- [Story] label maps each task to its user story for traceability
- TDD is mandatory: RED tests MUST fail before GREEN implementation
- All 47 existing tests must continue passing after every phase
- Commit after each phase checkpoint
- Frontend files are **audit only** — no code changes needed (credentials + API_URL already correct)
- `auth_utils.py` is **unchanged** — `decode_token()` already re-raises `JWTError`/`ExpiredSignatureError`
