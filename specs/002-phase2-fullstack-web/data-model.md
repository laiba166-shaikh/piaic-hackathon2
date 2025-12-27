# Data Model: User Authentication

**Feature:** User Authentication
**Date:** 2025-12-21
**Status:** Design Complete
**Input:** Feature spec (01-user-authentication.md) and research (research.md)

## Summary

This data model documents the user identification architecture for Phase 2. **The backend does NOT have a users table** - Better Auth manages user accounts entirely on the frontend. The backend database only stores a `user_id` field in the tasks table as an opaque string identifier extracted from JWT tokens. This architecture provides clear separation of concerns: frontend handles authentication and user management, backend enforces user isolation and data ownership.

---

## Architecture Overview

### Two-Database Architecture

```
┌─────────────────────────────────────┐
│         Frontend Database           │
│      (Better Auth Managed)          │
├─────────────────────────────────────┤
│  Tables:                            │
│  - user (id, email, emailVerified)  │
│  - password (hash, userId)          │
│  - session (id, expiresAt, userId)  │
│  - account (OAuth providers)        │
│  - verification (email tokens)      │
└─────────────────────────────────────┘
                ↓
         Issues JWT Token
         (contains user_id in 'sub' claim)
                ↓
┌─────────────────────────────────────┐
│         Backend Database            │
│      (Task Management)              │
├─────────────────────────────────────┤
│  Tables:                            │
│  - tasks (id, user_id, title, ...)  │
│                                     │
│  NO users table!                    │
│  Backend trusts JWT user_id         │
└─────────────────────────────────────┘
```

**Key Principle:** Backend database has NO users table. Backend trusts the `user_id` claim from JWT tokens issued by Better Auth (frontend).

---

## Backend Data Model

### Table: NONE (No Users Table)

**Important:** The backend does NOT store user account information. No users table exists in the backend database.

**Why No Users Table:**
1. **Separation of Concerns:** Frontend (Better Auth) manages user accounts, backend manages task data
2. **Simplicity:** Backend doesn't need user CRUD operations, password hashing, email verification
3. **Stateless Architecture:** Backend validates JWT tokens (stateless), doesn't query user records
4. **Trust Model:** Backend trusts JWT tokens issued by frontend (single issuer)

---

## User Identifier in Backend Tables

### Field Specification: `user_id`

**Purpose:** Identify the owner of a task (or any other resource) using the user's ID from the JWT token.

**Field Definition:**
```python
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)  # From JWT 'sub' claim
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False)
    # ... other fields
```

**SQL Schema:**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,  -- Opaque string from JWT
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for user isolation queries (CRITICAL for performance)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at);
```

**Field Properties:**
- **Type:** String (VARCHAR 255)
- **Source:** JWT token 'sub' claim (issued by Better Auth)
- **Format:** UUID format (e.g., "550e8400-e29b-41d4-a716-446655440000")
- **Nullable:** NO (every task must have an owner)
- **Indexed:** YES (frequently queried for user isolation)
- **Foreign Key:** NO (no users table to reference)
- **Validation:** Must be non-empty string (validated by JWT dependency)
- **Default:** N/A (must be provided from JWT token)

**Usage Pattern:**
```python
# Every query MUST filter by user_id
from sqlmodel import Session, select
from src.core.backend.dependencies import get_current_user

@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),  # Extracted from JWT
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.user_id == user_id,  # User isolation
        Task.deleted_at == None    # Exclude soft-deleted
    )
    tasks = session.exec(statement).all()
    return tasks
