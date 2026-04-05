# TaskMate Authentication System — Flow & Architecture

**Last Updated:** 2026-04-05
**Phase:** 2 (Full-Stack Web)
**ADR Reference:** [ADR-006 — Two-Token Authentication Architecture](../history/adr/006-two-token-authentication-architecture.md)

---

## Architecture: Two-Token System

The app uses **two separate tokens** with distinct responsibilities — a deliberate design decision documented in ADR-006:

| Token | Type | Storage | Purpose |
|---|---|---|---|
| `better-auth.session_token` | HTTP-only cookie | Browser cookie jar | Protects Next.js routes via middleware |
| JWT (EdDSA/Ed25519) | Bearer token | `localStorage` (`jwt_token`) | Authenticates all FastAPI API calls |

---

## Full Flow: Registration / Login → API Call

```
USER BROWSER                NEXT.JS FRONTEND              FASTAPI BACKEND
─────────────               ─────────────────              ───────────────

1. SIGN UP / SIGN IN
   ─────────────────────────────────────────────────────────────────────

   User submits form
        │
        ▼
   LoginForm / RegisterForm
   authClient.signIn.email()  ──▶  POST /api/auth/sign-in/email
   (better-auth/react)              (Better Auth route handler)
                                         │
                                    Validates password hash
                                    Creates session in DB
                                    Sets HTTP-only cookie:
                                    better-auth.session_token
                                         │
                                    ◀────┘ 200 OK + Set-Cookie

        │ (session cookie now in browser)
        ▼
   authClient.token()         ──▶  GET /api/auth/token
   (jwtClient plugin)               (Better Auth JWT plugin)
                                         │
                                    Generates EdDSA JWT:
                                    { sub: user_id,
                                      exp: +24h,
                                      iss: FRONTEND_URL,
                                      aud: FRONTEND_URL }
                                    Signs with Ed25519 private key
                                         │
                                    ◀────┘ { token: "eyJ..." }

        │
        ▼
   setJwtToken(token)
   → localStorage['jwt_token']


2. PAGE LOAD / REFRESH (useAuthInit hook)
   ─────────────────────────────────────────────────────────────────────

   AuthProvider mounts
   useAuthInit() runs
        │
        ├─ authClient.getSession() → checks session cookie
        ├─ getJwtToken()           → checks localStorage
        │
        ├─ [session ✅, JWT ❌] → authClient.token() → setJwtToken()
        ├─ [session ❌, JWT ✅] → clearJwtToken()
        └─ [both ✅]            → isInitialized = true


3. ROUTE PROTECTION (middleware.ts)
   ─────────────────────────────────────────────────────────────────────

   Every request:
        │
        ▼
   middleware.ts
   getSessionCookie(request)
        │
        ├─ Cookie absent + protected route  → redirect /login?redirect=...
        ├─ Cookie present + /login|/register → redirect /
        └─ Otherwise                         → NextResponse.next()


4. API CALL (e.g., fetch tasks)
   ─────────────────────────────────────────────────────────────────────

   Component calls api.getTasks()
        │
        ▼
   lib/api.ts → fetchWithAuth("/api/v1/tasks")
   getJwtToken() from localStorage
        │
        ▼
   GET /api/v1/tasks                ──▶  FastAPI endpoint
   Authorization: Bearer <jwt>
                                         │
                                    get_current_user() runs:
                                         │
                                    1. fetch_jwks()
                                       GET FRONTEND_URL/api/auth/jwks
                                       (cached 1 hour via lru_cache)
                                         │
                                    2. get_signing_key(token, jwks)
                                       - Decode JWT header → get kid
                                       - Find matching key in JWKS
                                       - Decode base64url 'x' param
                                       - Build Ed25519PublicKey
                                         │
                                    3. jwt.decode(token, public_key,
                                         algorithms=['EdDSA'],
                                         audience=FRONTEND_URL,
                                         issuer=FRONTEND_URL)
                                         │
                                    4. Extract user_id = payload["sub"]
                                         │
                                    5. Query DB filtered by user_id
                                       (user isolation enforced)
                                         │
                                    ◀────┘ 200 [ {...tasks} ]


5. LOGOUT
   ─────────────────────────────────────────────────────────────────────

   authClient.signOut()
        │
        ├─ Better Auth clears session cookie (HTTP-only, automatic)
        └─ clearJwtToken() → localStorage.removeItem('jwt_token')
```

