# Backend Guidelines

**Project:** Phase 2 - Full-Stack Web Application (Backend)
**Framework:** FastAPI with SQLModel
**Last Updated:** 2025-12-26

---

## Stack

- **FastAPI** - Modern, fast Python web framework
- **SQLModel** - SQL database ORM combining SQLAlchemy and Pydantic
- **Neon PostgreSQL** - Serverless PostgreSQL database
- **PyJWT** - JSON Web Token implementation for authentication
- **Alembic** - Database migration tool

---

## Project Structure

```
backend/
├── main.py                     # FastAPI app entry point
├── config.py                   # Configuration and environment variables
├── db.py                       # Database connection and session management
├── dependencies.py             # FastAPI dependencies (auth, db session)
├── models/                     # SQLModel database models
│   ├── __init__.py
│   └── task.py                 # Task model
├── api/                        # API route handlers
│   └── v1/                     # API version 1
│       ├── __init__.py
│       └── tasks.py            # Task CRUD endpoints
├── schemas/                    # Pydantic request/response schemas
│   ├── __init__.py
│   └── task.py                 # Task schemas (TaskCreate, TaskUpdate, TaskResponse)
├── migrations/                 # Alembic database migrations
│   ├── env.py
│   └── versions/               # Migration version files
└── tests/                      # Test files
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures
    ├── test_auth.py            # Authentication tests
    ├── test_tasks.py           # Task CRUD tests
    └── fixtures/               # Test data and utilities
        └── jwt_tokens.py       # JWT token generators for testing
```

---

## API Conventions

### URL Structure

**Pattern:** `/api/v{version}/{resource}`

**Examples:**
- `GET /api/v1/tasks` - List all tasks
- `POST /api/v1/tasks` - Create a task
- `GET /api/v1/tasks/{id}` - Get a single task
- `PUT /api/v1/tasks/{id}` - Update a task
- `DELETE /api/v1/tasks/{id}` - Delete a task
- `PATCH /api/v1/tasks/{id}/toggle` - Toggle task completion

### Response Format

**Success Response:**
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-26T10:00:00Z",
  "updated_at": "2025-12-26T10:00:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Task not found or you don't have permission to access it"
}
```

### Status Codes

- **200 OK** - Successful GET, PUT, PATCH
- **201 Created** - Successful POST
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Missing or invalid JWT token
- **404 Not Found** - Resource not found or not accessible
- **500 Internal Server Error** - Server error

---

## Database Patterns

### SQLModel Models

**Location:** `models/task.py`

**Example:**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Connection

**Location:** `db.py`

```python
from sqlmodel import create_engine, Session
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.DEBUG else False,
    connect_args={"sslmode": "require"}
)

def get_session():
    """Dependency for database sessions"""
    with Session(engine) as session:
        yield session
```

### Query Patterns

**Always filter by user_id and deleted_at:**
```python
# ✅ Correct - User isolation enforced
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .where(Task.deleted_at == None)
).all()

# ❌ Wrong - Exposes all users' data
tasks = session.exec(select(Task)).all()
```

**Soft Delete Pattern:**
```python
# ✅ Correct - Soft delete
task.deleted_at = datetime.utcnow()
session.add(task)
session.commit()

# ❌ Wrong - Hard delete
session.delete(task)
session.commit()
```

---

## Authentication & Authorization

### JWT Validation

**Location:** `dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate JWT token, return user_id.

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

### Using Authentication in Routes

```python
from fastapi import APIRouter, Depends
from dependencies import get_current_user

router = APIRouter()

@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all tasks for the authenticated user"""
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.deleted_at == None)
    ).all()
    return tasks
```

---

## Request/Response Schemas

**Location:** `schemas/task.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    """Schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## Error Handling

### Standard Error Responses

```python
from fastapi import HTTPException, status

# 400 Bad Request - Validation Error
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Title is required and cannot be empty"
)

# 401 Unauthorized - Authentication Error
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials"
)

# 404 Not Found - Resource Not Found or Not Accessible
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not found or you don't have permission to access it"
)

# 500 Internal Server Error - Unexpected Error
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="An unexpected error occurred"
)
```

### Error Logging

```python
import logging

