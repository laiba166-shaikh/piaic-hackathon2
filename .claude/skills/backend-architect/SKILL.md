---
name: backend-architect
description: Implement FastAPI routes and backend architecture following Phase 2 patterns. Use when (1) creating new API endpoints, (2) implementing backend business logic, (3) setting up FastAPI application structure, or (4) user asks about backend implementation.
license: Complete terms in LICENSE.txt
---

# Backend Architect

Design and implement FastAPI routes, dependency injection, and backend architecture following Phase 2 patterns and best practices.

## Workflow

Follow these steps when implementing backend features:

1. **Design FastAPI route handlers**
   - Map spec endpoints to route functions
   - Define HTTP methods and paths
   - Plan request/response flow
   - Identify dependencies (auth, database)

2. **Create Pydantic request/response models**
   - Request schemas for validation
   - Response schemas for serialization
   - Separate from database models
   - Include field validation rules

3. **Implement SQLModel database operations**
   - CRUD operations with async
   - Query filtering by user_id
   - Soft delete handling
   - Transaction management

4. **Set up dependency injection**
   - Authentication (JWT → user_id)
   - Database session management
   - Shared utilities
   - Error handling

5. **Ensure async patterns**
   - All route handlers async
   - Database operations await
   - Proper error handling
   - Resource cleanup

## Output Format

Present backend architecture using this structure:

```
🏗️ Backend Architecture: [feature-name]

Endpoint: POST /api/v1/tasks
Handler: create_task() in src/core/backend/routers/tasks.py

Dependencies:
- get_current_user() → user_id: str (from JWT)
- get_db() → session: Session (database)

Request Schema (Pydantic):
- TaskCreate: title, description, priority, tags

Response Schema (Pydantic):
- TaskResponse: id, title, description, priority, tags, created_at

Database Model (SQLModel):
- Task: includes user_id, deleted_at, timestamps

Flow:
1. Validate request with TaskCreate schema
2. Extract user_id from JWT via get_current_user()
3. Create Task with user_id from token
4. Save to database
5. Return TaskResponse
```

## Required Project Structure

```
backend/
├── main.py                 # FastAPI app setup, CORS, middleware
├── config.py               # Settings from environment variables
├── dependencies.py         # Shared dependencies (auth, db)
│
├── models/                 # SQLModel database models
│   ├── __init__.py
│   ├── task.py
│   └── base.py             # Shared base fields
│
├── schemas/                # Pydantic request/response schemas
│   ├── __init__.py
│   ├── task.py
│   └── common.py           # Shared schemas (Error, Success)
│
├── routers/                # API route handlers
│   ├── __init__.py
│   ├── tasks.py
│   └── health.py
│
├── services/               # Business logic layer
│   ├── __init__.py
│   └── task_service.py
│
├── database.py             # Database connection and session
├── auth.py                 # JWT validation and user extraction
│
└── tests/
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── conftest.py         # Shared fixtures
```

## Complete Route Implementation Example

**1. Database Model (SQLModel):**
```python
# src/core/backend/models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Task(SQLModel, table=True):
    """Task database model"""
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**2. Pydantic Schemas:**
```python
# src/core/backend/schemas/task.py
from pydantic import BaseModel, Field
from datetime import datetime

class TaskCreate(BaseModel):
    """Request schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)

class TaskUpdate(BaseModel):
    """Request schema for updating a task"""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    tags: list[str] | None = None

class TaskResponse(BaseModel):
    """Response schema for task"""
    id: int
    title: str
    description: str | None
    priority: int | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode
```

**3. Dependencies:**
```python
# src/core/backend/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session
from backend.database import get_session
from backend.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract user_id from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

async def get_db() -> Session:
    """Get database session"""
    async with get_session() as session:
        yield session
```

**4. Route Handler:**
```python
# src/core/backend/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from backend.models.task import Task
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.dependencies import get_current_user, get_db
from datetime import datetime

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Create a new task for the authenticated user"""
    task = Task(
        **task_data.model_dump(),
        user_id=user_id  # From JWT, not request
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.get("", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Get all tasks for the authenticated user"""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None  # Exclude soft-deleted
    )
    result = await session.exec(statement)
    return result.all()

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Get a specific task"""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,  # User isolation
        Task.deleted_at == None
    )
    task = await session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Update a task"""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    task = await session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Soft delete a task"""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    task = await session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Soft delete
    task.deleted_at = datetime.utcnow()
    session.add(task)
    await session.commit()
```

**5. Main App Setup:**
```python
# src/core/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import tasks
from backend.config import settings

app = FastAPI(
    title="Task Manager API",
    description="Phase 2 Full-Stack Task Manager",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Key Architecture Rules

**1. All routes require authentication**
- Use `Depends(get_current_user)` on all protected routes
- Extract user_id from JWT, never URL/body
- Return 401 for invalid/missing tokens

**2. Filter all queries by user_id**
- Every query includes `WHERE user_id = ?`
- Prevents cross-user data access
- Apply to SELECT, UPDATE, DELETE

**3. Use soft deletes**
- Set `deleted_at = datetime.utcnow()`
- Never hard delete user data
- Filter `WHERE deleted_at IS NULL`

**4. Async all database operations**
- Route handlers are `async def`
- Database calls use `await`
- Proper resource cleanup

**5. Separate schemas from models**
- Pydantic schemas for API (request/response)
- SQLModel models for database
- Never expose database model directly

**6. Service layer for business logic**
- Keep routes thin (validation, dependencies)
- Move complex logic to services
- Easier to test and reuse

**7. Proper error handling**
- HTTPException for client errors
- Appropriate status codes
- Clear error messages

**8. Transaction management**
- Commit on success
- Rollback on error
- Use context managers

## Key Rules

- **All routes require authentication** - Use `Depends(get_current_user)`
- **user_id from JWT only** - Never from URL/body
- **Filter queries by user_id** - Every user-scoped query
- **Use soft deletes** - Set deleted_at, filter it out
- **Async all database operations** - FastAPI best practice
- **Separate schemas from models** - API schemas vs DB models
- **Service layer for logic** - Keep routes thin
- **Proper HTTP status codes** - 200, 201, 204, 400, 401, 404
- **Validate with Pydantic** - Request/response schemas
- **Handle errors gracefully** - HTTPException with details