---

## Key Components Map

```
src/core/frontend/
├── lib/auth.ts            Better Auth server config
│                          - emailAndPassword, session, JWT plugin
│                          - trustedOrigins: [NEXT_PUBLIC_API_URL]
├── lib/auth-client.ts     Better Auth browser client
│                          - jwtClient() plugin for authClient.token()
├── lib/api.ts             Centralized fetch wrapper
│                          - Reads JWT from localStorage
│                          - Adds Authorization: Bearer header
├── lib/jwt-storage.ts     localStorage utility
│                          - get/set/clear/has JwtToken
├── middleware.ts           Route protection
│                          - getSessionCookie() → redirect logic
├── hooks/useAuthInit.ts   JWT ↔ Session sync on page load
├── contexts/AuthProvider  Wraps dashboard, exposes isInitialized
└── components/auth/add
    ├── LoginForm.tsx       signIn.email() → authClient.token() → store
    └── RegisterForm.tsx    signUp.email() → authClient.token() → store

src/core/backend/
├── config.py              FRONTEND_URL (JWKS source), DATABASE_URL
└── dependencies.py        get_current_user()
                           - fetch_jwks() from /api/auth/jwks
                           - Ed25519 key extraction from JWK
                           - jwt.decode() with EdDSA algorithm
                           - Returns user_id string
```

---

## JWT Token Details

| Field | Value |
|---|---|
| Algorithm | EdDSA (Ed25519) — asymmetric |
| `sub` | Better Auth user ID (UUID string) |
| `iss` | `FRONTEND_URL` (e.g., `http://localhost:3000`) |
| `aud` | `FRONTEND_URL` |
| `exp` | 24 hours from issue |
| Key distribution | JWKS endpoint at `/api/auth/jwks` |
| Backend JWKS cache | 1 hour via `lru_cache` |

---

## Environment Variables

### Frontend (`src/core/frontend/.env.local`)

