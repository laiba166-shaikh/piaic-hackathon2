---
name: database-designer
description: Design PostgreSQL schemas with SQLModel following Phase 2 architecture patterns. Use when (1) creating new database tables, (2) adding fields to existing tables, (3) user asks about schema design, or (4) implementing backend models from specifications.
license: Complete terms in LICENSE.txt
---

# Database Designer

Design normalized PostgreSQL schemas using SQLModel with proper types, indexes, and constraints following Phase 2 architecture patterns.

## Workflow

Follow these steps when designing database schemas:

1. **Read database requirements** from `specs/phase2/database/schema.md`
   - Identify entities and their fields
   - Note relationships between entities
   - Understand business constraints
   - Check for user isolation requirements

2. **Design normalized schemas**
   - Apply Phase 2 patterns (soft deletes, JSONB tags, timestamps)
   - Add user_id for multi-user data isolation
   - Choose appropriate field types
   - Define relationships (foreign keys where appropriate)

3. **Create SQLModel models** with proper types
   - Use SQLModel for ORM mapping
   - Add Field() validators and constraints
   - Include proper defaults
   - Document fields with docstrings

4. **Suggest indexes and constraints**
   - Index user_id for multi-user queries
   - Index deleted_at for soft delete filtering
   - Add unique constraints where needed
   - Consider composite indexes for common queries

5. **Plan migrations**
   - Use Alembic for schema versioning
   - Suggest migration commands
   - Consider data migration needs
   - Plan rollback strategy

## Output Format

Present schema design using this structure:

```
🗄️ Schema Design: [table-name]

Source: specs/phase2/database/schema.md

SQLModel:
[code snippet with complete model definition]

Indexes:
- idx_[table]_user_id ON user_id (B-tree)
- idx_[table]_deleted_at ON deleted_at WHERE deleted_at IS NULL (partial)
- idx_[table]_[field] ON [field] (B-tree)

Constraints:
- UNIQUE(user_id, [natural_key]) for user-scoped uniqueness
- CHECK constraints for validation

Migration:
alembic revision -m "add [table-name] table"
```

## Phase 2 Required Patterns

Every SQLModel must include these patterns:

**1. Soft Deletes:**
```python
deleted_at: datetime | None = Field(default=None, nullable=True)
```

**2. JSONB Tags Array:**
```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

tags: list[str] = Field(
    default_factory=list,
    sa_column=Column(JSONB)
)
```

**3. Automatic Timestamps:**
```python
from datetime import datetime

created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(
    default_factory=datetime.utcnow,
    sa_column_kwargs={"onupdate": datetime.utcnow}
)
```

**4. User Ownership:**
```python
user_id: str = Field(index=True)  # From JWT, no FK to users table
```

## Complete SQLModel Example

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional

class Task(SQLModel, table=True):
    """Task model for Phase 2 full-stack application

    Follows ADR-004 architecture patterns:
    - Soft deletes (deleted_at)
    - JSONB tags array
    - User isolation (user_id from JWT)
    - Automatic timestamps
    """
    __tablename__ = "tasks"

    # Primary key
    id: int | None = Field(default=None, primary_key=True)

    # User ownership (from JWT, no FK)
    user_id: str = Field(index=True, description="User ID from JWT token")

    # Core fields
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str | None = Field(default=None, description="Task description")
    priority: int | None = Field(default=None, ge=1, le=5, description="Priority (1-5)")

    # JSONB tags (Phase 2 pattern)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="Task tags as JSONB array"
    )

    # Soft delete (Phase 2 pattern)
    deleted_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Soft delete timestamp"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Last update timestamp"
    )
```

## Required Indexes

**Every table needs these indexes:**

```python
# In Alembic migration:
op.create_index(
    'idx_tasks_user_id',
    'tasks',
    ['user_id']
)

op.create_index(
    'idx_tasks_deleted_at',
    'tasks',
    ['deleted_at'],
    postgresql_where=text('deleted_at IS NULL')  # Partial index
)
```

**Additional indexes based on queries:**
- Index foreign keys for joins
- Index fields used in WHERE clauses
- Composite indexes for multi-field queries
- Unique indexes for natural keys scoped by user_id

## Key Rules

- **Follow ADR-004 database patterns** - Soft deletes, JSONB tags, user_id, timestamps
- **User isolation enforced** - Every user-scoped table has user_id indexed
- **No users table in backend** - Authentication is frontend concern (Better Auth)
- **Use soft deletes** - deleted_at filter, never hard delete user data
- **Tags as JSONB array** - Not junction table, stored as JSONB for flexibility
- **Suggest indexes** - Always propose indexes for user_id, deleted_at, and query fields
- **Plan migrations** - Provide Alembic migration commands
- **Type safety** - Use proper Python types with Field() validators
- **Document models** - Include docstrings explaining purpose and patterns