```

**Critical Rule:** ALL database queries involving user-owned resources (tasks, tags, etc.) MUST include `WHERE user_id = <authenticated_user_id>` to enforce user isolation. This prevents users from accessing or modifying other users' data.

---

## Frontend Data Model (Better Auth Managed)

### Table: `user`

**Managed By:** Better Auth (Drizzle ORM migrations)

**Schema:**
```sql
CREATE TABLE "user" (
    "id" TEXT PRIMARY KEY,                    -- UUID generated by Better Auth
    "email" TEXT NOT NULL UNIQUE,             -- User's email address
    "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
    "name" TEXT,                               -- Optional display name
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX "idx_user_email" ON "user"("email");
```

**Fields:**
- **id:** Unique identifier (UUID), used as 'sub' claim in JWT tokens
- **email:** User's email address (unique, used for login)
- **emailVerified:** Whether email has been verified (Phase 3+ feature)
- **name:** Optional display name
- **createdAt:** Account creation timestamp
- **updatedAt:** Last update timestamp

**Relationships:**
- **One-to-Many with `password`:** Each user has one hashed password
- **One-to-Many with `session`:** User can have multiple active sessions
- **One-to-Many with `account`:** OAuth accounts (Phase 3+ feature)

---

### Table: `password`

**Managed By:** Better Auth

**Schema:**
```sql
CREATE TABLE "password" (
    "hash" TEXT NOT NULL,                     -- bcrypt hashed password
    "userId" TEXT NOT NULL PRIMARY KEY REFERENCES "user"("id") ON DELETE CASCADE
);
```

**Fields:**
- **hash:** bcrypt hash of user's password (never store plaintext)
- **userId:** Foreign key to user table (cascade delete on user deletion)

**Security:** Better Auth automatically hashes passwords with bcrypt (work factor 10+).

---

### Table: `session`

**Managed By:** Better Auth

**Schema:**
```sql
CREATE TABLE "session" (
    "id" TEXT PRIMARY KEY,                    -- Session UUID
    "expiresAt" TIMESTAMP NOT NULL,           -- Session expiration (24 hours)
    "ipAddress" TEXT,                         -- Client IP (optional)
    "userAgent" TEXT,                         -- Browser user agent (optional)
    "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX "idx_session_userId" ON "session"("userId");
CREATE INDEX "idx_session_expiresAt" ON "session"("expiresAt");
```

**Fields:**
- **id:** Unique session identifier
- **expiresAt:** When session expires (24 hours from creation)
- **ipAddress:** Client IP address (for security audit)
- **userAgent:** Browser user agent (for security audit)
- **userId:** Foreign key to user (which user owns this session)
- **createdAt:** Session creation timestamp

**Lifecycle:**
- **Created:** On login (signIn())
- **Validated:** On each request (getSession())
- **Expired:** After 24 hours or on logout (signOut())

---

### Table: `account` (Phase 3+ OAuth)

**Managed By:** Better Auth

**Schema:**
```sql
CREATE TABLE "account" (
    "id" TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
    "accountId" TEXT NOT NULL,                -- Provider-specific user ID
    "providerId" TEXT NOT NULL,               -- "google", "github", etc.
    "accessToken" TEXT,                       -- OAuth access token (encrypted)
    "refreshToken" TEXT,                      -- OAuth refresh token (encrypted)
    "expiresAt" TIMESTAMP,                    -- Token expiration
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX "idx_account_userId" ON "account"("userId");
```

**Note:** OAuth providers (Google, GitHub) are deferred to Phase 3+. This table is created by Better Auth but unused in Phase 2.

---

### Table: `verification` (Phase 3+ Email Verification)

**Managed By:** Better Auth

**Schema:**
```sql
CREATE TABLE "verification" (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT NOT NULL,               -- Email address
    "value" TEXT NOT NULL,                    -- Verification token
    "expiresAt" TIMESTAMP NOT NULL,           -- Token expiration
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX "idx_verification_identifier" ON "verification"("identifier");
```

**Note:** Email verification is deferred to Phase 3+. This table is created by Better Auth but unused in Phase 2.

---

## Data Relationships

### Frontend (Better Auth Database)

```
user (1) ──────< (N) password
  │
  └────────< (N) session
  │
  └────────< (N) account (OAuth, Phase 3+)
```

### Backend (Task Management Database)

```
NO RELATIONSHIPS

tasks.user_id is an opaque string (no foreign key to user table)
```

### Cross-Database Relationship (Conceptual Only)

```
Frontend: user.id ──→ JWT Token 'sub' claim ──→ Backend: tasks.user_id
           (UUID)                                          (string)
```

**Important:** This is NOT a database foreign key. It's a logical relationship enforced by the application layer (JWT tokens).

---

## Entity Lifecycle

### User (Frontend - Better Auth)

```
┌─────────────┐
│ Registration│
│ (signUp)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ User Created│
│ in Frontend │
│ DB          │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Password    │
│ Hashed &    │
│ Stored      │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ JWT Token   │
│ Issued      │
│ (user_id in │
│  'sub')     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Cookie Set  │
│ in Browser  │
└─────────────┘
```

### Task (Backend)

```
┌─────────────┐
│ Client      │
│ Sends       │
│ Request     │
│ with JWT    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Backend     │
│ Validates   │
│ JWT         │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Extract     │
│ user_id     │
│ from 'sub'  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Create Task │
│ with        │
│ user_id     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Return Task │
│ to Client   │
└─────────────┘
```

---

## Validation Rules

### Frontend (Better Auth)

**Email Validation:**
- Format: Valid email format (RFC 5321)
- Max Length: 254 characters
- Uniqueness: Must be unique in `user` table
- Required: Cannot be null or empty

**Password Validation:**
- Min Length: 8 characters
- Max Length: 128 characters (practical limit)
- Required: Cannot be null or empty
- Hashing: bcrypt with work factor 10+

**Session Validation:**
- Expiration: 24 hours from creation
- Cleanup: Expired sessions removed by Better Auth cron job

### Backend (FastAPI)

**user_id Validation:**
- Source: Must come from JWT 'sub' claim (enforced by `get_current_user` dependency)
- Type: String (UUID format)
- Required: Cannot be null or empty
- Validation: No database check (trusts JWT issuer)

**Example Validation Code:**
```python
# src/core/backend/dependencies.py
import jwt
from fastapi import HTTPException

async def get_current_user(token: str) -> str:
    """Validate JWT and extract user_id."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id: str = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## State Transitions

### User Account States (Frontend)

```
┌──────────────┐
│  Not Exists  │
└──────┬───────┘
       │ signUp()
       ↓
┌──────────────┐
│   Active     │ ←──── Login (signIn())
│ (email +     │
│  password)   │
└──────┬───────┘
       │ signOut()
       ↓
┌──────────────┐
│  Logged Out  │
│ (session     │
│  cleared)    │
└──────┬───────┘
       │ signIn()
       ↓
    (back to Active)

Note: Account deletion is Phase 3+ feature
```

### Task Ownership (Backend)

```
┌──────────────┐
│  No Tasks    │
└──────┬───────┘
       │ POST /api/v1/tasks (with JWT)
       ↓
┌──────────────┐
│  Task        │
│  Created     │
│  with        │
│  user_id     │
└──────┬───────┘
       │ DELETE /api/v1/tasks/{id}
       ↓
┌──────────────┐
│ Soft Deleted │
│ (deleted_at  │
│  timestamp)  │
└──────────────┘

Note: Tasks are never transferred between users
      (user_id is immutable after creation)
```

---

## Migration Strategy

### Frontend Database (Better Auth)

**Initial Setup:**
```bash
# Better Auth creates tables automatically on first run
# No manual migrations needed for Phase 2

# Install Better Auth dependencies
npm install better-auth drizzle-orm postgres

# Configure database connection
# src/core/frontend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/frontend_auth

# Better Auth will auto-create tables on app start
npm run dev
```

**Schema Creation:** Better Auth creates all tables automatically (user, password, session, account, verification).

**No Manual Migrations Needed:** Better Auth handles schema versioning internally.

### Backend Database (Task Management)

**Initial Setup:**
```bash
# Backend database does NOT have users table
# Only tasks table with user_id field

# Install Alembic for migrations
pip install alembic sqlmodel

# Initialize Alembic
alembic init migrations

# Create initial migration (tasks table)
alembic revision --autogenerate -m "Initial schema: tasks table"

# Run migration
alembic upgrade head
```

**Migration File Example:**
```python
# src/core/backend/migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Indexes for performance
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_deleted_at', 'tasks', ['deleted_at'])

def downgrade():
    op.drop_table('tasks')
```

**Important:** Backend migrations do NOT include a users table. The user_id field is just a string (no foreign key).

---

## Performance Considerations

### Indexing Strategy

**Frontend (Better Auth manages):**
- `user.email` - Indexed for login lookups (UNIQUE constraint)
- `session.userId` - Indexed for session validation
- `session.expiresAt` - Indexed for cleanup queries
- `password.userId` - Primary key (automatic index)

**Backend:**
- `tasks.user_id` - **CRITICAL INDEX** for user isolation queries (all queries filter by user_id)
- `tasks.deleted_at` - Indexed for soft delete filtering (exclude deleted tasks)

**Query Performance:**
```sql
-- Fast (uses idx_tasks_user_id)
SELECT * FROM tasks WHERE user_id = 'user-123' AND deleted_at IS NULL;

-- Slow without index (full table scan)
SELECT * FROM tasks WHERE title = 'Buy milk';  -- Needs full-text search index (Phase 3+)
```

### Query Patterns

**All User Queries Use Index:**
```python
# Every query filters by user_id (uses index)
select(Task).where(
    Task.user_id == user_id,      # Indexed
    Task.deleted_at == None        # Indexed (partial index)
)
```

**No Cross-User Queries:**
Backend NEVER queries tasks across multiple users (violates user isolation).

---

## Security Considerations

### No Users Table in Backend = Simplified Security Model

**Benefits:**
1. **No Password Storage:** Backend doesn't handle passwords (no hashing, no breaches)
2. **No User CRUD:** Backend doesn't need to validate email uniqueness, handle registration, etc.
3. **Stateless Validation:** Backend only validates JWT signatures (fast, scalable)
4. **Trust Boundary:** Clear separation - frontend manages users, backend validates tokens

**Security Rules:**
1. **Trust JWT Tokens:** Backend trusts user_id from JWT (assumes frontend issued valid tokens)
2. **Validate Signatures:** Backend MUST validate JWT signatures (prevents forged tokens)
3. **Check Expiration:** Backend MUST reject expired tokens (prevents replay attacks)
4. **Filter All Queries:** Backend MUST filter all queries by user_id (prevents cross-user access)

### Data Isolation

**Enforcement:**
- **Application Layer:** `get_current_user()` dependency extracts user_id from JWT
- **Database Layer:** All queries filter by `WHERE user_id = <authenticated_user>`
- **No Foreign Key:** user_id is opaque string (no database-level validation)

**Example:**
```python
# User A (user_id = "user-a") tries to access User B's task

@router.get("/api/v1/tasks/{task_id}")
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),  # Extracts "user-a" from JWT
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,  # Filters to User A's tasks only
        Task.deleted_at == None
    )
    task = session.exec(statement).first()

    if not task:
        # Returns 404 even if task exists for User B (information hiding)
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

**Result:** User A cannot access User B's tasks (404 error even if task exists).

---

## Testing Data Model

### Frontend (Better Auth)

**Test Data:**
```typescript
// src/core/frontend/tests/fixtures/users.ts
export const testUsers = {
  user1: {
    email: "user1@example.com",
    password: "password123",
    expectedUserId: "generated-by-better-auth", // UUID
  },
  user2: {
    email: "user2@example.com",
    password: "password456",
    expectedUserId: "generated-by-better-auth", // UUID
  },
};
```

**Setup:**
```typescript
// Create test users in Better Auth database before tests
await signUp({ email: testUsers.user1.email, password: testUsers.user1.password });
```

### Backend (Tasks)

**Test Data:**
```python
# src/core/backend/tests/fixtures/tasks.py
from src.core.backend.models import Task

def create_test_task(session, user_id: str = "test-user-123") -> Task:
    """Create a test task with given user_id."""
    task = Task(
        user_id=user_id,
        title="Test Task",
        description="Test Description",
        completed=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

**Isolation Test:**
```python
# src/core/backend/tests/test_user_isolation.py
def test_user_cannot_access_other_users_tasks(session):
    """User A cannot access User B's tasks."""
    # Create tasks for two users
    task_a = create_test_task(session, user_id="user-a")
    task_b = create_test_task(session, user_id="user-b")

    # Query as User A
    statement = select(Task).where(
        Task.user_id == "user-a",
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()

    # Should only see User A's task
    assert len(tasks) == 1
    assert tasks[0].id == task_a.id
    assert task_b not in tasks
```

---

## Summary

**Data Model Characteristics:**
- **Backend:** NO users table, only user_id field in tasks table (opaque string)
- **Frontend:** Full user management (Better Auth creates user, password, session, account, verification tables)
- **Separation:** Frontend manages users, backend enforces user isolation
- **Security:** JWT tokens bridge frontend and backend, backend trusts frontend issuer
- **Performance:** user_id indexed for fast user isolation queries
- **Simplicity:** Backend doesn't need user CRUD, password hashing, email verification

**Next Steps:**
1. Generate API contracts (jwt-validation.md, better-auth-flow.md)
2. Generate quickstart.md (developer setup guide)
3. Generate tasks.md (TDD implementation tasks)

Data model design is complete and aligns with Phase 2 architecture.