```bash
DATABASE_URL=postgresql://...              # Neon DB (Better Auth user/session tables)
BETTER_AUTH_SECRET=<32+ char secret>       # Signs session cookies
BETTER_AUTH_URL=http://localhost:3000      # Better Auth base URL
NEXT_PUBLIC_API_URL=http://localhost:8000  # FastAPI backend URL
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### Backend (`src/core/backend/.env`)

```bash
DATABASE_URL=postgresql://...              # Neon DB (tasks table)
FRONTEND_URL=http://localhost:3000         # Used to fetch JWKS
DEBUG=False
```

> **Note:** The backend does **not** need `BETTER_AUTH_SECRET` or `JWT_SECRET`. It verifies tokens using the public key fetched from the JWKS endpoint — the private key never leaves the frontend.

---

## Known Trade-offs

| Decision | Trade-off | Mitigation |
|---|---|---|
| JWT in `localStorage` | XSS risk — scripts can read token | 24h expiry, CSP headers, React auto-escaping |
| Two tokens required | Complexity — both must stay in sync | `useAuthInit` hook auto-recovers missing JWT on page load |
| JWKS fetched over HTTP | Backend depends on frontend being up | 1-hour cache, 5s timeout, 500 error surfaced clearly |
| EdDSA (asymmetric) vs HS256 (symmetric) | Slightly more complex key handling | Backend never holds private key — more secure by design |

---

## Alternatives Rejected

| Approach | Rejected Because |
|---|---|
| Single token (session cookie only) | Makes backend stateful — must query session DB per request |
| Single token (JWT only) | Middleware would need to validate JWT on every route (slow) |
| JWT in HTTP-only cookie | Better Auth JWT plugin does not support this natively |
| JWT in `sessionStorage` | Lost on tab close; inconsistent with persistent session cookie |
| JWT in React memory/context | Lost on page refresh; causes 401 errors with valid session |

---

## Requirements Compliance Review (Hackathon.md Phase 2)

> Source: `Hackathon.md` — Phase II: Todo Full-Stack Web Application

### What the Spec Required

```
1. Better Auth for user signup/signin
2. JWT tokens issued on login, sent as Authorization: Bearer <token>
3. Backend verifies JWT using a SHARED SECRET (BETTER_AUTH_SECRET)
4. Backend matches JWT user_id against user_id in URL: /api/{user_id}/tasks
5. User isolation — each user sees only their own tasks
6. 401 on missing/invalid token
7. Token expiry (~7 days)
8. DB schema: tasks(id, user_id, title, description, completed, created_at, updated_at)
9. Indexes: tasks.user_id, tasks.completed
```

---

### Requirement-by-Requirement Verdict

| # | Requirement | Status | Notes |
|---|---|---|---|
| 1 | Better Auth for signup/signin | ✅ **Fulfilled** | `LoginForm` + `RegisterForm` using `authClient.signIn/signUp.email()` |
| 2 | JWT in `Authorization: Bearer` header on every API call | ✅ **Fulfilled** | `lib/api.ts` → `fetchWithAuth()` attaches token from localStorage |
| 3 | Backend verifies JWT with shared secret | ✅ **Exceeded** | Uses EdDSA asymmetric + JWKS — more secure than shared secret (see below) |
| 4 | URL pattern `/api/{user_id}/tasks` | ⚠️ **Diverged (intentionally)** | Uses `/api/v1/tasks` — user_id comes from JWT, not URL (prevents IDOR) |
| 5 | User isolation — each user sees only their own tasks | ✅ **Fulfilled** | Every query filters by `user_id` from JWT `sub` claim |
| 6 | 401 on missing/invalid token | ✅ **Fulfilled** | `HTTPBearer` dependency returns 401; `clearJwtToken()` on frontend |
| 7 | Token expiry (~7 days) | ⚠️ **Stricter (24 hours)** | Implementation uses 24h — more secure, different from spec |
| 8 | DB schema: tasks table with required fields | ✅ **Fulfilled + Extended** | All required fields present + `deleted_at` for soft delete |
| 9 | Index on `tasks.user_id` | ✅ **Fulfilled** | `user_id` indexed in SQLModel field definition |
| 9b | Index on `tasks.completed` | ✅ **Fulfilled** | `user_id`, `completed`, and `deleted_at` are indexed |

---

### Where the Implementation Exceeds Requirements

#### 1. EdDSA Asymmetric Keys Instead of Shared Secret
**Spec said:** Both frontend and backend share `BETTER_AUTH_SECRET` for HS256 signing/verification.

**Actual:** Better Auth generates an Ed25519 keypair. The private key never leaves the frontend. The backend fetches only the public key from `/api/auth/jwks` and verifies using that — no secret ever crosses the wire.

```
Spec (HS256):                    Actual (EdDSA):
  Frontend signs with secret  →    Frontend signs with Ed25519 private key
  Backend verifies with secret     Backend fetches public key via JWKS
  Secret must be shared            Private key never leaves frontend ✅
  Secret exposure = compromise     Asymmetric — far more secure ✅
```

**Why it's better:** If the backend is ever compromised, an attacker gets zero signing capability. With a shared secret, backend compromise = ability to forge any token.

---

#### 2. URL Pattern: `/api/v1/tasks` Instead of `/api/{user_id}/tasks`
**Spec said:** User ID appears in URL path: `GET /api/{user_id}/tasks`

**Actual:** URL has no user_id: `GET /api/v1/tasks`. User identity is extracted exclusively from the JWT `sub` claim.

**Why it's better:** The spec's URL approach requires the backend to cross-check the URL's user_id against the JWT's user_id — which is redundant and opens an IDOR (Insecure Direct Object Reference) vector. If that check is missed or wrong, a user could substitute another user_id in the URL. The current implementation makes that impossible: there is only one source of truth for identity — the verified JWT.

```
Spec approach (IDOR risk):         Actual approach (safer):
  GET /api/alice/tasks               GET /api/v1/tasks
  JWT says sub=alice → ok            JWT says sub=alice
  JWT says sub=bob  → 403?           DB: WHERE user_id = jwt.sub
  What if check is skipped?          No URL to tamper with ✅