logger = logging.getLogger(__name__)

try:
    # ... database operation
except Exception as e:
    logger.error(f"Error creating task for user {user_id}: {str(e)}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create task"
    )
```

---

## CORS Configuration

**Location:** `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,                   # Allow cookies (JWT)
    allow_methods=["*"],                      # Allow all HTTP methods
    allow_headers=["*"],                      # Allow all headers
)
```

---

## Configuration Management

**Location:** `config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration from environment variables"""

    # Database
    DATABASE_URL: str

    # Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Application
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**Environment Variables (.env):**
```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET=your-256-bit-secret-key-here
DEBUG=True
```

---

## Testing Guidelines

### Test Structure

**Location:** `tests/test_tasks.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from fixtures.jwt_tokens import create_test_token

client = TestClient(app)

def test_create_task_success():
    """Test creating a task with valid data"""
    token = create_test_token(user_id="user123")
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test Task", "description": "Test Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

def test_create_task_unauthorized():
    """Test creating a task without authentication"""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test Task"}
    )
    assert response.status_code == 401
```

### Test Fixtures

**Location:** `tests/conftest.py`

```python
import pytest
from sqlmodel import create_engine, Session, SQLModel
from fastapi.testclient import TestClient
from main import app
from db import get_session

@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with test database"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

---

## Database Migrations

### Creating a Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Create tasks table"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Migration Template

**Location:** `migrations/versions/001_create_tasks.py`

```python
"""Create tasks table

Revision ID: 001
Revises:
Create Date: 2025-12-26 10:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False, index=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_user_deleted', 'tasks', ['user_id', 'deleted_at'])

def downgrade() -> None:
    op.drop_table('tasks')
```

---

## Running the Application

### Development Server

```bash
cd backend

# Install dependencies
pip install -r requirements.txt
# or
uv pip install

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --port 8000
```

**Server starts at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs (Swagger UI)

### Environment Setup

1. Create `.env` file in backend directory
2. Add required environment variables (see Configuration section)
3. Never commit `.env` file to version control

---

## Key Principles

1. **User Isolation** - ALWAYS filter queries by `user_id` from JWT token
2. **Soft Deletes** - Use `deleted_at` timestamp instead of hard deletes
3. **Type Safety** - Use Pydantic models for all request/response data
4. **Error Handling** - Return appropriate HTTP status codes and error messages
5. **Security** - Validate JWT tokens, sanitize inputs, use parameterized queries
6. **Testing** - Write tests before implementation (TDD)
7. **Logging** - Log errors with context, never log sensitive data

---

## Common Pitfalls to Avoid

❌ **Don't skip user_id filtering** - Every query must filter by authenticated user
❌ **Don't use hard deletes** - Always use soft deletes with `deleted_at`
❌ **Don't expose user_id in URLs** - Extract from JWT token only
❌ **Don't return 404 for unauthorized access** - Use 404 (not 403) to prevent user enumeration
❌ **Don't log JWT tokens or passwords** - Sensitive data must never be logged
❌ **Don't commit secrets to git** - Use environment variables

---

## Security Checklist

- ✅ All endpoints require JWT authentication (except public endpoints)
- ✅ All queries filter by `user_id` from JWT token
- ✅ Input validation using Pydantic schemas
- ✅ SQL injection prevention via SQLModel parameterized queries
- ✅ CORS configured for frontend origin only
- ✅ HTTP-only cookies for JWT storage (frontend responsibility)
- ✅ Secrets stored in environment variables
- ✅ Error messages don't expose sensitive information

---

## Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **SQLModel Documentation:** https://sqlmodel.tiangolo.com
- **Alembic Documentation:** https://alembic.sqlalchemy.org
- **PyJWT Documentation:** https://pyjwt.readthedocs.io
- **Phase 2 Backend Architecture:** `../specs/002-phase2-fullstack-web/00-backend-architecture.md`
- **API Endpoints Specification:** `../specs/002-phase2-fullstack-web/api/rest-endpoints.md`
- **Database Schema:** `../specs/002-phase2-fullstack-web/database/schema.md`

---

**Last Updated:** 2025-12-26
**Maintained By:** Phase 2 Implementation Team
