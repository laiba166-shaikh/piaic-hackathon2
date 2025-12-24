# Implementation Plan: User Authentication

**Branch**: `002-phase2-fullstack-web` | **Date**: 2025-12-21 | **Spec**: [01-user-authentication.md](./01-user-authentication.md)
**Input**: Feature specification from `specs/002-phase2-fullstack-web/features/01-user-authentication.md`

## Summary

Implement secure user authentication for the multi-user task management application using Better Auth library on the frontend and JWT token validation on the backend. Better Auth manages user credentials, registration, login, and JWT token issuance entirely on the frontend, while the backend validates JWT tokens to enforce user isolation. This is a foundational feature that enables all other Phase 2 features by establishing secure user identity and session management without requiring a users table in the backend database.

**Technical Approach:** Frontend-managed authentication with JWT validation on backend (NO backend users table).

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, React 18+, Next.js 15+ (App Router)
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Better Auth (authentication), Next.js API Routes, React
- Backend: FastAPI, PyJWT (JWT validation), Python-JOSE
- Shared: JWT tokens (HS256 algorithm)

**Storage**:
- Frontend: PostgreSQL (Neon) for Better Auth user storage
- Backend: PostgreSQL (Neon) for task data (NO users table)
- Browser: HTTP-only cookies for JWT token storage

**Testing**:
- Frontend: Vitest (unit tests), React Testing Library, Playwright (E2E)
- Backend: Pytest, FastAPI TestClient

**Target Platform**:
- Frontend: Web browsers (Chrome, Firefox, Safari, Edge) running Next.js client
- Backend: Linux server running FastAPI (Uvicorn)

**Project Type**: Web application (frontend + backend monorepo)

**Performance Goals**:
- Authentication operations < 500ms (login, register)
- JWT validation < 50ms (backend dependency)
- Session check < 100ms (frontend middleware)

**Constraints**:
- NO users table in backend database (trusts JWT tokens)
- NO backend authentication endpoints (Better Auth handles on frontend)
- JWT tokens expire after 24 hours (no refresh tokens in Phase 2)
- HTTP-only cookies (prevents XSS attacks)
- Stateless backend (no session storage)

**Scale/Scope**:
- Support: 1000+ concurrent users
- JWT tokens: 256-bit secret, HS256 algorithm
- 10 UI components (login, register, logout, middleware, error states)
- 1 backend dependency function (get_current_user)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development ✅ PASS
- **Requirement:** Feature has complete markdown specification with 12 sections
- **Status:** PASS - 01-user-authentication.md contains all 12 required sections (Feature Name, Overview, Priority, Dependencies, User Stories, Acceptance Criteria, Edge Cases, Error Handling, Non-Goals, API Contract, Data Model, UI/UX)
- **Evidence:** Feature spec exists at specs/002-phase2-fullstack-web/features/01-user-authentication.md

### II. Clean Code and Proper Structure ✅ PASS
- **Requirement:** Code must follow clean code principles (readability, modularity, scalability, type hints)
- **Status:** PASS - Plan includes:
  - **Modularity:** Centralized API client (lib/api.ts), reusable auth components, dependency injection
  - **Scalability:** Stateless backend, JWT tokens (no session storage), indexed user_id field
  - **Type Hints:** TypeScript on frontend, Python type hints on backend (Pydantic models)
  - **Readability:** Clear separation (Better Auth on frontend, JWT validation on backend)

### III. Test-First (NON-NEGOTIABLE) ✅ PASS
- **Requirement:** Tests written before implementation (TDD red-green-refactor)
- **Status:** PASS - Plan includes TDD workflow:
  - **Frontend Tests:** Login form unit tests, registration validation tests, middleware E2E tests
  - **Backend Tests:** JWT validation unit tests, get_current_user dependency tests, error handling tests
  - **Red-Green-Refactor:** Write failing test → implement → refactor
  - **Test Automation:** All tests run in CI/CD pipeline

### IV. Version Control and CI/CD ✅ PASS
- **Requirement:** GitHub repository, pull requests, automated testing, semantic versioning
- **Status:** PASS - Plan aligns with:
  - **Repository:** Monorepo structure (frontend/ and backend/ directories)
  - **Pull Requests:** Feature implemented on 002-phase2-fullstack-web branch
  - **CI/CD:** Tests run on pull request (GitHub Actions)
  - **Versioning:** Phase 2 version (aligns with project roadmap)

### V. Observability and Logging ✅ PASS
- **Requirement:** Structured logging for errors, events, performance
- **Status:** PASS - Plan includes logging:
  - **Error Logging:** Failed login attempts, invalid JWT tokens, missing secrets
  - **Event Logging:** Successful login, logout, registration, token validation
  - **Performance Logging:** Authentication operation duration, JWT validation time
  - **Stack Traces:** All exceptions logged with context