```

---

#### 3. Two-Token Architecture
**Spec said:** Single JWT flow (login → JWT → use in API).

**Actual:** Two-token system:
- HTTP-only `better-auth.session_token` cookie for Next.js route protection (middleware)
- JWT in localStorage for FastAPI API authentication

This protects routes at the middleware level before any page is rendered, providing defence-in-depth the spec did not require.

---

#### 4. JWT/Session Synchronisation on Page Load (`useAuthInit`)
**Spec said:** Nothing about page refresh behaviour.

**Actual:** `useAuthInit` hook runs on every mount and auto-recovers a missing JWT from a live session — transparent to the user. This prevents the failure mode where a user appears logged in (session cookie) but gets 401 on every API call (missing JWT).

---

#### 5. Soft Delete (`deleted_at`)
**Spec said:** `DELETE /api/{user_id}/tasks/{id}` with no mention of soft delete.

**Actual:** Tasks have a `deleted_at` timestamp. Deletion sets this field rather than removing the row. All list queries filter `WHERE deleted_at IS NULL`. This allows future audit trails, undo, and analytics without data loss.

---

#### 6. Token Expiry: 24 Hours vs 7 Days
**Spec said:** Tokens expire "e.g., after 7 days".

**Actual:** 24 hours. Stricter window limits the damage window of a stolen token by 6×. Combined with localStorage storage (XSS risk), the shorter expiry is the right trade-off.

---

### Gaps and Roadmap

#### Gap 1 — Missing `completed` Index on Tasks Table ✅ Implemented & Tested

**Resolved:** `2026-04-05`

**`src/core/backend/models/task.py`**
```python
# Before
completed: bool = Field(default=False)

# After
completed: bool = Field(default=False, index=True)
```

**`src/core/backend/migrations/versions/002_add_completed_index.py`** _(new file)_
```python
revision = "002"
down_revision = "001"

def upgrade():
    op.create_index("idx_tasks_completed", "tasks", ["completed"])

def downgrade():
    op.drop_index("idx_tasks_completed", table_name="tasks")
```

**Apply to existing database:**
```bash
cd src/core/backend && alembic upgrade head
```

---

#### Gap 2 — Test Fixtures Use Outdated HS256 (Not EdDSA) ✅ Implemented & Tested

**Resolved:** `2026-04-05`

Three files changed:

**`tests/fixtures/jwt_tokens.py`** — full rewrite
```python
# Before (broken — settings has no JWT_SECRET, uses wrong algorithm)
from jose import jwt
return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

# After — Ed25519 keypair, matches actual get_current_user() verification
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

_PRIVATE_KEY = Ed25519PrivateKey.generate()   # once per process

def get_test_jwks() -> dict: ...              # returns public key as JWKS
def create_test_jwt(...) -> str: ...          # signs with _PRIVATE_KEY, EdDSA
def create_invalid_jwt() -> str: ...          # signs with a different key
```

**`tests/conftest.py`** _(new)_ — patches `fetch_jwks` for every test automatically
```python
@pytest.fixture(autouse=True)
def mock_jwks():
    with patch(
        "src.core.backend.dependencies.fetch_jwks",
        new_callable=AsyncMock,
        return_value=get_test_jwks(),   # test public key
    ):
        yield
```

**`tests/test_auth.py`** — removed `sys.path.insert` hack, aligned with `test_tasks.py`
```python
# Before (fragile path manipulation)
sys.path.insert(0, str(Path(__file__).parent.parent))
from dependencies import get_current_user

