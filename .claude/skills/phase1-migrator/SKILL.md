---
name: phase1-migrator
description: Port Phase 1 CLI code to Phase 2 web architecture while preserving business logic and adapting to multi-user, database-backed patterns. Use when (1) setting up Phase 2 initially, (2) user asks "can we reuse Phase 1 code?", (3) converting models/logic from CLI to API, or (4) adapting business rules for web context.
license: Complete terms in LICENSE.txt
---

# Phase 1 Migrator

Analyze Phase 1 CLI code and port reusable components to Phase 2 web architecture, adapting for multi-user context and database storage.

## Workflow

Follow these steps when migrating Phase 1 code:

1. **Analyze Phase 1 code** in `cli/src/core/`
   - Identify models (Task, Priority, Recurrence enums)
   - Review validation logic
   - Extract business rules
   - Note test patterns

2. **Identify reusable components**
   - Data structures (dataclasses → SQLModel)
   - Enums (Priority, Recurrence, Status)
   - Validation rules (Pydantic validators)
   - Business logic methods

3. **Suggest Phase 2 conversions**
   - How to adapt models for database
   - Multi-user isolation requirements
   - API endpoint structure
   - Test migration strategy

4. **Port models to SQLModel**
   - Convert dataclasses to SQLModel
   - Add database-specific fields (id, user_id, timestamps)
   - Apply Phase 2 patterns (soft deletes, JSONB tags)
   - Preserve validation logic

5. **Adapt business logic for web context**
   - Convert synchronous to async where needed
   - Add user_id filtering to all queries
   - Update for stateless FastAPI architecture
   - Maintain Phase 1 behavior where possible

## Output Format

Present migration analysis using this structure:

```
🔄 Migration Analysis: [component-name]

Phase 1 Source: cli/src/core/[file].py
Phase 2 Target: src/core/backend/[location]/[file].py

Reusable:
✅ Task model structure (title, description, priority)
✅ Priority enum (Low=1, Medium=2, High=3, Urgent=4, Critical=5)
✅ Validation logic (title length, priority range)
✅ Business rules (task lifecycle, status transitions)

Adaptations Needed:
⚠️ Convert dataclass to SQLModel with table=True
⚠️ Add user_id: str field for multi-user isolation
⚠️ Add deleted_at: datetime | None for soft deletes
⚠️ Change tags: list[str] to JSONB column
⚠️ Add timestamps (created_at, updated_at)
⚠️ Convert sync storage methods to async database queries

New Requirements:
➕ Database session management (SQLModel Session)
➕ JWT authentication integration (extract user_id)
➕ API request/response schemas (Pydantic)
➕ FastAPI route handlers (async def)
➕ User isolation on all queries (WHERE user_id = ?)
```

## Conversion Patterns

### Phase 1 → Phase 2 Model Conversion

**Phase 1 (CLI):**
```python
from dataclasses import dataclass
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class Task:
    id: int
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    tags: list[str] = field(default_factory=list)
```

**Phase 2 (Web):**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from enum import IntEnum

class Priority(IntEnum):  # ✅ Keep Phase 1 enum
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class Task(SQLModel, table=True):  # ⚠️ Converted to SQLModel
    __tablename__ = "tasks"

    # Database fields
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # ➕ NEW: multi-user

    # Phase 1 fields (preserved)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None)
    priority: int = Field(default=Priority.MEDIUM, ge=1, le=5)

    # Phase 2 patterns
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))  # ⚠️ JSONB
    deleted_at: datetime | None = Field(default=None)  # ➕ NEW: soft delete
    created_at: datetime = Field(default_factory=datetime.utcnow)  # ➕ NEW
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # ➕ NEW
```

### Phase 1 → Phase 2 Storage Conversion

**Phase 1 (In-Memory):**
```python
class MemoryStorage:
    def __init__(self):
        self.tasks: dict[int, Task] = {}

    def create(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def get_all(self) -> list[Task]:
        return list(self.tasks.values())
```

**Phase 2 (Database):**
```python
from sqlmodel import Session, select

async def create_task(
    task_data: TaskCreate,
    user_id: str,  # ➕ NEW: from JWT
    session: Session
) -> Task:
    task = Task(
        **task_data.dict(),
        user_id=user_id  # ➕ NEW: user isolation
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def get_tasks(
    user_id: str,  # ➕ NEW: from JWT
    session: Session
) -> list[Task]:
    statement = select(Task).where(
        Task.user_id == user_id,  # ➕ NEW: user filter
        Task.deleted_at == None  # ➕ NEW: soft delete filter
    )
    result = await session.exec(statement)
    return result.all()
```

### Phase 1 → Phase 2 CLI Command to API Route

**Phase 1 (CLI Command):**
```python
def add_task(title: str, description: str = None):
    task = Task(title=title, description=description)
    storage.create(task)
    print(f"Task created: {task.title}")
```

**Phase 2 (FastAPI Route):**
```python
from fastapi import APIRouter, Depends
from src.core.backend.dependencies import get_current_user, get_db

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),  # ➕ NEW: JWT auth
    session: Session = Depends(get_db)
):
    task = await create_task(task_data, user_id, session)
    return task
```

## What to Keep from Phase 1

**✅ Preserve these exactly:**
- Enum definitions (Priority, Recurrence, Status)
- Validation rules (field lengths, ranges, formats)
- Business logic methods (status transitions, calculations)
- Test patterns (unit tests structure, test cases)
- Error messages and user feedback

**⚠️ Adapt these for Phase 2:**
- Data models (dataclass → SQLModel)
- Storage layer (in-memory → PostgreSQL)
- Sync code → async/await for FastAPI
- Single-user → multi-user with user_id

**➕ Add these for Phase 2:**
- user_id field on all user-scoped data
- deleted_at for soft deletes
- Timestamps (created_at, updated_at)
- Database session management
- JWT authentication integration
- API request/response schemas

## Key Rules

- **Reference Phase 1, don't duplicate** - Import enums and utilities where possible
- **Preserve business logic** - Keep validation rules and behavior from Phase 1
- **Add multi-user isolation** - Every model needs user_id from JWT
- **Convert to async patterns** - FastAPI requires async database operations
- **Keep Phase 1 CLI working** - Don't modify cli/ files during Phase 2 development
- **Port tests** - Adapt Phase 1 test cases to pytest for Phase 2
- **Document changes** - Comment what changed from Phase 1 and why
- **Maintain compatibility** - Phase 1 and Phase 2 should handle same business rules
