# Phase 2 Implementation Tasks

**Generated:** 2025-12-25
**Branch:** 002-phase2-fullstack-web
**Status:** Ready for Implementation

---

## Table of Contents

1. [Task Format & Conventions](#task-format--conventions)
2. [Phase 0: Project Setup](#phase-0-project-setup)
3. [Phase 1: Foundational Infrastructure](#phase-1-foundational-infrastructure)
4. [Phase 2: Feature 1 - User Authentication](#phase-2-feature-1---user-authentication)
5. [Phase 3: Feature 2 - Task CRUD](#phase-3-feature-2---task-crud)
6. [Phase 4: Feature 3 - Task Completion](#phase-4-feature-3---task-completion)
7. [Phase 5: Integration & Polish](#phase-5-integration--polish)
8. [Task Summary](#task-summary)

---

## Task Format & Conventions

### Task Structure

```
- [ ] [TaskID] [P?] [Story?] Description with exact file path
```

**Legend:**
- `[TaskID]` - Sequential task identifier (T001, T002, etc.)
- `[P]` - Parallelizable (can run independently)
- `[Story]` - Feature label: [F1] Auth, [F2] CRUD, [F3] Completion
- Description - Clear action with exact file path

### Task States

- `[ ]` - Not started
- `[🔄]` - In progress
- `[✅]` - Completed
- `[❌]` - Blocked/Failed

### TDD Workflow

For each feature:
1. **RED** - Write failing tests first
2. **GREEN** - Implement code to pass tests
3. **REFACTOR** - Optimize and clean up

### Dependencies

- Tasks within a phase are sequentially dependent unless marked `[P]`
- Each phase must complete before next phase starts
- Database migrations must run before backend code
- Backend APIs must exist before frontend code

---

## Phase 0: Project Setup

**Duration:** 2-3 hours
**Goal:** Initialize monorepo structure and development environment

### Monorepo Structure

- [✅] **[T001]** [P] Create monorepo directory structure
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\`
  - **Directories:**
    - `src/core/backend/` - FastAPI application
    - `src/core/frontend/` - Next.js application
    - `src/core/shared/` - Shared TypeScript types
  - **Acceptance:** All three directories exist with README.md files

- [✅] **[T001A]** [P] Create CLAUDE.md files for frontend and backend
  - **Paths:**
    - `D:\piaic-hackathon\hackathon2\src\core\frontend\CLAUDE.md`
    - `D:\piaic-hackathon\hackathon2\src\core\backend\CLAUDE.md`
  - **Purpose:** Provide Claude Code with context-specific guidelines for each part of the monorepo
  - **Content:**
    - Frontend CLAUDE.md: Next.js patterns, API client usage, Tailwind CSS conventions
    - Backend CLAUDE.md: FastAPI patterns, SQLModel usage, JWT validation, database conventions
  - **Acceptance:** Both CLAUDE.md files exist with comprehensive guidelines

- [✅] **[T002]** [P] Setup backend project (Python/FastAPI)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\`
  - **Actions:**
    - Create `pyproject.toml` with dependencies (FastAPI, SQLModel, Alembic, PyJWT)
    - Create `requirements.txt` for pip fallback
    - Create `.python-version` file (3.11+)
    - Create `src/core/backend/__init__.py`
    - Add `[tool.uv]` section in pyproject.toml
  - **Acceptance:** `uv pip install -e .` or `pip install -r requirements.txt` succeeds

- [✅] **[T003]** [P] Setup frontend project (Next.js 16+)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\`
  - **Actions:**
    - Run `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`
    - Install dependencies: `npm install better-auth @better-fetch/fetch jose`
    - Install dev dependencies: `npm install -D vitest @testing-library/react @testing-library/jest-dom`
    - Create `src/core/frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - **Acceptance:** `npm run dev` starts Next.js dev server

- [✅] **[T004]** Setup environment variables
  - **Paths:**
    - `D:\piaic-hackathon\hackathon2\.env.example`
    - `D:\piaic-hackathon\hackathon2\.env`
  - **Variables:**
    ```bash
    # Shared
    JWT_SECRET=your-256-bit-secret-key-here

    # Backend
    DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

    # Frontend
    NEXT_PUBLIC_API_URL=http://localhost:8000
    BETTER_AUTH_URL=http://localhost:3000
    BETTER_AUTH_SECRET=your-secret-key-here
    ```
  - **Acceptance:** `.env.example` exists for documentation, `.env` exists for local dev (gitignored)

- [✅] **[T005]** [P] Setup linters and formatters
  - **Backend:** Configure Ruff (`src/core/backend/pyproject.toml`)
  - **Frontend:** Configure ESLint and Prettier (`src/core/frontend/.eslintrc.json`, `src/core/frontend/.prettierrc`)
  - **Acceptance:** `ruff check src/core/backend/` and `npm run lint` run without errors

- [✅] **[T006]** Setup Git pre-commit hooks
  - **Path:** `D:\piaic-hackathon\hackathon2\.git\hooks\pre-commit`
  - **Actions:** Run linters before commit
  - **Acceptance:** Commit fails if linting errors exist

**Phase 0 Completed:** Monorepo structure ready, all tools installed

---

## Phase 1: Foundational Infrastructure

**Duration:** 3-4 hours
**Goal:** Setup database, backend framework, frontend framework, and shared types

### Database Setup

- [✅] **[T007]** Create Neon PostgreSQL database
  - **Actions:**
    - Sign up for Neon.tech free tier
    - Create project: `todo-app-eval`
    - Create database: `todo_db`
    - Copy connection string to `src/core/backend/.env`
  - **Acceptance:** Connection string saved in `.env`

- [✅] **[T008]** Setup Alembic migrations
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\migrations\`
  - **Actions:**
    - Run `alembic init migrations`
    - Configure `alembic.ini` to use `DATABASE_URL` from `.env`
    - Update `migrations/env.py` to import SQLModel models
  - **Acceptance:** `alembic current` runs without error

### Backend Foundation

- [✅] **[T009]** Create FastAPI application structure
  - **Paths:**
    - `D:\piaic-hackathon\hackathon2\src\core\backend\main.py`
    - `D:\piaic-hackathon\hackathon2\src\core\backend\config.py`
    - `D:\piaic-hackathon\hackathon2\src\core\backend\db.py`
  - **Actions:**
    - Create `main.py` with FastAPI app initialization
    - Create `config.py` with Pydantic Settings (JWT_SECRET, DATABASE_URL)
    - Create `db.py` with SQLModel engine and session dependency
  - **Acceptance:** `uvicorn src.core.backend.main:app --reload` starts server at http://localhost:8000

- [✅] **[T010]** [P] Configure CORS middleware
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\main.py`
  - **Config:**
    ```python
    allow_origins=["http://localhost:3000"]
    allow_credentials=True
    allow_methods=["*"]
    allow_headers=["*"]
    ```
  - **Acceptance:** Frontend can make API requests without CORS errors

- [✅] **[T011]** [P] Create health check endpoint
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\main.py`
  - **Endpoint:** `GET /health`
  - **Response:** `{"status": "ok"}`
  - **Acceptance:** `curl http://localhost:8000/health` returns 200 OK

### Frontend Foundation

- [✅] **[T012]** Configure Tailwind CSS with journal theme
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\tailwind.config.ts`
  - **Colors (Light & Dark Mode):**
    - Light Mode:
      - `paper.cream`: #F5F1E8
      - `paper.highlight`: #E6DFC8
      - `ink.black`: #2C3E50
      - `ink.faded`: rgba(44, 62, 80, 0.5)
      - `accent.blue`: #4A7C99
      - `neutral.pencil`: #9AA5A1
    - Dark Mode:
      - `paper.night`: #1E2428
      - `paper.highlight`: #2A3238
      - `ink.primary`: #E6E1D8
      - `ink.faded`: rgba(230, 225, 216, 0.5)
      - `accent.vintageBlue`: #7FA6BF
      - `neutral.pencilGray`: #A0A9A5
  - **Fonts:** Inter (body), Patrick Hand (heading), Courier Prime (mono)
  - **Acceptance:** Colors and fonts available via Tailwind classes, dark mode toggle implemented

- [✅] **[T013]** Setup Google Fonts
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\app\layout.tsx`
  - **Fonts:** Import Inter, Patrick_Hand, Courier_Prime from `next/font/google`
  - **Acceptance:** Fonts load and apply to text

- [✅] **[T014]** Create root layout with sidebar
  - **Paths:**
    - `D:\piaic-hackathon\hackathon2\src\core\frontend\app\layout.tsx`
    - `D:\piaic-hackathon\hackathon2\src\core\frontend\components\layout\Sidebar.tsx`
    - `D:\piaic-hackathon\hackathon2\src\core\frontend\components\layout\Header.tsx`
  - **Structure:** Sidebar (left, 240px), Header (top right), Main content
  - **Acceptance:** Layout renders with journal aesthetic

- [✅] **[T015]** Create centralized API client
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\lib\api.ts`
  - **Functions:** `fetchWithAuth()`, `api.getTasks()`, etc.
  - **Features:** Auto-include JWT cookie, error handling, response parsing
  - **Acceptance:** API client exports typed functions for all endpoints

### Shared Types

- [✅] **[T016]** [P] Create shared TypeScript types
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\shared\types\task.ts`
  - **Types:** `Task`, `TaskCreate`, `TaskUpdate`, `TaskResponse`
  - **Acceptance:** Types exported and usable in frontend code

**Phase 1 Completed:** Infrastructure ready for feature implementation ✅

---

## Phase 2: Feature 1 - User Authentication

**Duration:** 6-8 hours
**Goal:** Implement JWT-based authentication with Better Auth (frontend) and JWT validation (backend)

### Backend: JWT Validation (TDD)

#### RED - Write Failing Tests

- [✅] **[T017]** [F1] Write JWT validation tests (RED)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\tests\test_auth.py`
  - **Test Cases:**
    - `test_get_current_user_with_valid_token()` - Should extract user_id from JWT
    - `test_get_current_user_with_expired_token()` - Should return 401
    - `test_get_current_user_with_invalid_token()` - Should return 401
    - `test_get_current_user_with_missing_token()` - Should return 401
    - `test_get_current_user_with_missing_sub_claim()` - Should return 401
  - **Status:** Tests PASS (all 5 tests passing)
  - **Acceptance:** `pytest src/core/backend/tests/test_auth.py` shows 5 passing tests ✅

#### GREEN - Implement JWT Validation

- [✅] **[T018]** [F1] Implement get_current_user dependency (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\dependencies.py`
  - **Function:** `async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> str`
  - **Logic:**
    - Decode JWT with python-jose
    - Validate signature with JWT_SECRET
    - Extract user_id from 'sub' claim
    - Raise HTTPException(401) if invalid/expired/missing
  - **Acceptance:** All tests in T017 pass ✅

- [✅] **[T019]** [F1] Configure JWT_SECRET in config
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\config.py`
  - **Field:** `JWT_SECRET: str` (from environment variable)
  - **Validation:** Raise error if JWT_SECRET not set
  - **Acceptance:** Config loads JWT_SECRET from `.env` ✅

#### REFACTOR

- [✅] **[T020]** [F1] Add logging to JWT validation
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\dependencies.py`
  - **Actions:** Log failed validation attempts (without exposing tokens)
  - **Acceptance:** Logs show authentication events ✅

### Frontend: Better Auth Integration (TDD)

#### Setup Better Auth

- [✅] **[T021]** [F1] Setup Better Auth database (Neon)
  - **Actions:**
    - Create separate Neon database for Better Auth user data
    - Copy connection string to `src/core/frontend/.env.local` as `DATABASE_URL`
  - **Acceptance:** Better Auth can connect to database ✅
  - **Completed:** Neon database configured, connection string added to .env.local

- [✅] **[T022]** [F1] Configure Better Auth with JWT Plugin
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\lib\auth.ts`
  - **Config:**
    - Database URL
    - Secret (BETTER_AUTH_SECRET, shared with backend as JWT_SECRET)
    - Email/password provider
    - Session cookie settings (HTTP-only, SameSite=Strict)
    - **[NEW]** JWT plugin: `plugins: [jwt()]`
  - **JWT Plugin Configuration:**
    - Algorithm: HS256
    - Expiration: 24 hours (matches session)
    - Claims: `{ "sub": user_id, "exp": timestamp, "iat": timestamp }`
  - **Acceptance:**
    - ✅ Better Auth initialized with JWT plugin
    - ✅ `authClient.token()` endpoint available
    - ✅ JWT secret matches backend JWT_SECRET
  - **Completed:** auth.ts created with PostgreSQL pool, email/password auth, session config, JWT plugin

- [✅] **[T023]** [F1] Run Better Auth migrations
  - **Actions:** Run Better Auth migration to create users table
  - **Acceptance:** Users table exists in Better Auth database ✅
  - **Completed:** Migration successful - user, session, account, verification tables created

#### RED - Write Failing Frontend Tests

- [✅] **[T024]** [F1] Write login form tests (RED)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\components\auth\LoginForm.test.tsx`
  - **Test Cases:**
    - `test_login_form_renders_correctly()` ✅
    - `test_login_form_validation_requires_email()` ✅
    - `test_login_form_validation_requires_password()` ✅
    - `test_login_form_shows_error_on_failed_login()` ✅
    - `test_login_form_redirects_on_success()` ✅
    - `test_password_visibility_toggle()` ✅ (bonus test)
  - **Status:** Tests created (will FAIL until LoginForm component is implemented)
  - **Acceptance:** Test file created with 6 comprehensive test cases ✅

#### GREEN - Implement Auth UI

- [✅] **[T025]** [F1] Create login page (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\app\login\page.tsx`
  - **Component:** Server Component rendering LoginForm
  - **Acceptance:** Page accessible at /login ✅
  - **Completed:** Login page created with journal theme styling and link to register

- [✅] **[T026]** [F1] Create LoginForm component (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\auth\LoginForm.tsx`
  - **Fields:** Email (type="email"), Password (type="password", show/hide toggle)
  - **Validation:** Client-side validation before submission
  - **Actions:** Call Better Auth `signIn()`, redirect to / on success
  - **Acceptance:** All tests in T024 pass ✅
  - **Completed:** All 6 tests passing - form rendering, validation, error handling, success redirect, password toggle

#### JWT Token Retrieval & Storage

- [✅] **[T026A]** [F1] Create JWT storage utility
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\lib\jwt-storage.ts`
  - **Functions:**
    - `getJwtToken(): string | null` - Read JWT from localStorage
    - `setJwtToken(token: string): void` - Store JWT in localStorage
    - `clearJwtToken(): void` - Remove JWT from localStorage
    - `hasJwtToken(): boolean` - Check if JWT exists
  - **Storage Key:** `'jwt_token'`
  - **NOT in-memory:** Must use localStorage for persistence
  - **Acceptance:** JWT persists across page refreshes ✅

- [✅] **[T026B]** [F1] Integrate JWT retrieval in LoginForm
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\auth\LoginForm.tsx`
  - **After Better Auth signIn() success:**
    1. Call `authClient.token()` to retrieve JWT
    2. Store JWT: `setJwtToken(tokenResult.data.token)`
    3. Handle errors if token retrieval fails
  - **Acceptance:**
    - ✅ JWT retrieved after successful login
    - ✅ JWT stored in localStorage
    - ✅ Login fails if JWT retrieval fails

- [✅] **[T026C]** [F1] Integrate JWT retrieval in RegisterForm
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\auth\RegisterForm.tsx`
  - **After Better Auth signUp() success:**
    1. Call `authClient.token()` to retrieve JWT
    2. Store JWT: `setJwtToken(tokenResult.data.token)`
    3. Handle errors if token retrieval fails
  - **Acceptance:**
    - ✅ JWT retrieved after successful registration
    - ✅ JWT stored in localStorage
    - ✅ Registration fails if JWT retrieval fails

- [✅] **[T026D]** [F1] Update LogoutButton to clear JWT
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\auth\LogoutButton.tsx`
  - **On logout:**
    1. Call `authClient.signOut()` (clears session cookie)
    2. Call `clearJwtToken()` (clears JWT from localStorage)
  - **Acceptance:**
    - ✅ Both session cookie AND JWT cleared on logout
    - ✅ Subsequent API calls fail with 401 (no JWT)

- [✅] **[T027]** [F1] Create register page
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\app\register\page.tsx`
  - **Component:** Server Component rendering RegisterForm
  - **Acceptance:** Page accessible at /register ✅
  - **Completed:** Register page created with link to login

- [✅] **[T028]** [F1] Create RegisterForm component
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\auth\RegisterForm.tsx`
  - **Fields:** Email, Password (min 8 chars), Confirm Password
  - **Validation:** Password strength indicator, match validation
  - **Actions:** Call Better Auth `signUp()`, redirect to / on success
  - **Acceptance:** User can register and auto-login ✅
  - **Completed:** RegisterForm with name field, password strength indicator, confirmation matching

- [✅] **[T029]** [F1] Create LogoutButton component
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\auth\LogoutButton.tsx`
  - **Actions:** Call Better Auth `signOut()`, redirect to /login
  - **Placement:** In Header component
  - **Acceptance:** User can logout successfully ✅
  - **Completed:** LogoutButton added to Header with loading state

#### Middleware & Protection

- [✅] **[T030]** [F1] Create authentication middleware
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\middleware.ts`
  - **Logic:**
    - Check for auth-token cookie
    - Redirect to /login if not authenticated (for protected routes)
    - Redirect to / if authenticated (for /login, /register)
  - **Acceptance:** Middleware protects routes correctly ✅
  - **Completed:** Middleware checks Better Auth session cookie, protects all routes except auth pages and API

- [✅] **[T030A]** [F1] Create JWT refresh hook for page load
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\hooks\useAuthInit.ts`
  - **Purpose:** Refresh JWT on page load if session exists but JWT missing
  - **Logic:**
    ```typescript
    useEffect(() => {
      async function initAuth() {
        const session = await authClient.getSession();
        const jwt = getJwtToken();

        // Session exists but no JWT → retrieve JWT
        if (session.data && !jwt) {
          const tokenResult = await authClient.token();
          if (tokenResult.data) {
            setJwtToken(tokenResult.data.token);
          }
        }

        // No session → clear JWT if exists
        if (!session.data && jwt) {
          clearJwtToken();
        }
      }
      initAuth();
    }, []);
    ```
  - **Acceptance:**
    - ✅ JWT refreshed on page load if session exists
    - ✅ JWT cleared if no session exists
    - ✅ Backend API calls succeed after page refresh

#### REFACTOR

- [✅] **[T031]** [F1] Create reusable auth UI components
  - **Paths:**
    - `src/core/frontend\components\ui\ErrorMessage.tsx`
    - `src/core/frontend\components\ui\LoadingSpinner.tsx`
    - `src/core/frontend\components\auth\PasswordToggle.tsx`
  - **Acceptance:** Components reusable across auth forms ✅
  - **Completed:** ErrorMessage, LoadingSpinner, PasswordToggle components created and used in auth forms

### Integration Tests

- [✅] **[T032]** [F1] Write end-to-end auth flow tests
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\e2e\auth.spec.ts`
  - **Test Cases:**
    - ✅ Complete registration flow with validation
    - ✅ Complete login flow with error handling
    - ✅ Protected route access (middleware enforcement)
    - ✅ Complete logout flow
    - ✅ Password visibility toggle
    - ✅ Form validation (7 comprehensive tests total)
  - **Tool:** Playwright
  - **Acceptance:** E2E tests pass ✅
  - **Completed:** 7 comprehensive E2E tests covering full auth flow, Playwright configured

- [✅] **[T032A]** [F1] E2E test: JWT persistence after page refresh
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\e2e\auth.spec.ts`
  - **Test Flow:**
    1. Register new user → Login succeeds
    2. Verify JWT in localStorage
    3. **Refresh page**
    4. Verify JWT still in localStorage
    5. Make backend API call (GET /api/v1/tasks)
    6. **Assertion:** API call succeeds (200 OK, not 401)
  - **Failure Scenario:** If JWT lost on refresh, API call returns 401
  - **Acceptance:** Test passes (JWT persists, backend auth works)

**Phase 2 Completed:** User authentication fully functional ✅

---

## Phase 3: Feature 2 - Task CRUD

**Duration:** 8-10 hours
**Goal:** Implement full CRUD operations for tasks with user isolation

### Database: Tasks Table

- [✅] **[T033]** [F2] Create tasks table migration
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\migrations\versions\001_create_tasks.py`
  - **Schema:**
    - id (SERIAL, PRIMARY KEY)
    - user_id (VARCHAR(255), NOT NULL, INDEXED)
    - title (VARCHAR(200), NOT NULL)
    - description (TEXT, NULLABLE)
    - completed (BOOLEAN, DEFAULT FALSE)
    - priority, tags, due_date, recurrence (Phase 3+, nullable)
    - deleted_at (TIMESTAMP, NULLABLE, INDEXED)
    - created_at, updated_at (TIMESTAMP, AUTO)
  - **Indexes:** user_id, deleted_at, (user_id, deleted_at)
  - **Triggers:** Auto-update updated_at
  - **Acceptance:** `alembic upgrade head` creates table

- [✅] **[T034]** [F2] Create Task SQLModel
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\models\task.py`
  - **Model:** `class Task(SQLModel, table=True)`
  - **Fields:** All fields from migration
  - **Validation:** Title length, required fields
  - **Acceptance:** Model imports without errors

### Backend: Task CRUD API (TDD)

#### RED - Write Failing Tests

- [✅] **[T035]** [F2] Write task CRUD tests (RED)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\tests\test_tasks.py`
  - **Test Categories:**
    - **Create:** Valid creation, missing title, title too long, user isolation
    - **Read List:** Get user tasks, empty list, exclude deleted, exclude other users' tasks
    - **Read Single:** Get by ID, 404 for non-existent, 404 for other user's task
    - **Update:** Update title/description, 404 for non-existent, updated_at refreshes
    - **Delete:** Soft delete, 404 after delete, 404 for other user's task
    - **User Isolation:** User A cannot access User B's tasks
  - **Status:** Tests should FAIL (routes not implemented yet)
  - **Acceptance:** `pytest src/core/backend/tests/test_tasks.py` shows ~20 failing tests

#### GREEN - Implement Task CRUD

- [✅] **[T036]** [F2] Implement POST /api/v1/tasks (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\api\v1\tasks.py`
  - **Route:** `@router.post("/api/v1/tasks")`
  - **Logic:**
    - Extract user_id from JWT (Depends(get_current_user))
    - Validate TaskCreate schema
    - Create task with user_id
    - Return 201 Created with task
  - **Acceptance:** Tests for task creation pass

- [✅] **[T037]** [F2] Implement GET /api/v1/tasks (GREEN)
  - **Route:** `@router.get("/api/v1/tasks")`
  - **Logic:**
    - Filter by user_id and deleted_at IS NULL
    - Return list of tasks
  - **Acceptance:** Tests for listing tasks pass

- [✅] **[T038]** [F2] Implement GET /api/v1/tasks/{id} (GREEN)
  - **Route:** `@router.get("/api/v1/tasks/{id}")`
  - **Logic:**
    - Filter by id, user_id, and deleted_at IS NULL
    - Return 404 if not found or not owned
  - **Acceptance:** Tests for getting single task pass

- [✅] **[T039]** [F2] Implement PUT /api/v1/tasks/{id} (GREEN)
  - **Route:** `@router.put("/api/v1/tasks/{id}")`
  - **Logic:**
    - Update title and/or description
    - Refresh updated_at timestamp
    - Return 404 if not found or not owned
  - **Acceptance:** Tests for updating task pass

- [✅] **[T040]** [F2] Implement DELETE /api/v1/tasks/{id} (GREEN)
  - **Route:** `@router.delete("/api/v1/tasks/{id}")`
  - **Logic:**
    - Set deleted_at to current timestamp (soft delete)
    - Return 204 No Content
    - Return 404 if not found or not owned
  - **Acceptance:** Tests for deleting task pass

#### REFACTOR

- [✅] **[T041]** [F2] Refactor common query patterns
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\api\v1\tasks.py`
  - **Actions:** Extract `get_user_task()` helper function
  - **Acceptance:** Code DRY, tests still pass

### Frontend: Task UI (TDD)

#### RED - Write Failing Frontend Tests

- [ ] **[T042]** [F2] Write task UI tests (RED)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\components\tasks\TaskList.test.tsx`
  - **Test Cases:**
    - Task list renders tasks
    - Empty state shows correct message
    - Loading state shows skeleton
    - Error state shows error message
    - Create button opens modal
    - Delete confirmation works
  - **Status:** Tests should FAIL (components not implemented yet)
  - **Acceptance:** `npm test` shows failing tests

#### GREEN - Implement Task UI

- [ ] **[T043]** [F2] Create tasks page (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\app\tasks\page.tsx`
  - **Component:** Server Component fetching tasks
  - **Layout:** "Want todos" heading, Create Task button, TaskList
  - **Acceptance:** Page accessible at /tasks

- [ ] **[T044]** [F2] Create TaskList component (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskList.tsx`
  - **Features:** Display task cards, handle loading/empty/error states
  - **Acceptance:** All tests in T042 pass

- [ ] **[T045]** [F2] Create TaskCard component
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskCard.tsx`
  - **Layout:** Title, description, metadata, Edit/Delete buttons
  - **Styling:** Paper-like card with journal aesthetic
  - **Acceptance:** Task card displays all fields correctly

- [ ] **[T046]** [F2] Create Modal component
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\ui\Modal.tsx`
  - **Features:** Backdrop, close button, keyboard navigation (Escape to close)
  - **Acceptance:** Modal opens and closes correctly

- [ ] **[T047]** [F2] Create TaskForm component
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskForm.tsx`
  - **Fields:** Title (required, max 200 chars), Description (optional)
  - **Validation:** Client-side validation before submission
  - **Actions:** Call api.createTask(), close modal on success
  - **Acceptance:** Form validation works, task creates successfully

- [ ] **[T048]** [F2] Create task detail page
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\app\tasks\[id]\page.tsx`
  - **Component:** Server Component fetching single task
  - **Features:** Display full task details, Edit/Delete buttons
  - **Acceptance:** Task detail page accessible at /tasks/[id]

- [ ] **[T049]** [F2] Implement task editing
  - **Component:** TaskForm in edit mode
  - **Actions:** Pre-populate form, call api.updateTask(), refresh view
  - **Acceptance:** User can edit task successfully

- [ ] **[T050]** [F2] Implement task deletion with confirmation
  - **Component:** DeleteConfirmationModal
  - **Flow:** Show confirmation → User confirms → Call api.deleteTask() → Remove from UI
  - **Acceptance:** User can delete task with confirmation

#### REFACTOR

- [ ] **[T051]** [F2] Extract reusable UI components
  - **Paths:**
    - `src/core/frontend\components\ui\Button.tsx`
    - `src/core/frontend\components\ui\Input.tsx`
    - `src/core/frontend\components\ui\Card.tsx`
  - **Acceptance:** Components follow design system, reusable

### Integration Tests

- [ ] **[T052]** [F2] Write end-to-end task CRUD tests
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\e2e\tasks.spec.ts`
  - **Test Cases:**
    - Create task flow
    - View task details
    - Edit task flow
    - Delete task flow
    - User isolation (cannot see other user's tasks)
  - **Tool:** Playwright
  - **Acceptance:** E2E tests pass

**Phase 3 Completed:** Task CRUD fully functional

---

## Phase 4: Feature 3 - Task Completion

**Duration:** 4-5 hours
**Goal:** Implement task completion toggle with checkbox UI

### Backend: Completion Toggle (TDD)

#### RED - Write Failing Tests

- [ ] **[T053]** [F3] Write completion toggle tests (RED)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\tests\test_completion.py`
  - **Test Cases:**
    - Toggle false → true
    - Toggle true → false
    - Updated_at refreshes on toggle
    - 404 for non-existent task
    - 404 for other user's task
    - 404 for deleted task
  - **Status:** Tests should FAIL (endpoint not implemented yet)
  - **Acceptance:** `pytest src/core/backend/tests/test_completion.py` shows failing tests

#### GREEN - Implement Completion Toggle

- [ ] **[T054]** [F3] Implement PATCH /api/v1/tasks/{id}/toggle (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\api\v1\tasks.py`
  - **Route:** `@router.patch("/api/v1/tasks/{id}/toggle")`
  - **Logic:**
    - Get task by id and user_id
    - Toggle completed: `task.completed = not task.completed`
    - Refresh updated_at timestamp
    - Return updated task
  - **Acceptance:** All tests in T053 pass

- [ ] **[T055]** [F3] Add completion index to database
  - **Migration:** `D:\piaic-hackathon\hackathon2\src\core\backend\migrations\versions\002_add_completion_index.py`
  - **Index:** `CREATE INDEX idx_tasks_completed ON tasks(completed);`
  - **Acceptance:** `alembic upgrade head` adds index

#### REFACTOR

- [ ] **[T056]** [F3] Add logging for completion events
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\backend\api\v1\tasks.py`
  - **Actions:** Log task completions for analytics
  - **Acceptance:** Logs show completion events

### Frontend: Completion Checkbox (TDD)

#### RED - Write Failing Frontend Tests

- [ ] **[T057]** [F3] Write completion UI tests (RED)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\components\tasks\TaskCheckbox.test.tsx`
  - **Test Cases:**
    - Checkbox renders checked/unchecked based on completed status
    - Clicking checkbox toggles state
    - Strike-through text applies to completed tasks
    - Optimistic UI update works
    - Error state rolls back on failure
  - **Status:** Tests should FAIL (component not implemented yet)
  - **Acceptance:** `npm test` shows failing tests

#### GREEN - Implement Completion UI

- [ ] **[T058]** [F3] Create TaskCheckbox component (GREEN)
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskCheckbox.tsx`
  - **Features:**
    - Checkbox bound to task.completed
    - Click handler calls api.toggleTask()
    - Optimistic UI update (immediately update checkbox and strike-through)
    - Rollback on error
  - **Acceptance:** All tests in T057 pass

- [ ] **[T059]** [F3] Add strike-through styling for completed tasks
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskCard.tsx`
  - **Styling:** Apply `line-through` and opacity to completed task title/description
  - **Acceptance:** Completed tasks visually distinct

- [ ] **[T060]** [F3] Create TaskFilter component
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskFilter.tsx`
  - **Options:** All, Active (completed=false), Completed (completed=true)
  - **Logic:** Filter tasks client-side based on selection
  - **Acceptance:** User can filter tasks by completion status

- [ ] **[T061]** [F3] Add completion count display
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\app\tasks\page.tsx`
  - **Display:** "X of Y completed" or "X active tasks"
  - **Update:** Dynamically update on task completion
  - **Acceptance:** Count displays correctly

#### REFACTOR

- [ ] **[T062]** [F3] Add loading state to checkbox during toggle
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\components\tasks\TaskCheckbox.tsx`
  - **Actions:** Disable checkbox, show subtle spinner during API request
  - **Acceptance:** Loading state provides feedback

### Integration Tests

- [ ] **[T063]** [F3] Write end-to-end completion tests
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\e2e\completion.spec.ts`
  - **Test Cases:**
    - Toggle task completion
    - Filter by completion status
    - Verify strike-through styling
    - Verify optimistic UI
  - **Tool:** Playwright
  - **Acceptance:** E2E tests pass

**Phase 4 Completed:** Task completion fully functional

---

## Phase 5: Integration & Polish

**Duration:** 4-6 hours
**Goal:** Integration testing, UI polish, documentation, deployment prep

### Full Integration Testing

- [ ] **[T064]** Write full integration test suite
  - **Path:** `D:\piaic-hackathon\hackathon2\src\core\frontend\__tests__\e2e\integration.spec.ts`
  - **Test Cases:**
    - Complete user journey: Register → Login → Create Task → Complete Task → Logout
    - User isolation: Two users with separate task lists
    - Error handling: Network errors, expired tokens
  - **Tool:** Playwright
  - **Acceptance:** All integration tests pass

- [ ] **[T065]** Test authentication flows end-to-end
  - **Test Cases:**
    - Registration flow with validation
    - Login flow with invalid credentials
    - Token expiration handling
    - Protected route access
  - **Acceptance:** All auth flows work correctly

- [ ] **[T066]** Test task operations end-to-end
  - **Test Cases:**
    - Create task with long description
    - Edit task multiple times
    - Delete task with confirmation
    - Completion toggle persistence
    - Filter tasks by status
  - **Acceptance:** All task operations work correctly

### UI Polish

- [ ] **[T067]** [P] Apply journal theme consistently
  - **Paths:** All frontend components
  - **Actions:**
    - Verify all colors match design system
    - Verify fonts (Crimson Text, Playfair Display) applied
    - Verify spacing follows 8px grid
  - **Acceptance:** UI matches design system spec

- [ ] **[T068]** [P] Implement responsive design
  - **Actions:**
    - Test mobile layout (< 768px)
    - Test tablet layout (768px - 1024px)
    - Test desktop layout (> 1024px)
    - Collapsible sidebar on mobile
  - **Acceptance:** UI works on all screen sizes

- [ ] **[T069]** [P] Add loading skeletons
  - **Paths:**
    - Task list skeleton
    - Task detail skeleton
  - **Acceptance:** Loading states provide good UX

- [ ] **[T070]** [P] Improve error messages
  - **Actions:**
    - Review all error messages for clarity
    - Add retry buttons where appropriate
    - Add error illustrations/icons
  - **Acceptance:** Error messages are user-friendly

- [ ] **[T071]** [P] Add success feedback
  - **Actions:**
    - Toast notifications for task creation/update/delete
    - Brief success animations
  - **Acceptance:** User receives feedback on actions

### Accessibility Audit

- [ ] **[T072]** [P] Audit keyboard navigation
  - **Actions:**
    - Tab through all interactive elements
    - Verify Enter/Space trigger actions
    - Verify Escape closes modals
  - **Acceptance:** All features keyboard-accessible

- [ ] **[T073]** [P] Audit screen reader support
  - **Actions:**
    - Add ARIA labels where missing
    - Test with screen reader
    - Verify error messages announced
  - **Acceptance:** Screen reader users can use app

- [ ] **[T074]** [P] Audit color contrast
  - **Actions:**
    - Check all text meets WCAG AA contrast ratio
    - Adjust colors if needed
  - **Acceptance:** All text readable

### Documentation

- [ ] **[T075]** [P] Write README.md
  - **Path:** `D:\piaic-hackathon\hackathon2\README.md`
  - **Sections:**
    - Project overview
    - Setup instructions
    - Running locally
    - Running tests
    - Deployment guide
  - **Acceptance:** README complete and accurate

- [ ] **[T076]** [P] Write CONTRIBUTING.md
  - **Path:** `D:\piaic-hackathon\hackathon2\CONTRIBUTING.md`
  - **Sections:**
    - Development workflow
    - Code standards
    - Testing requirements
    - PR guidelines
  - **Acceptance:** Contributors can follow guide

- [ ] **[T077]** [P] Document API endpoints
  - **Path:** `D:\piaic-hackathon\hackathon2\docs\API.md`
  - **Content:** All endpoints with request/response examples
  - **Acceptance:** API fully documented

### Deployment Preparation

- [ ] **[T078]** Setup production environment variables
  - **Actions:**
    - Create production `.env` file template
    - Document all required variables
    - Generate production JWT secret
  - **Acceptance:** Production config ready

- [ ] **[T079]** [P] Configure production database
  - **Actions:**
    - Create production Neon database
    - Run migrations
    - Verify connection
  - **Acceptance:** Production database ready

- [ ] **[T080]** [P] Setup CI/CD pipeline
  - **Path:** `.github/workflows/ci.yml`
  - **Actions:**
    - Run linters on push
    - Run tests on pull request
    - Build frontend and backend
  - **Acceptance:** CI/CD pipeline works

- [ ] **[T081]** Deploy backend to Vercel/Railway
  - **Actions:**
    - Configure deployment settings
    - Set environment variables
    - Deploy and verify health check
  - **Acceptance:** Backend deployed and accessible

- [ ] **[T082]** Deploy frontend to Vercel
  - **Actions:**
    - Configure deployment settings
    - Set NEXT_PUBLIC_API_URL to production backend
    - Deploy and verify
  - **Acceptance:** Frontend deployed and accessible

### Final Validation

- [ ] **[T083]** Run full test suite
  - **Commands:**
    - Backend: `pytest src/core/backend/tests/`
    - Frontend: `npm test`
    - E2E: `npm run test:e2e`
  - **Acceptance:** All tests pass

- [ ] **[T084]** Manual QA on deployed application
  - **Test Cases:**
    - Register new user
    - Create 5 tasks
    - Complete 2 tasks
    - Delete 1 task
    - Filter by status
    - Logout and login again
  - **Acceptance:** All features work in production

- [ ] **[T085]** Performance audit
  - **Actions:**
    - Run Lighthouse audit
    - Check page load times
    - Verify API response times
  - **Acceptance:** Performance meets targets (< 3s load, < 500ms API)

**Phase 5 Completed:** Application production-ready

---

## Task Summary

### Total Task Count: 91 tasks

**By Phase:**
- Phase 0 (Project Setup): 6 tasks
- Phase 1 (Foundational Infrastructure): 10 tasks
- Phase 2 (Feature 1 - User Authentication): 22 tasks (was 16, added 6 JWT tasks: T026A-D, T030A, T032A)
- Phase 3 (Feature 2 - Task CRUD): 20 tasks
- Phase 4 (Feature 3 - Task Completion): 11 tasks
- Phase 5 (Integration & Polish): 22 tasks

**By Type:**
- Setup/Config: 16 tasks
- Backend Implementation: 21 tasks
- Frontend Implementation: 28 tasks
- Testing: 15 tasks
- Documentation: 3 tasks
- Deployment: 2 tasks

**Estimated Duration:**
- Phase 0: 2-3 hours
- Phase 1: 3-4 hours
- Phase 2: 6-8 hours
- Phase 3: 8-10 hours
- Phase 4: 4-5 hours
- Phase 5: 4-6 hours

**Total Estimated Time: 27-36 hours**

### Parallel Execution Opportunities

Tasks marked `[P]` can be executed in parallel within their phase:
- Phase 0: T001, T002, T003, T005 (4 tasks)
- Phase 1: T010, T011, T016 (3 tasks)
- Phase 5: T067-T074, T075-T077, T079-T080 (15 tasks)

**Potential Time Savings with Parallel Execution: 5-8 hours**

### Critical Path

The critical path (longest sequence of dependent tasks):
1. Phase 0 → Phase 1 → Phase 2 (Auth Backend) → Phase 2 (Auth Frontend) → Phase 3 (CRUD Backend) → Phase 3 (CRUD Frontend) → Phase 4 → Phase 5

**Critical Path Duration: ~24 hours minimum**

---

## Implementation Notes

### Best Practices

1. **Always run tests before moving to next task**
   - Ensures no regressions
   - Validates implementation correctness

2. **Commit after each completed task**
   - Small, atomic commits
   - Clear commit messages referencing task ID

3. **Follow TDD workflow strictly**
   - RED: Write failing test
   - GREEN: Implement to pass test
   - REFACTOR: Optimize code

4. **Maintain user isolation in all queries**
   - Every backend query MUST filter by user_id
   - Security vulnerability if missed

5. **Use centralized API client**
   - NO direct fetch() calls in components
   - All API calls through lib/api.ts

### Common Pitfalls to Avoid

❌ **Don't skip tests** - TDD is non-negotiable
❌ **Don't hardcode user_id** - Always extract from JWT
❌ **Don't use user_id in URLs** - Security risk
❌ **Don't forget soft deletes** - Always check deleted_at IS NULL
❌ **Don't commit secrets** - Use .env files, never commit .env

### Getting Help

If blocked on a task:
1. Review the feature spec (01, 02, or 03)
2. Review architecture docs (00-backend-architecture.md, 08-frontend-design-flow.md)
3. Check existing code examples in completed tasks
4. Ask for clarification with specific task ID

---

**Document Status:** Ready for Implementation
**Next Action:** Begin Phase 0 - Project Setup
**Start with:** T001 - Create monorepo directory structure