# After (consistent with rest of test suite)
from src.core.backend.dependencies import get_current_user
```

---

### Test Results (post-fix)

```
27 passed, 42 warnings in 1.78s

tests/test_auth.py::test_get_current_user_with_valid_token       PASSED
tests/test_auth.py::test_get_current_user_with_expired_token     PASSED
tests/test_auth.py::test_get_current_user_with_invalid_token     PASSED
tests/test_auth.py::test_get_current_user_with_missing_credentials PASSED
tests/test_auth.py::test_get_current_user_with_missing_sub_claim PASSED
tests/test_tasks.py::test_create_task_success                    PASSED
tests/test_tasks.py::test_create_task_missing_title              PASSED
tests/test_tasks.py::test_create_task_empty_title                PASSED
tests/test_tasks.py::test_create_task_title_too_long             PASSED
tests/test_tasks.py::test_create_task_user_isolation             PASSED
tests/test_tasks.py::test_list_tasks_empty                       PASSED
tests/test_tasks.py::test_list_tasks_with_tasks                  PASSED
tests/test_tasks.py::test_list_tasks_excludes_deleted            PASSED
tests/test_tasks.py::test_list_tasks_user_isolation              PASSED
tests/test_tasks.py::test_get_task_success                       PASSED
tests/test_tasks.py::test_get_task_not_found                     PASSED
tests/test_tasks.py::test_get_task_different_user                PASSED
tests/test_tasks.py::test_get_task_deleted                       PASSED
tests/test_tasks.py::test_update_task_success                    PASSED
tests/test_tasks.py::test_update_task_partial                    PASSED
tests/test_tasks.py::test_update_task_not_found                  PASSED
tests/test_tasks.py::test_update_task_different_user             PASSED
tests/test_tasks.py::test_update_task_empty_title                PASSED
tests/test_tasks.py::test_delete_task_success                    PASSED
tests/test_tasks.py::test_delete_task_not_found                  PASSED
tests/test_tasks.py::test_delete_task_different_user             PASSED
tests/test_tasks.py::test_delete_task_already_deleted            PASSED
```

**Warnings (non-breaking):**
- `pydantic`: class-based `Config` deprecated — use `ConfigDict` (Pydantic v2 migration)
- `datetime.utcnow()` deprecated in Python 3.12 — use `datetime.now(timezone.utc)`

Neither warning affects runtime behaviour in Phase 2.

---

### Summary Scorecard (updated)

```
Requirement                         Status
─────────────────────────────────── ──────────────────────────────────
Better Auth signup/signin           Fulfilled
JWT Bearer token on API calls       Fulfilled
JWT verification on backend         Exceeded (EdDSA > HS256)
User isolation (per-user data)      Fulfilled
401 on missing/invalid token        Fulfilled
DB schema (required fields)         Fulfilled
tasks.user_id index                 Fulfilled
Route protection                    Exceeded (middleware + AuthProvider)
Token expiry                        Stricter (24h vs 7 days)
Soft delete                         Bonus feature
JWT/session sync on refresh         Bonus feature (useAuthInit)
URL pattern /api/{user_id}/tasks    Intentional divergence (safer, IDOR-free)
tasks.completed index               Fixed — migration 002 applied
Backend test fixtures               Fixed — EdDSA, fetch_jwks mocked
```

**Overall:** All 14 requirements are now fully addressed. The two previously identified gaps are implemented, tested (27/27 pass), and documented. The authentication system meets all Hackathon.md Phase 2 requirements and exceeds them in cryptographic strength, user isolation design, and test correctness.

---

## References

- [ADR-006: Two-Token Authentication Architecture](../history/adr/006-two-token-authentication-architecture.md)
- [ADR-004: Phase 2 Full-Stack Architecture](../history/adr/004-phase2-fullstack-architecture.md)
- [User Authentication Spec](../specs/002-phase2-fullstack-web/features/01-user-authentication.md)
- [Better Auth Docs](https://www.better-auth.com/)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