### Performance Standards ✅ PASS
- **Requirement:** CRUD operations < 500ms, optimized queries, indexed fields
- **Status:** PASS
  - **Authentication < 500ms:** Better Auth optimized for fast login/register
  - **JWT Validation < 50ms:** Stateless validation with cached secret
  - **Indexed Fields:** user_id indexed in tasks table for fast filtering
  - **Query Optimization:** All queries filter by user_id (indexed)

### Security Requirements ✅ PASS
- **Requirement:** Secure authentication, encryption, parameterized queries, input sanitization
- **Status:** PASS - Plan implements:
  - **Authentication:** JWT tokens (HS256), HTTP-only cookies (XSS protection), SameSite=Strict (CSRF protection)
  - **Encryption:** Passwords hashed by Better Auth (bcrypt), JWT signed with secret
  - **SQL Injection:** SQLModel uses parameterized queries (automatic protection)
  - **XSS Protection:** Input sanitization on forms, React auto-escapes output
  - **User Isolation:** All queries filter by user_id from JWT (prevents cross-user access)

### Success Criteria ✅ PASS
- **Functionality:** Login, register, logout, protected routes, JWT validation all implemented
- **Code Quality:** Clean separation (frontend auth vs backend validation), typed interfaces
- **Performance:** All operations under 500ms target
- **Security:** No security vulnerabilities (JWT validation, HTTP-only cookies, user isolation)
- **UX:** Intuitive forms with validation, clear error messages, loading states
- **Documentation:** Complete plan.md, research.md, data-model.md, quickstart.md

### Compliance ✅ PASS
- **GDPR:** User data stored securely, encrypted in transit and at rest
- **Licensing:** MIT license (inherited from project), all dependencies compatible

**GATE RESULT:** ✅ ALL CHECKS PASS - Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/002-phase2-fullstack-web/features/
├── 01-user-authentication.md  # Feature spec (input)
├── plan.md                    # This file (/sp.plan output)
├── research.md                # Phase 0 output (to be generated)
├── data-model.md              # Phase 1 output (to be generated)
├── quickstart.md              # Phase 1 output (to be generated)
├── contracts/                 # Phase 1 output (to be generated)
│   ├── jwt-validation.md      # Backend JWT dependency contract
│   └── better-auth-flow.md    # Frontend auth flow documentation
└── tasks.md                   # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Option 2: Web application (frontend + backend monorepo)

