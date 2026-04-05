# Backend Architecture - Phase 2

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-12-21
**Type:** Architecture Reference Document

---

## Table of Contents

1. [Overview](#overview)
2. [API Contract Standards](#api-contract-standards)
3. [Data Ownership Rules](#data-ownership-rules)
4. [Validation Rules](#validation-rules)
5. [Error Behavior](#error-behavior)
6. [Phase 2 Required Patterns](#phase-2-required-patterns)
7. [Security & Authentication](#security--authentication)
8. [Database Patterns](#database-patterns)
9. [Testing Standards](#testing-standards)
10. [Code Examples](#code-examples)

---

## Overview

This document defines the **architectural patterns and standards** that ALL Phase 2 backend features must follow. It serves as the authoritative reference for backend implementation across all feature specifications.

**Purpose:**
- Establish consistent API design patterns
- Enforce data ownership and user isolation
- Standardize validation and error handling
- Document Phase 2 required technical patterns
- Provide reusable code templates

**Scope:**
- Applies to ALL backend features in Phase 2
- Referenced by individual feature specs (01-07)
- Enforced by API Developer Agent during implementation
- Validated by Quality Guardian Agent

---

## API Contract Standards

### URL Structure

**Pattern:** `/api/v{version}/{resource}`

```
✅ CORRECT
GET    /api/v1/tasks
POST   /api/v1/tasks
GET    /api/v1/tasks/{id}
PUT    /api/v1/tasks/{id}
DELETE /api/v1/tasks/{id}
PATCH  /api/v1/tasks/{id}/toggle

❌ WRONG
GET /tasks                    # Missing /api/v1/
GET /api/tasks                # Missing version
GET /api/v1/users/{user_id}/tasks  # user_id in URL (security risk)
```

**Rules:**
1. All endpoints start with `/api/v1/`
2. Use RESTful resource naming (plural nouns: `tasks`, not `task`)
3. Never include `user_id` in URL paths (extract from JWT)
4. Use HTTP verbs correctly (GET, POST, PUT, PATCH, DELETE)

---

### HTTP Methods and Status Codes

| Method | Use Case | Success Status | Response Body |
|--------|----------|----------------|---------------|
| **GET** | Retrieve resource(s) | 200 OK | Resource(s) data |
| **POST** | Create new resource | 201 Created | Created resource |
| **PUT** | Update entire resource | 200 OK | Updated resource |
| **PATCH** | Partial update | 200 OK | Updated resource |
| **DELETE** | Remove resource | 204 No Content | Empty |

**Status Code Usage:**

| Code | Meaning | When to Use |
|------|---------|-------------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST (resource created) |
| **204** | No Content | Successful DELETE (no response body) |
| **400** | Bad Request | Invalid request format, missing required fields |
| **401** | Unauthorized | Missing, invalid, or expired JWT token |
| **403** | Forbidden | Valid auth but insufficient permissions (rarely used in Phase 2) |
| **404** | Not Found | Resource doesn't exist OR belongs to different user |
| **422** | Unprocessable Entity | Pydantic validation errors |
| **500** | Internal Server Error | Database errors, unexpected exceptions |

**Important:** Return **404** (not 403) when user tries to access another user's resource. This prevents information leakage about resource existence.

---

### Request Headers

**Required Headers (All Requests):**

```http
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Optional Headers:**

```http
Accept: application/json
X-Request-ID: {unique-request-id}  # For request tracing
```

---

### Response Headers

**Standard Response Headers (All Responses):**

```http
Content-Type: application/json
X-Request-ID: {unique-request-id}  # Echo back request ID if provided
```

---

### Request/Response Format

**Request Body (JSON):**

```json
{
  "field_name": "value",
  "nested_object": {
    "key": "value"
  },
  "array_field": ["item1", "item2"]
}
```

**Success Response (JSON):**

```json
{
  "id": 123,
  "user_id": "user-uuid",
  "field_name": "value",
  "created_at": "2025-12-21T10:30:00Z",
  "updated_at": "2025-12-21T10:30:00Z"
}
```

**Rules:**
- Use `snake_case` for field names (Python convention)
- ISO 8601 format for timestamps: `YYYY-MM-DDTHH:MM:SSZ`
- Include `user_id` in response (for frontend validation)
- Always include `created_at` and `updated_at`

---

## Data Ownership Rules

### Rule 1: User Isolation

**Every database query MUST filter by `user_id`**

```python
# ✅ CORRECT - Filter by user_id from JWT
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.user_id == user_id,  # Required!
        Task.deleted_at == None
    )
    return session.exec(statement).all()

# ❌ WRONG - Missing user_id filter
statement = select(Task).where(Task.deleted_at == None)
# This returns ALL users' tasks - SECURITY VULNERABILITY!
```

### Rule 2: user_id Source

**Always extract `user_id` from JWT token, NEVER from request**

```python
# ✅ CORRECT - user_id from JWT dependency
@router.post("/api/v1/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),  # From JWT
    session: Session = Depends(get_db)
):
    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    session.commit()
    return task

# ❌ WRONG - user_id from request body
@router.post("/api/v1/tasks")
async def create_task(task_data: TaskCreate):
    # If TaskCreate includes user_id field, users can forge it!
    task = Task(**task_data.model_dump())  # SECURITY RISK!
```

### Rule 3: No user_id in URL Paths

**Never include user_id in URL paths**

```python
# ❌ WRONG - user_id in URL
@router.get("/api/v1/users/{user_id}/tasks")
# Problems:
# 1. User can change user_id in URL to access other users' data
# 2. Redundant (JWT already contains user_id)
# 3. URL exposes user_id unnecessarily

# ✅ CORRECT - No user_id in URL
@router.get("/api/v1/tasks")
async def get_tasks(user_id: str = Depends(get_current_user)):
    # user_id from JWT, not URL
```

### Rule 4: Cross-User Access Prevention

**Return 404 (not 403) when user tries to access another user's resource**

```python
# ✅ CORRECT - Return 404 for unauthorized access
@router.get("/api/v1/tasks/{task_id}")
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,  # Ensures ownership
        Task.deleted_at == None
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        # Don't reveal if task exists but belongs to another user

    return task

# ❌ WRONG - Return 403 when user doesn't own task
# This reveals that task exists, just not owned by requester
if task.user_id != user_id:
    raise HTTPException(status_code=403, detail="Forbidden")
```

---

## Validation Rules

### Input Validation (Pydantic)

**Use Pydantic schemas for request validation**

```python
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10000)

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

# FastAPI automatically validates request body against schema
@router.post("/api/v1/tasks")
async def create_task(task_data: TaskCreate):
    # If validation fails, FastAPI returns 422 automatically
    ...
```

### Validation Error Response (422)

**FastAPI automatically returns this format for Pydantic validation errors:**

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

### Common Validation Rules

| Field Type | Validation Rules |
|------------|------------------|
| **String (required)** | `Field(..., min_length=1, max_length=N)` |
| **String (optional)** | `Field(None, max_length=N)` |
| **Integer (range)** | `Field(..., ge=1, le=5)` (greater/equal, less/equal) |
| **Email** | Use `EmailStr` from pydantic |
| **URL** | Use `HttpUrl` from pydantic |
| **Datetime** | Use `datetime` with ISO 8601 format |
| **Enum** | Use Python `Enum` class |

### Custom Validators

```python
from pydantic import field_validator

class TaskCreate(BaseModel):
    title: str
    priority: int | None = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError('Priority must be between 1 and 5')
        return v
```

---

## Error Behavior

### Standard Error Response Format

**All errors return this JSON structure:**

```json
{
  "detail": "Human-readable error message"
}
```

**For validation errors (422), FastAPI returns:**

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

### Error Messages

**Use clear, actionable error messages**

```python
# ✅ GOOD - Clear and actionable
raise HTTPException(
    status_code=400,
    detail="Title is required and cannot be empty"
)

# ❌ BAD - Vague or technical
raise HTTPException(
    status_code=400,
    detail="Invalid input"
)

# ❌ BAD - Exposes internal details
raise HTTPException(
    status_code=500,
    detail="SQLAlchemy IntegrityError on column tasks.title"
)
```

### Error Handling Pattern

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

@router.post("/api/v1/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    try:
        task = Task(**task_data.model_dump(), user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    except IntegrityError as e:
        session.rollback()
        # Log the technical error for debugging
        logger.error(f"Database integrity error: {e}")
        # Return user-friendly message
        raise HTTPException(
            status_code=400,
            detail="Unable to create task. Please check your input."
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error creating task: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )
```

### Common Error Scenarios

| Scenario | Status | Error Detail |
|----------|--------|--------------|
| Missing required field | 400 | "{Field} is required" |
| Invalid field value | 400 | "{Field} must be {constraint}" |
| Missing JWT token | 401 | "Authorization required" |
| Invalid/expired JWT | 401 | "Invalid or expired token" |
| Resource not found | 404 | "{Resource} not found" |
| User doesn't own resource | 404 | "{Resource} not found" (same as above) |
| Validation error | 422 | Pydantic validation array |
| Database error | 500 | "An error occurred. Please try again." |
| Unexpected error | 500 | "An unexpected error occurred." |

---

## Phase 2 Required Patterns

### Pattern 1: Soft Deletes

**Never hard delete records - use `deleted_at` timestamp**

```python
# Database Model
class Task(SQLModel, table=True):
    deleted_at: datetime | None = Field(default=None)

# DELETE endpoint - Sets deleted_at, doesn't remove row
@router.delete("/api/v1/tasks/{task_id}")
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.deleted_at == None  # Only soft-delete non-deleted tasks
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Soft delete
    task.deleted_at = datetime.utcnow()
    session.commit()

    return Response(status_code=204)

# ❌ NEVER DO THIS - Hard delete
# session.delete(task)
# session.commit()
```

**All queries MUST exclude soft-deleted records:**

```python
# ✅ ALWAYS include deleted_at filter
statement = select(Task).where(
    Task.user_id == user_id,
    Task.deleted_at == None  # Required!
)

# ❌ WRONG - Missing deleted_at filter
statement = select(Task).where(Task.user_id == user_id)
# This returns deleted tasks too!
```

### Pattern 2: Auto Timestamps

**Every model MUST have `created_at` and `updated_at`**

```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Auto-update updated_at on every change (event listener)
from sqlalchemy import event

@event.listens_for(Task, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()
```

### Pattern 3: JSONB for Arrays

**Use PostgreSQL JSONB for simple arrays (e.g., tags)**

```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Task(SQLModel, table=True):
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default='[]')
    )

# No separate tags table in Phase 2
# Can migrate to junction table in Phase 3+ if needed
```

### Pattern 4: Database Indexes

**Index frequently queried columns**

```python
class Task(SQLModel, table=True):
    user_id: str = Field(index=True)  # Frequently queried
    deleted_at: datetime | None = Field(default=None, index=True)  # For soft delete filter

# Composite index for common query patterns
# CREATE INDEX idx_tasks_user_deleted ON tasks(user_id, deleted_at);
```

**Partial index for soft deletes (optimization):**

```sql
-- Only index non-deleted records
CREATE INDEX idx_tasks_deleted_at
ON tasks(deleted_at)
WHERE deleted_at IS NULL;
```

### Pattern 5: Dependency Injection

**Use FastAPI dependencies for auth, database, etc.**

```python
from fastapi import Depends
from typing import Annotated

# Define dependencies
async def get_db() -> Session:
    with Session(engine) as session:
        yield session

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    # Validate JWT, extract user_id
    payload = jwt.decode(credentials.credentials, settings.JWT_SECRET)
    return payload.get("sub")

# Use dependencies in route handlers
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: Annotated[str, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    # user_id and session automatically injected
    ...
```

---

## Security & Authentication

### JWT Token Structure

**Frontend (Better Auth) issues JWT with this payload:**

```json
{
  "sub": "user-uuid-here",      // user_id (subject)
  "email": "user@example.com",  // optional
  "iat": 1703174400,            // issued at (timestamp)
  "exp": 1703260800             // expires at (timestamp)
}
```

**Backend extracts `user_id` from `sub` claim:**

```python
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """Extract and validate user_id from JWT token."""
    try:
        # Validate JWT signature
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id from 'sub' claim
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

### Authentication Requirement

**ALL endpoints MUST require authentication (except health checks)**

```python
# ✅ CORRECT - Requires authentication
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user)  # Auth required
):
    ...

# ❌ WRONG - No authentication
@router.get("/api/v1/tasks")
async def get_tasks():
    # Anyone can call this!
    ...
```

### CORS Configuration

**Configure CORS to allow frontend origin:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend dev server
        "https://yourdomain.com"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Patterns

### SQLModel Schema Template

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Primary key
    id: int | None = Field(default=None, primary_key=True)

    # User ownership (Phase 2 required)
    user_id: str = Field(index=True, nullable=False)

    # Core fields (from spec)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False)

    # Future features (nullable in Phase 2)
    priority: int | None = Field(default=None, ge=1, le=5)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default='[]')
    )
    due_date: datetime | None = Field(default=None)
    recurrence: str | None = Field(default=None, max_length=20)

    # Phase 2 required patterns
    deleted_at: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Alembic Migration Template

```python
"""Add tasks table

Revision ID: 001
Create Date: 2025-12-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('tags', JSONB, nullable=False, server_default='[]'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurrence', sa.String(20), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index(
        'idx_tasks_deleted_at',
        'tasks',
        ['deleted_at'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index('idx_tasks_user_deleted', 'tasks', ['user_id', 'deleted_at'])

def downgrade():
    op.drop_table('tasks')
```

---

## Testing Standards

### Unit Test Template (Pytest)

```python
import pytest
from fastapi.testclient import TestClient
from src.core.backend.main import app

client = TestClient(app)

def test_create_task_returns_201(auth_headers):
    """Test successful task creation returns 201 with task data."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test Task", "description": "Test description"},
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data

def test_create_task_requires_auth():
    """Test task creation fails without auth token."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test Task"}
        # No auth headers
    )

    assert response.status_code == 401

def test_user_cannot_access_other_users_tasks(auth_headers, other_user_headers):
    """Test user isolation - users can't see each other's tasks."""
    # User 1 creates task
    response1 = client.post(
        "/api/v1/tasks",
        json={"title": "User 1 Task"},
        headers=auth_headers
    )
    task_id = response1.json()["id"]

    # User 2 tries to access User 1's task
    response2 = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=other_user_headers
    )

    assert response2.status_code == 404  # Not 403!
```

### Test Fixtures

```python
import pytest
from src.core.backend.auth import create_access_token

@pytest.fixture
def auth_headers():
    """Provide authentication headers for test user."""
    token = create_access_token({"sub": "test-user-123"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_user_headers():
    """Provide authentication headers for different user."""
    token = create_access_token({"sub": "other-user-456"})
    return {"Authorization": f"Bearer {token}"}
```

---

## Code Examples

### Complete Route Handler Example

```python
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select
from typing import Annotated
from datetime import datetime

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# CREATE
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: Annotated[str, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    """Create a new task for the authenticated user."""
    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# READ (List)
@router.get("", response_model=list[TaskResponse])
async def get_tasks(
    user_id: Annotated[str, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    """Get all tasks for the authenticated user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()
    return tasks

# READ (Single)
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: Annotated[str, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    """Get a specific task by ID."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

# UPDATE
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: Annotated[str, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    """Update a task."""
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.deleted_at == None
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task

# DELETE (Soft)
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: Annotated[str, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    """Soft delete a task."""
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.deleted_at == None
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.deleted_at = datetime.utcnow()
    session.commit()
    return Response(status_code=204)
```

---

## Summary

This backend architecture document establishes:

✅ **API Contract Standards** - URL structure, HTTP methods, status codes, headers
✅ **Data Ownership Rules** - User isolation, user_id from JWT, no user_id in URLs
✅ **Validation Rules** - Pydantic schemas, validation patterns, error formats
✅ **Error Behavior** - Standard error responses, clear messages, proper status codes
✅ **Phase 2 Patterns** - Soft deletes, auto timestamps, JSONB, indexes, dependency injection
✅ **Security & Auth** - JWT validation, authentication requirement, CORS
✅ **Database Patterns** - SQLModel templates, migration templates
✅ **Testing Standards** - Unit test templates, fixtures

**All Phase 2 backend features MUST follow these patterns.**

---

**Document Status:** Active
**Referenced By:** All Phase 2 feature specs (01-07)
**Enforced By:** API Developer Agent, Quality Guardian Agent
**Next Review:** After Feature 02 (Task CRUD) implementation
