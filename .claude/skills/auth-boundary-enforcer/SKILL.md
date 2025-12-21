---
name: auth-boundary-enforcer
description: Enforce authentication architecture rules from ADR-004, ensuring JWT-based auth, user_id from token only, database query filtering, and proper user isolation. Use when (1) implementing any API endpoint, (2) handling user-specific data, (3) reviewing authentication flow, or (4) before any code that accesses user data.
license: Complete terms in LICENSE.txt
---

# Auth Boundary Enforcer

Enforce authentication and authorization architecture rules to ensure proper user isolation and security following ADR-004 patterns.

## Workflow

Follow these steps when enforcing auth boundaries:

1. **Verify JWT authentication**
   - Check Authorization header extraction
   - Validate JWT token signature
   - Ensure token is not expired
   - Extract user_id from token claims

2. **Ensure user_id from JWT only**
   - NO user_id in URL path parameters
   - NO user_id in request body
   - NO user_id in query parameters
   - user_id ONLY from validated JWT token

3. **Check database query filtering**
   - Every user-scoped query filters by user_id
   - Soft delete filter (deleted_at IS NULL) applied
   - No cross-user data access possible
   - Aggregations scoped to user_id

4. **Validate backend has NO users table**
   - Authentication is frontend concern (Better Auth)
   - Backend validates JWT, extracts user_id
   - No user profile storage in backend database
   - User identity managed by Better Auth

5. **Enforce user isolation on every operation**
   - Create: Add user_id from token
   - Read: Filter by user_id from token
   - Update: Verify user_id matches token
   - Delete: Soft delete with user_id check

## Output Format

Present authentication boundary checks using this structure:

```
🔐 Auth Boundary Check: [endpoint/component]

Endpoint: POST /api/v1/tasks
Source: backend/routers/tasks.py:45

Rules Verified:
✅ JWT extracted from Authorization header
✅ user_id from token (not URL/body)
✅ Database query filtered by user_id
✅ Soft delete filter applied
✅ No cross-user data access

OR

❌ Violations Detected:
- Line 23: user_id passed in URL path /api/v1/users/{user_id}/tasks
  Fix: Remove user_id from URL, extract from JWT with get_current_user()
  ADR-004 Rule: User ID must come from JWT token, not URL

- Line 45: Query not filtered by user_id
  Fix: Add .where(Task.user_id == user_id) to query
  ADR-004 Rule: All queries must filter by authenticated user_id

- Line 67: Hard delete used instead of soft delete
  Fix: Set deleted_at = datetime.utcnow() instead of session.delete()
  ADR-004 Rule: Use soft deletes for user data
```

## Required Authentication Flow

Enforce this exact architecture from ADR-004:

```
┌─────────────────────────────────────────┐
│ Frontend (Next.js)                      │
├─────────────────────────────────────────┤
│ Better Auth                             │
│  ├─ Manages user identity              │
│  ├─ Issues JWT tokens on login         │
│  └─ Stores JWT in HTTP-only cookie     │
└────────────────┬────────────────────────┘
                 │
                 │ Authorization: Bearer <JWT>
                 ↓
┌─────────────────────────────────────────┐
│ Backend (FastAPI)                       │
├─────────────────────────────────────────┤
│ JWT Validation                          │
│  ├─ Validates JWT signature            │
│  ├─ Extracts user_id from token        │
│  ├─ Filters all queries by user_id     │
│  └─ NO users table                     │
└─────────────────────────────────────────┘
```

## ADR-004 Authentication Rules

**Rule 1: Frontend issues JWT, backend validates JWT**
- Better Auth in Next.js manages authentication
- Backend receives and validates JWT tokens
- Backend trusts JWT signature (shared secret)

**Rule 2: NO user_id in URL paths or body**
- ❌ BAD: `GET /api/v1/users/{user_id}/tasks`
- ✅ GOOD: `GET /api/v1/tasks` (user_id from JWT)
- ❌ BAD: `POST /api/v1/tasks {"user_id": "123", "title": "..."}`
- ✅ GOOD: `POST /api/v1/tasks {"title": "..."}` (user_id from JWT)

**Rule 3: Every database query filtered by user_id**
- ❌ BAD: `SELECT * FROM tasks`
- ✅ GOOD: `SELECT * FROM tasks WHERE user_id = ? AND deleted_at IS NULL`
- Apply to ALL operations: SELECT, UPDATE, DELETE

**Rule 4: User isolation enforced on every operation**
- Users can only access their own data
- No cross-user reads or writes
- No aggregations across users
- No admin bypass (except explicit admin endpoints)

**Rule 5: Backend is stateless and trusts JWT**
- No session storage in backend
- No user lookup before query
- Trust JWT claims after signature validation
- user_id is authoritative identifier

## Anti-Patterns to Flag

**❌ User ID in URL:**
```python
@router.get("/users/{user_id}/tasks")  # WRONG
async def get_tasks(user_id: str):
    # Allows accessing any user's data!
```

**✅ Correct Pattern:**
```python
@router.get("/tasks")
async def get_tasks(user_id: str = Depends(get_current_user)):
    # user_id from JWT, can't be spoofed
```

**❌ User ID in Request Body:**
```python
class TaskCreate(BaseModel):
    user_id: str  # WRONG - client can spoof this
    title: str
```

**✅ Correct Pattern:**
```python
class TaskCreate(BaseModel):
    title: str  # user_id added server-side from JWT

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user)
):
    task = Task(**task_data.dict(), user_id=user_id)  # Add user_id from JWT
```

**❌ Unfiltered Query:**
```python
statement = select(Task)  # WRONG - returns all users' tasks
```

**✅ Correct Pattern:**
```python
statement = select(Task).where(
    Task.user_id == user_id,  # Filter by authenticated user
    Task.deleted_at == None   # Filter soft-deleted
)
```

**❌ Hard Delete:**
```python
session.delete(task)  # WRONG - permanent deletion
```

**✅ Correct Pattern:**
```python
task.deleted_at = datetime.utcnow()  # Soft delete
session.add(task)
```

**❌ Users Table in Backend:**
```python
class User(SQLModel, table=True):  # WRONG - auth is frontend concern
    id: str
    email: str
    password_hash: str
```

**✅ Correct Pattern:**
```python
# NO User model in backend!
# Better Auth handles user management
# Backend only uses user_id from JWT
```

## Dependency Injection Pattern

**Required dependencies for all protected endpoints:**

```python
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract and validate user_id from JWT token

    Returns:
        user_id (str): User ID from validated JWT token

    Raises:
        HTTPException 401: Invalid or expired token
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# Usage in all protected routes:
@router.get("/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),  # Required!
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    # ... rest of implementation
```

## Key Rules

- **JWT is the single source of user identity** - No other source of user_id accepted
- **User ID never in URL or body** - Always from validated JWT token
- **Filter every query by user_id** - No exceptions for user-scoped data
- **Soft deletes required** - Never hard delete user data
- **Backend has NO users table** - Authentication is frontend concern (Better Auth)
- **User isolation is mandatory** - No cross-user data access
- **Stateless backend** - Trust JWT claims after signature validation
- **get_current_user() on all protected routes** - Use FastAPI dependency injection