hackathon2/
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   │   └── page.tsx              # Login page component
│   │   ├── register/
│   │   │   └── page.tsx              # Registration page component
│   │   ├── middleware.ts             # Auth middleware (protected routes)
│   │   └── layout.tsx                # Global layout (logout button)
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx         # Login form component
│   │   │   ├── RegisterForm.tsx      # Registration form component
│   │   │   ├── LogoutButton.tsx      # Logout button component
│   │   │   └── PasswordToggle.tsx    # Show/hide password component
│   │   └── ui/
│   │       ├── ErrorMessage.tsx      # Reusable error message
│   │       ├── LoadingSpinner.tsx    # Loading indicator
│   │       └── Toast.tsx             # Toast notification (session expired)
│   ├── lib/
│   │   ├── auth.ts                   # Better Auth configuration
│   │   └── api.ts                    # Centralized API client
│   ├── hooks/
│   │   └── useAuth.ts                # Auth state hook
│   ├── types/
│   │   └── auth.ts                   # TypeScript auth types
│   └── tests/
│       ├── unit/
│       │   ├── LoginForm.test.tsx
│       │   ├── RegisterForm.test.tsx
│       │   └── useAuth.test.ts
│       └── e2e/
│           ├── login.spec.ts
│           ├── register.spec.ts
│           └── protected-routes.spec.ts
│
├── backend/
│   ├── dependencies.py               # get_current_user dependency
│   ├── config.py                     # JWT_SECRET configuration
│   ├── main.py                       # FastAPI app (CORS, middleware)
│   ├── api/
│   │   └── v1/
│   │       └── tasks.py              # Task routes (uses get_current_user)
│   └── tests/
│       ├── test_dependencies.py      # JWT validation tests
│       ├── test_auth_flow.py         # Integration tests
│       └── fixtures/
│           └── jwt_tokens.py         # Test JWT token generators
│
├── shared/
│   └── types/
│       └── auth.ts                   # Shared auth types (TypeScript/Python)
│
└── .env                              # JWT_SECRET shared between frontend/backend
```

**Structure Decision:** Web application monorepo structure with separate frontend and backend directories. Frontend contains Better Auth integration, UI components, and authentication flow. Backend contains JWT validation dependency and protected API routes. Shared types ensure consistency between frontend and backend. No users table in backend database - Better Auth manages users entirely on frontend side.

## Complexity Tracking

> **This section is intentionally empty** - No constitutional violations exist for this feature. All complexity is justified:
> - **No Repository Pattern:** Direct SQLModel usage is constitutional (simple, testable)
> - **Monorepo:** Justified by spec-driven architecture (single source of truth)
> - **Frontend-Managed Auth:** Justified by separation of concerns (Better Auth handles user management, backend validates tokens)

No violations to justify.

## Phase 0: Research & Decision Documentation

**Status:** To be generated in research.md

**Unknowns to Research:**
1. Better Auth configuration for Next.js 15 App Router
2. JWT secret sharing between frontend and backend (environment variables)
3. HTTP-only cookie configuration with SameSite and Secure flags
4. Better Auth database schema and migration setup
5. Frontend middleware pattern for protected routes (Next.js 15)
6. Backend JWT validation with PyJWT (algorithm, expiration, claims)
7. Error handling patterns for expired/invalid tokens
8. CORS configuration for frontend-backend communication
9. Testing patterns for JWT-based auth (mocking tokens)
10. Accessibility best practices for authentication forms

**Research Tasks:**
- [ ] Better Auth documentation review (Next.js integration, JWT token generation)
- [ ] Next.js 15 middleware patterns for authentication
- [ ] FastAPI JWT validation patterns (dependency injection)
- [ ] HTTP-only cookie security best practices
- [ ] CORS configuration for JWT cookies (credentials: 'include')
- [ ] Testing strategies for authentication flows (E2E and unit)
- [ ] Accessibility guidelines for login/register forms (WCAG 2.1)

**Output:** research.md with decisions, rationale, and alternatives for each unknown.

## Phase 1: Design Artifacts

**Status:** To be generated after Phase 0 research

### Data Model (data-model.md)
- **Entities:** NO user entity in backend (Better Auth manages users on frontend)
- **Fields:** user_id field in tasks table (string, indexed, from JWT)
- **Relationships:** No relationships (no users table to reference)
- **Validation:** user_id must be present in JWT 'sub' claim
- **State Transitions:** N/A (authentication is stateless)

### API Contracts (contracts/ directory)
- **jwt-validation.md:** Backend get_current_user() dependency specification
  - Input: Authorization header or auth-token cookie
  - Process: JWT validation, expiration check, user_id extraction
  - Output: user_id string
  - Errors: 401 Unauthorized (missing/invalid/expired token)

- **better-auth-flow.md:** Frontend authentication flow documentation
  - Registration flow: signUp() → JWT issued → redirect to dashboard
  - Login flow: signIn() → JWT issued → redirect to dashboard
  - Logout flow: signOut() → cookie cleared → redirect to login
  - Session check: getSession() → auth status

### Quickstart Guide (quickstart.md)
- **Prerequisites:** Node.js 18+, Python 3.11+, PostgreSQL (Neon)
- **Setup Steps:**
  1. Install dependencies (frontend: npm install, backend: pip install)
  2. Configure environment variables (JWT_SECRET, DATABASE_URL)
  3. Run Better Auth migrations (frontend database setup)
  4. Start development servers (frontend: npm run dev, backend: uvicorn)
- **Testing:**
  1. Run frontend tests: npm run test
  2. Run backend tests: pytest
  3. Run E2E tests: npm run test:e2e
- **Verification:**
  - Visit /register → create account → redirected to dashboard
  - Visit /login → log in → redirected to dashboard
  - Visit / without auth → redirected to /login

## Next Steps After Planning

1. **Generate research.md** (Phase 0) - Resolve all unknowns listed above
2. **Generate data-model.md** (Phase 1) - Document user_id field specification
3. **Generate contracts/** (Phase 1) - JWT validation and Better Auth flow contracts
4. **Generate quickstart.md** (Phase 1) - Developer setup guide
5. **Run /sp.tasks** (Phase 2) - Generate tasks.md with test-driven implementation tasks
6. **Implement** (Phases 3-6) - Execute tasks in TDD red-green-refactor cycles

**Agent Coordination:**
- **Spec Coordinator:** Validates plan aligns with 01-user-authentication.md spec
- **Schema Architect:** Documents user_id field (no users table)
- **API Developer:** Implements get_current_user dependency (backend)
- **UI Developer:** Implements Better Auth integration, auth forms (frontend)
- **Test Engineer:** Writes TDD tests for auth flow (frontend and backend)

---

**Plan Status:** ✅ Technical Context and Constitution Check complete. Ready for Phase 0 research.
