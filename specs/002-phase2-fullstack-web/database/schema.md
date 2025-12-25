# Database Schema Specification - Phase 2 Full-Stack Web Application

**Project:** Todo Application - Hackathon II Phase 2
**Database:** Neon Serverless PostgreSQL
**ORM:** SQLModel (SQLAlchemy + Pydantic)
**Version:** Phase 2 - Basic Level Features
**Date:** 2025-12-25
**Status:** Design Complete

---

## 1. Overview

This document specifies the complete PostgreSQL database schema for Phase 2 of the Todo application. The database follows a **two-database architecture** where user authentication is managed separately by Better Auth (frontend), and the backend database stores only task-related data with user isolation enforced via JWT tokens.

### Key Design Principles

- **User Isolation:** All tables have `user_id` foreign key for multi-user data separation
- **Soft Deletes:** Tasks use `deleted_at` timestamp instead of hard deletes
- **Auto Timestamps:** `created_at` and `updated_at` automatically managed
- **JSONB for Flexibility:** Tags stored as JSONB array for Phase 2+ features
- **Performance:** Strategic indexes on frequently queried columns
- **Type Safety:** SQLModel models provide Pydantic validation + SQLAlchemy ORM

---

## 2. Database Connection

### Connection Configuration

**Database Type:** PostgreSQL 15+ (Neon Serverless)
**ORM:** SQLModel (combines SQLAlchemy + Pydantic)
**Connection Pooling:** SQLAlchemy engine with pool size configuration
**SSL Mode:** `require` (mandatory for Neon connections)

### Environment Variable

```bash
# Backend .env file
DATABASE_URL=postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/todo_db?sslmode=require
```

### Connection String Format

```
postgresql://<username>:<password>@<host>/<database>?sslmode=require
```

### Connection Pooling Configuration

```python
# backend/db.py
from sqlmodel import create_engine, Session

engine = create_engine(
    database_url,
    echo=True,  # SQL logging (disable in production)
    pool_size=5,  # Number of permanent connections
    max_overflow=10,  # Max connections beyond pool_size
    pool_pre_ping=True,  # Check connection health before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)
```

---

## 3. Tables

### 3.1 users Table

**Status:** ❌ **NOT PRESENT IN BACKEND DATABASE**

**Managed By:** Better Auth (frontend database)

**Important Note:**
The backend database has **NO users table**. User accounts are completely managed by Better Auth in the frontend database. The backend trusts JWT tokens issued by the frontend and extracts `user_id` from the token's `sub` claim.

**user_id Usage:**
The `user_id` field in backend tables is an **opaque string identifier** extracted from JWT tokens. It is NOT a foreign key to any users table in the backend database.

**Why No Users Table:**
1. **Separation of Concerns:** Frontend handles authentication, backend handles task data
2. **Simplified Backend:** No password hashing, email verification, or user CRUD operations
3. **Stateless Architecture:** Backend validates JWT tokens (stateless), doesn't query user records
4. **Trust Model:** Backend trusts JWT tokens issued by frontend (single issuer)

---

### 3.2 tasks Table

**Primary Table:** Stores all task data for all users with strict user isolation

#### SQL Schema

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20),
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    due_date TIMESTAMP WITH TIME ZONE,
    recurrence VARCHAR(20),
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### Table Purpose

- **Scope:** All task data for all users (multi-tenant)
- **Isolation:** `user_id` field ensures data separation between users
- **Soft Deletes:** Tasks are marked deleted via `deleted_at`, not removed
- **Phase 2 Fields:** Includes fields for future features (priority, tags, due_date, recurrence)

---

## 4. Field Specifications

### tasks Table Fields

| Field | Type | Nullable | Default | Description | Phase 2 Usage |
|-------|------|----------|---------|-------------|---------------|
| `id` | SERIAL (integer) | NO | auto-increment | Primary key, unique task identifier | ✅ Active |
| `user_id` | VARCHAR(255) | NO | - | Owner's user ID from JWT `sub` claim (indexed) | ✅ Active |
| `title` | VARCHAR(200) | NO | - | Task title (1-200 characters) | ✅ Active |
| `description` | TEXT | YES | NULL | Task description (unlimited length) | ✅ Active |
| `completed` | BOOLEAN | NO | FALSE | Completion status (true/false) | ✅ Active |
| `priority` | VARCHAR(20) | YES | NULL | Priority level: "low", "medium", "high" | ⏸️ Exists but not used |
| `tags` | JSONB | NO | `'[]'` | Array of tag strings (e.g., `["work", "urgent"]`) | ⏸️ Exists but not used |
| `due_date` | TIMESTAMP WITH TIME ZONE | YES | NULL | Task deadline (ISO 8601 timestamp) | ⏸️ Exists but not used |
| `recurrence` | VARCHAR(20) | YES | NULL | Recurrence pattern: "daily", "weekly", "monthly" | ⏸️ Exists but not used |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | YES | NULL | Soft delete timestamp (NULL = active task) | ✅ Active |
| `created_at` | TIMESTAMP WITH TIME ZONE | NO | NOW() | Creation timestamp (auto-set on insert) | ✅ Active |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NO | NOW() | Last update timestamp (auto-updated) | ✅ Active |

### Field Detailed Descriptions

#### id (Primary Key)
- **Type:** SERIAL (auto-incrementing integer)
- **Constraint:** PRIMARY KEY
- **Purpose:** Unique identifier for each task
- **Generated By:** PostgreSQL automatically on INSERT

#### user_id (Owner Identifier)
- **Type:** VARCHAR(255)
- **Source:** JWT token `sub` claim (issued by Better Auth)
- **Format:** UUID string (e.g., `"550e8400-e29b-41d4-a716-446655440000"`)
- **Constraint:** NOT NULL (every task must have an owner)
- **Indexed:** YES (critical for user isolation queries)
- **Foreign Key:** NO (no users table in backend database)
- **Validation:** Extracted from validated JWT token (enforced by `get_current_user` dependency)

#### title (Task Title)
- **Type:** VARCHAR(200)
- **Constraint:** NOT NULL, 1-200 characters
- **Validation Rules:**
  - Minimum 1 character (after trimming whitespace)
  - Maximum 200 characters
  - Cannot be whitespace-only (enforced by CHECK constraint)
- **Example:** `"Buy groceries"`, `"Complete project report"`

#### description (Task Description)
- **Type:** TEXT
- **Constraint:** NULLABLE (optional field)
- **Max Length:** Unlimited (PostgreSQL TEXT supports ~1GB)
- **Example:** `"Need to buy milk, eggs, bread, and fruits for the week"`
- **Null vs Empty String:**
  - `NULL` = No description provided
  - `""` = Empty description provided (valid but empty)

#### completed (Completion Status)
- **Type:** BOOLEAN
- **Constraint:** NOT NULL, DEFAULT FALSE
- **Values:** `true` (completed) or `false` (incomplete)
- **Phase 2 Usage:** Toggled via PATCH `/api/v1/tasks/{id}/toggle`
- **Index:** YES (for filtering by completion status)

#### priority (Task Priority) - Phase 3+
- **Type:** VARCHAR(20)
- **Constraint:** NULLABLE
- **Values:** `"low"`, `"medium"`, `"high"`, or NULL
- **Phase 2 Status:** Field exists but NOT used (always NULL in Phase 2)
- **Future Usage:** Phase 3 feature for task prioritization

#### tags (Task Tags) - Phase 3+
- **Type:** JSONB (PostgreSQL JSON Binary)
- **Constraint:** NOT NULL, DEFAULT `'[]'::jsonb`
- **Values:** Array of strings: `["work", "urgent", "personal"]`
- **Phase 2 Status:** Field exists but NOT used (always `[]` in Phase 2)
- **Future Usage:** Phase 3 feature for task categorization
- **Example:** `["work", "urgent"]`, `[]` (empty array)

#### due_date (Task Deadline) - Phase 3+
- **Type:** TIMESTAMP WITH TIME ZONE
- **Constraint:** NULLABLE
- **Format:** ISO 8601 timestamp with timezone
- **Phase 2 Status:** Field exists but NOT used (always NULL in Phase 2)
- **Future Usage:** Phase 3 feature for task deadlines and reminders
- **Example:** `"2025-12-31T23:59:59Z"`

#### recurrence (Recurrence Pattern) - Phase 3+
- **Type:** VARCHAR(20)
- **Constraint:** NULLABLE
- **Values:** `"daily"`, `"weekly"`, `"monthly"`, or NULL
- **Phase 2 Status:** Field exists but NOT used (always NULL in Phase 2)
- **Future Usage:** Phase 3 feature for recurring tasks
- **Example:** `"weekly"` (task repeats every week)

#### deleted_at (Soft Delete Timestamp)
- **Type:** TIMESTAMP WITH TIME ZONE
- **Constraint:** NULLABLE
- **Purpose:** Soft delete mechanism (tasks never physically deleted)
- **Active Task:** `deleted_at = NULL`
- **Deleted Task:** `deleted_at = <timestamp when deleted>`
- **Query Pattern:** All queries must filter `WHERE deleted_at IS NULL`
- **Index:** Partial index on `deleted_at` WHERE `deleted_at IS NULL`

#### created_at (Creation Timestamp)
- **Type:** TIMESTAMP WITH TIME ZONE
- **Constraint:** NOT NULL, DEFAULT NOW()
- **Purpose:** Track when task was created
- **Auto-Generated:** Set automatically by database on INSERT
- **Immutable:** Never updated after creation
- **Example:** `"2025-12-25T10:30:00Z"`

#### updated_at (Last Update Timestamp)
- **Type:** TIMESTAMP WITH TIME ZONE
- **Constraint:** NOT NULL, DEFAULT NOW()
- **Purpose:** Track when task was last modified
- **Auto-Updated:** Refreshed automatically on UPDATE via trigger
- **Example:** `"2025-12-25T14:45:30Z"`

---

## 5. Constraints

### tasks Table Constraints

#### Primary Key Constraint
```sql
PRIMARY KEY (id)
```
- **Purpose:** Ensure each task has a unique identifier
- **Auto-Generated:** SERIAL type auto-increments on INSERT

#### NOT NULL Constraints
```sql
user_id NOT NULL
title NOT NULL
completed NOT NULL
tags NOT NULL
created_at NOT NULL
updated_at NOT NULL
```
- **Purpose:** Ensure critical fields always have values
- **user_id:** Every task must have an owner
- **title:** Every task must have a title
- **completed:** Completion status must be explicit (true/false)
- **tags:** Always an array (empty `[]` if no tags)
- **created_at, updated_at:** Timestamps must exist

#### Title Length Constraint
```sql
CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200)
```
- **Purpose:** Enforce title length between 1-200 characters
- **Validation:** Prevents empty titles and excessively long titles

#### Title Whitespace Constraint
```sql
CHECK (title !~ '^\s*$')
```
- **Purpose:** Prevent whitespace-only titles (e.g., `"   "`)
- **Regex:** `^\s*$` matches strings containing only whitespace
- **Negation:** `!~` ensures title does NOT match whitespace-only pattern

---

## 6. Indexes

Indexes optimize query performance for frequently filtered and sorted columns.

### tasks Table Indexes

#### Primary Key Index (Automatic)
```sql
-- Created automatically by PRIMARY KEY constraint
CREATE UNIQUE INDEX tasks_pkey ON tasks(id);
```
- **Type:** Unique B-tree index
- **Purpose:** Fast task lookup by ID
- **Usage:** `SELECT * FROM tasks WHERE id = 5`

#### User ID Index (Critical for User Isolation)
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```
- **Type:** B-tree index
- **Purpose:** Fast filtering by user for multi-tenant queries
- **Usage:** `SELECT * FROM tasks WHERE user_id = 'user-123'`
- **Criticality:** ⭐⭐⭐⭐⭐ (Every query filters by user_id)

#### Partial Index for Soft Deletes
```sql
CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at) WHERE deleted_at IS NULL;
```
- **Type:** Partial B-tree index (only indexes non-deleted tasks)
- **Purpose:** Fast filtering to exclude soft-deleted tasks
- **Usage:** `SELECT * FROM tasks WHERE deleted_at IS NULL`
- **Optimization:** Smaller index (only active tasks), faster queries

#### Composite Index: User + Deleted
```sql
CREATE INDEX idx_tasks_user_deleted ON tasks(user_id, deleted_at);
```
- **Type:** Composite B-tree index
- **Purpose:** Optimize queries filtering by user AND deleted status
- **Usage:** `SELECT * FROM tasks WHERE user_id = 'user-123' AND deleted_at IS NULL`
- **Performance:** Single index scan covers both conditions

#### Completion Status Index
```sql
CREATE INDEX idx_tasks_completed ON tasks(completed);
```
- **Type:** B-tree index
- **Purpose:** Fast filtering by completion status
- **Usage:** `SELECT * FROM tasks WHERE completed = false`
- **Use Case:** Filter "active" vs "completed" tasks

#### Composite Index: User + Completion
```sql
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```
- **Type:** Composite B-tree index
- **Purpose:** Optimize queries filtering by user AND completion status
- **Usage:** `SELECT * FROM tasks WHERE user_id = 'user-123' AND completed = false`
- **Use Case:** "Show me my active tasks" queries

### Index Usage Summary

| Index Name | Columns | Type | Primary Usage |
|------------|---------|------|---------------|
| `tasks_pkey` | `id` | Unique B-tree | Task lookup by ID |
| `idx_tasks_user_id` | `user_id` | B-tree | User isolation (every query) |
| `idx_tasks_deleted_at` | `deleted_at` WHERE NULL | Partial B-tree | Exclude soft-deleted tasks |
| `idx_tasks_user_deleted` | `user_id, deleted_at` | Composite | User + soft delete filtering |
| `idx_tasks_completed` | `completed` | B-tree | Filter by completion status |
| `idx_tasks_user_completed` | `user_id, completed` | Composite | User + completion filtering |

---

## 7. Triggers

### Auto-Update `updated_at` Timestamp

PostgreSQL trigger function to automatically refresh `updated_at` on every UPDATE.

#### Trigger Function

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Function Details:**
- **Name:** `update_updated_at_column`
- **Returns:** TRIGGER (special return type for trigger functions)
- **Logic:** Sets `NEW.updated_at` to current timestamp before UPDATE completes
- **Language:** PL/pgSQL (PostgreSQL's procedural language)

#### Trigger Definition

```sql
CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

**Trigger Details:**
- **Name:** `update_tasks_updated_at`
- **Timing:** BEFORE UPDATE (executes before row is updated)
- **Scope:** FOR EACH ROW (runs for every updated row)
- **Function:** Calls `update_updated_at_column()` to set `updated_at`

**Example Behavior:**
```sql
-- Initial state
INSERT INTO tasks (user_id, title) VALUES ('user-123', 'Buy groceries');
-- created_at = 2025-12-25 10:00:00
-- updated_at = 2025-12-25 10:00:00

-- Update task
UPDATE tasks SET title = 'Buy groceries and fruits' WHERE id = 1;
-- Trigger automatically sets: updated_at = 2025-12-25 14:30:00
-- created_at remains: 2025-12-25 10:00:00 (unchanged)
```

---

## 8. SQLModel Models

SQLModel combines SQLAlchemy ORM with Pydantic validation, providing type-safe database operations.

### Task Model (Python)

```python
# backend/models.py
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model for todo items with user isolation.

    Combines SQLAlchemy ORM (database operations) with Pydantic validation
    (type safety and data validation).
    """
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique task identifier (auto-generated)"
    )

    # User Isolation (Critical Field)
    user_id: str = Field(
        index=True,
        nullable=False,
        max_length=255,
        description="Owner's user ID from JWT token sub claim"
    )

    # Task Content
    title: str = Field(
        max_length=200,
        nullable=False,
        min_length=1,
        description="Task title (1-200 characters, required)"
    )

    description: Optional[str] = Field(
        default=None,
        description="Task description (optional, unlimited length)"
    )

    # Task Status
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status (true/false)"
    )

    # Phase 3+ Fields (exist but not used in Phase 2)
    priority: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Priority level: low, medium, high (Phase 3+)"
    )

    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default='[]'),
        description="Array of tag strings (Phase 3+)"
    )

    due_date: Optional[datetime] = Field(
        default=None,
        description="Task deadline (ISO 8601 timestamp, Phase 3+)"
    )

    recurrence: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Recurrence pattern: daily, weekly, monthly (Phase 3+)"
    )

    # Soft Delete
    deleted_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Soft delete timestamp (NULL = active task)"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp (auto-set on insert)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (auto-updated via trigger)"
    )

    class Config:
        """Pydantic configuration for SQLModel"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and fruits",
                "completed": false,
                "priority": null,
                "tags": [],
                "due_date": null,
                "recurrence": null,
                "deleted_at": null,
                "created_at": "2025-12-25T10:30:00Z",
                "updated_at": "2025-12-25T10:30:00Z"
            }
        }
```

### Field Type Mappings

| Python Type (SQLModel) | PostgreSQL Type | Example Value |
|------------------------|-----------------|---------------|
| `int` | INTEGER (SERIAL) | `1`, `42`, `99999` |
| `str` | VARCHAR(n) or TEXT | `"Buy groceries"`, `"Long description..."` |
| `bool` | BOOLEAN | `True`, `False` |
| `list[str]` (JSONB) | JSONB | `["work", "urgent"]`, `[]` |
| `datetime` | TIMESTAMP WITH TIME ZONE | `datetime(2025, 12, 25, 10, 30, 0)` |
| `Optional[T]` | Nullable column | `None` (SQL NULL) |

### Pydantic Validation Benefits

```python
# Validation automatically enforced by SQLModel
task = Task(
    user_id="user-123",
    title="",  # ❌ Validation Error: min_length=1
)

task = Task(
    user_id="user-123",
    title="A" * 201,  # ❌ Validation Error: max_length=200
)

task = Task(
    user_id="user-123",
    title="Buy groceries",
    completed="yes"  # ❌ Validation Error: expected bool, got str
)

# ✅ Valid task
task = Task(
    user_id="user-123",
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False
)
```

---

## 9. Alembic Migration

Alembic is the database migration tool for SQLAlchemy/SQLModel, providing version control for database schema changes.

### Initial Migration Script

**File:** `backend/migrations/versions/001_create_tasks_table.py`

```python
"""Initial schema: Create tasks table

Revision ID: 001_create_tasks_table
Revises:
Create Date: 2025-12-25 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# Revision identifiers
revision = '001_create_tasks_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """
    Upgrade database schema: Create tasks table with all fields and indexes.
    """
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('tags', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurrence', sa.String(20), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_deleted_at', 'tasks', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_tasks_user_deleted', 'tasks', ['user_id', 'deleted_at'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_user_completed', 'tasks', ['user_id', 'completed'])

    # Add CHECK constraints
    op.create_check_constraint(
        'check_title_length',
        'tasks',
        sa.and_(
            sa.func.length(sa.column('title')) >= 1,
            sa.func.length(sa.column('title')) <= 200
        )
    )

    op.create_check_constraint(
        'check_title_not_whitespace',
        'tasks',
        sa.text("title !~ '^\\s*$'")
    )

    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for tasks table
    op.execute("""
        CREATE TRIGGER update_tasks_updated_at
        BEFORE UPDATE ON tasks
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade():
    """
    Downgrade database schema: Drop tasks table and related objects.
    """
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop indexes (automatically dropped with table, but explicit for clarity)
    op.drop_index('idx_tasks_user_completed', table_name='tasks')
    op.drop_index('idx_tasks_completed', table_name='tasks')
    op.drop_index('idx_tasks_user_deleted', table_name='tasks')
    op.drop_index('idx_tasks_deleted_at', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')

    # Drop table (CASCADE drops all dependent objects)
    op.drop_table('tasks')
```

### Running Migrations

```bash
# Initialize Alembic (first time setup)
cd backend
alembic init migrations

# Configure alembic.ini with DATABASE_URL
# Edit migrations/env.py to import SQLModel models

# Create migration (auto-generate from models)
alembic revision --autogenerate -m "Create tasks table"

# Apply migration (upgrade to latest)
alembic upgrade head

# Rollback migration (downgrade one version)
alembic downgrade -1

# View migration history
alembic history

# View current migration version
alembic current
```

---

## 10. Data Validation Rules

### Title Validation

| Rule | Constraint | Error Message | Example |
|------|-----------|---------------|---------|
| **Required** | NOT NULL | "Title is required" | ❌ `title = null` |
| **Min Length** | LENGTH >= 1 | "Title is required" | ❌ `title = ""` |
| **Max Length** | LENGTH <= 200 | "Title must not exceed 200 characters" | ❌ `title = "A" * 201` |
| **Not Whitespace** | `title !~ '^\s*$'` | "Title is required" | ❌ `title = "   "` |
| **Valid** | All checks pass | - | ✅ `title = "Buy groceries"` |

### Description Validation

| Rule | Constraint | Error Message | Example |
|------|-----------|---------------|---------|
| **Optional** | NULLABLE | - | ✅ `description = null` |
| **Unlimited Length** | TEXT type | - | ✅ 10,000 character description |
| **Empty String** | Allowed | - | ✅ `description = ""` |

### user_id Validation

| Rule | Constraint | Error Message | Example |
|------|-----------|---------------|---------|
| **Required** | NOT NULL | "Invalid token: missing user_id" | ❌ `user_id = null` |
| **From JWT** | Extracted from token | "Invalid or expired token" | ❌ User-provided user_id |
| **UUID Format** | String (no validation) | - | ✅ `"550e8400-e29b-41d4-a716-446655440000"` |

### Soft Delete Validation

| Rule | Constraint | Query Filter | Example |
|------|-----------|--------------|---------|
| **Active Tasks** | `deleted_at IS NULL` | `WHERE deleted_at IS NULL` | ✅ Show in task list |
| **Deleted Tasks** | `deleted_at IS NOT NULL` | Excluded from queries | ❌ Hidden from list |
| **Delete Operation** | Set `deleted_at = NOW()` | Update, not DELETE | ✅ Soft delete |
| **Cannot Restore** | Phase 2 limitation | - | ⏸️ Restore in Phase 4 |

### Timestamp Validation

| Field | Auto-Set | Auto-Update | User-Editable | Example |
|-------|----------|-------------|---------------|---------|
| `created_at` | ✅ On INSERT | ❌ Never | ❌ No | `2025-12-25T10:30:00Z` |
| `updated_at` | ✅ On INSERT | ✅ On UPDATE | ❌ No | `2025-12-25T14:45:30Z` |
| `deleted_at` | ❌ NULL | ✅ On DELETE | ❌ No | `2025-12-26T09:00:00Z` |

---

## 11. Query Patterns

### Common Queries

#### Get All Tasks for User

```sql
SELECT * FROM tasks
WHERE user_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC;
```

**Usage:** List all active tasks for authenticated user
**Parameters:** `$1` = user_id from JWT token
**Index Used:** `idx_tasks_user_deleted` (composite index)

#### Get Single Task

```sql
SELECT * FROM tasks
WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL;
```

**Usage:** Get task details (ensures user owns task)
**Parameters:** `$1` = task_id, `$2` = user_id from JWT
**Index Used:** `tasks_pkey` (primary key) + user_id check

#### Create Task

```sql
INSERT INTO tasks (user_id, title, description, completed, tags)
VALUES ($1, $2, $3, FALSE, '[]'::jsonb)
RETURNING *;
```

**Usage:** Create new task for user
**Parameters:** `$1` = user_id, `$2` = title, `$3` = description
**Auto-Generated:** `id`, `created_at`, `updated_at`

#### Update Task

```sql
UPDATE tasks
SET title = $1, description = $2
WHERE id = $3 AND user_id = $4 AND deleted_at IS NULL
RETURNING *;
```

**Usage:** Update task title and/or description
**Parameters:** `$1` = new title, `$2` = new description, `$3` = task_id, `$4` = user_id
**Trigger:** `updated_at` automatically refreshed

#### Soft Delete Task

```sql
UPDATE tasks
SET deleted_at = NOW()
WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL
RETURNING *;
```

**Usage:** Soft delete task (mark as deleted, not remove)
**Parameters:** `$1` = task_id, `$2` = user_id
**Result:** Task no longer appears in task list queries

#### Toggle Completion Status

```sql
UPDATE tasks
SET completed = NOT completed
WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL
RETURNING *;
```

**Usage:** Toggle task between complete/incomplete
**Parameters:** `$1` = task_id, `$2` = user_id
**Logic:** `NOT completed` flips boolean (true ↔ false)

#### Filter by Completion Status

```sql
SELECT * FROM tasks
WHERE user_id = $1 AND completed = $2 AND deleted_at IS NULL
ORDER BY created_at DESC;
```

**Usage:** Get active or completed tasks
**Parameters:** `$1` = user_id, `$2` = true (completed) or false (active)
**Index Used:** `idx_tasks_user_completed` (composite index)

### SQLModel Query Examples

#### Get All Tasks (Python)

```python
from sqlmodel import Session, select

def get_user_tasks(session: Session, user_id: str) -> list[Task]:
    """Get all active tasks for user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    ).order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()
    return tasks
```

#### Get Single Task (Python)

```python
def get_task_by_id(session: Session, task_id: int, user_id: str) -> Task | None:
    """Get task by ID (ensures user ownership)."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted_at == None
    )

    task = session.exec(statement).first()
    return task  # Returns None if not found or not owned by user
```

#### Create Task (Python)

```python
def create_task(session: Session, user_id: str, title: str, description: str | None = None) -> Task:
    """Create new task for user."""
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False,
        tags=[]
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

#### Soft Delete Task (Python)

```python
from datetime import datetime

def soft_delete_task(session: Session, task_id: int, user_id: str) -> Task | None:
    """Soft delete task (set deleted_at timestamp)."""
    task = get_task_by_id(session, task_id, user_id)

    if task:
        task.deleted_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

    return task
```

#### Toggle Completion (Python)

```python
def toggle_task_completion(session: Session, task_id: int, user_id: str) -> Task | None:
    """Toggle task completion status."""
    task = get_task_by_id(session, task_id, user_id)

    if task:
        task.completed = not task.completed
        # updated_at automatically refreshed by database trigger
        session.add(task)
        session.commit()
        session.refresh(task)

    return task
```

---

## 12. Database Setup Instructions

### Step 1: Create Neon Account

1. **Sign Up:** Visit [neon.tech](https://neon.tech) and create account
2. **Free Tier:** Neon offers free tier with generous limits:
   - 1 project
   - 10 GB storage
   - 100 hours compute time per month
3. **No Credit Card Required:** Free tier doesn't require payment info

### Step 2: Create Database

1. **Create Project:** In Neon dashboard, create new project
2. **Project Name:** `todo-app-phase2`
3. **Region:** Select closest region (e.g., `us-east-1`)
4. **Database Name:** `todo_db`
5. **PostgreSQL Version:** 15+ (latest stable)

### Step 3: Get Connection String

1. **Navigate to Dashboard:** Go to project settings
2. **Connection String:** Copy connection string in format:
   ```
   postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/todo_db?sslmode=require
   ```
3. **Credentials:** Note username and password (shown once)

### Step 4: Configure Backend Environment

```bash
# backend/.env
DATABASE_URL=postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/todo_db?sslmode=require

# Optional: Database connection pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600
```

### Step 5: Install Dependencies

```bash
cd backend

# Install SQLModel and Alembic
pip install sqlmodel alembic psycopg2-binary

# Or using uv (recommended)
uv pip install sqlmodel alembic psycopg2-binary
```

### Step 6: Initialize Alembic

```bash
# Initialize Alembic migrations
alembic init migrations

# Edit alembic.ini to use DATABASE_URL from .env
# Edit migrations/env.py to import SQLModel models
```

**migrations/env.py:**
```python
from sqlmodel import SQLModel
from backend.models import Task  # Import all models

target_metadata = SQLModel.metadata
```

### Step 7: Create Initial Migration

```bash
# Auto-generate migration from SQLModel models
alembic revision --autogenerate -m "Create tasks table"

# Review generated migration file in migrations/versions/
# Ensure all fields, indexes, and constraints are correct
```

### Step 8: Run Migration

```bash
# Apply migration to database
alembic upgrade head

# Verify tables created in Neon dashboard
```

### Step 9: Test Connection

```python
# backend/test_db.py
from sqlmodel import create_engine, Session, select
from models import Task
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

# Test connection
with Session(engine) as session:
    # Create test task
    task = Task(
        user_id="test-user-123",
        title="Test Task",
        description="Testing database connection"
    )
    session.add(task)
    session.commit()

    # Query task
    statement = select(Task).where(Task.user_id == "test-user-123")
    result = session.exec(statement).first()
    print(f"Task created: {result.title}")

    # Clean up
    session.delete(result)
    session.commit()

print("✅ Database connection successful!")
```

### Environment Variables Reference

```bash
# Required
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Optional (with defaults)
DB_POOL_SIZE=5               # Number of persistent connections
DB_MAX_OVERFLOW=10           # Max connections beyond pool_size
DB_POOL_RECYCLE=3600         # Recycle connections after 1 hour
DB_ECHO_SQL=false            # Log SQL queries (true for debugging)
```

---

## 13. Future Schema Changes (Phase 3+)

### Phase 3: Intermediate Level Features

**Priority Management:**
- ✅ Field already exists: `priority VARCHAR(20)`
- Add validation: Check priority in ('low', 'medium', 'high')
- Add index: `CREATE INDEX idx_tasks_priority ON tasks(priority);`

**Tag Management:**
- ✅ Field already exists: `tags JSONB`
- Add GIN index for tag search: `CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);`
- Add tag filtering queries

**Search & Filter:**
- Add full-text search index on title and description
- Create trigram indexes for fuzzy search
- Add composite indexes for common filter combinations

**Sort Options:**
- Utilize existing indexes (created_at, due_date)
- Add indexes for custom sort orders

### Phase 4: Advanced Level Features

**Recurring Tasks:**
- ✅ Field already exists: `recurrence VARCHAR(20)`
- Add validation: Check recurrence in ('daily', 'weekly', 'monthly')
- Add `next_occurrence` TIMESTAMP field for scheduling
- Create separate `task_occurrences` table for history

**Due Dates & Reminders:**
- ✅ Field already exists: `due_date TIMESTAMP WITH TIME ZONE`
- Add `reminder_at` TIMESTAMP field for notifications
- Create `reminders` table for notification tracking
- Add Kafka event publishing on due date changes

**New Tables:**

**reminders:**
```sql
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

**task_history (Audit Log):**
```sql
CREATE TABLE task_history (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'created', 'updated', 'deleted', 'completed'
    changes JSONB,  -- Before/after values
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Phase 5: Chatbot Integration

**conversations:**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

**messages:**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## 14. Performance Considerations

### Query Optimization

**User Isolation Queries:**
```sql
-- ✅ Good: Uses idx_tasks_user_deleted composite index
SELECT * FROM tasks
WHERE user_id = 'user-123' AND deleted_at IS NULL;

-- ❌ Bad: No user_id filter (full table scan)
SELECT * FROM tasks
WHERE title LIKE '%groceries%';

-- ✅ Better: Add user_id filter
SELECT * FROM tasks
WHERE user_id = 'user-123' AND title LIKE '%groceries%' AND deleted_at IS NULL;
```

**Completion Filtering:**
```sql
-- ✅ Good: Uses idx_tasks_user_completed composite index
SELECT * FROM tasks
WHERE user_id = 'user-123' AND completed = false AND deleted_at IS NULL;

-- ❌ Bad: No indexes for sorting by updated_at with filters
SELECT * FROM tasks
WHERE user_id = 'user-123' AND completed = false AND deleted_at IS NULL
ORDER BY updated_at DESC;

-- ✅ Better: Add composite index (user_id, completed, deleted_at, updated_at)
-- Deferred to Phase 3 when sorting becomes critical
```

### Index Selection Strategy

**Cardinality Considerations:**
- **High Cardinality:** `user_id` (many unique values) → Good for indexing
- **Low Cardinality:** `completed` (only 2 values) → Index still useful for filtering
- **Composite Indexes:** Combine high + low cardinality (e.g., user_id + completed)

**Query Frequency:**
- `user_id` filter: **Every query** → Critical index
- `deleted_at IS NULL` filter: **Every query** → Partial index optimization
- `completed` filter: **Common** → Useful index
- `tags` search: **Phase 3** → Defer GIN index until needed

### Connection Pooling

```python
# backend/db.py
from sqlmodel import create_engine

engine = create_engine(
    database_url,
    pool_size=5,           # 5 persistent connections (good for low traffic)
    max_overflow=10,       # Up to 15 total connections (5 + 10 overflow)
    pool_pre_ping=True,    # Verify connection health before using
    pool_recycle=3600,     # Recycle connections after 1 hour (Neon closes idle)
)
```

**Neon Serverless Considerations:**
- Neon automatically scales compute based on connections
- Connection pooling reduces overhead of creating new connections
- Idle connections are auto-closed after 5 minutes (Neon default)

### N+1 Query Prevention

```python
# ❌ Bad: N+1 query problem (separate query for each task)
tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
for task in tasks:
    # If tasks had relationships, this would trigger N additional queries
    pass

# ✅ Good: Single query (no relationships in Phase 2, but good practice)
tasks = session.exec(
    select(Task).where(Task.user_id == user_id).options(
        # joinedload() would be used here for relationships
    )
).all()
```

---

## 15. Security Considerations

### User Isolation Enforcement

**Critical Rule:** ALL queries MUST filter by `user_id` from JWT token.

```python
# ✅ Correct: User isolation enforced
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),  # From JWT token
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.user_id == user_id,  # ⭐ Critical filter
        Task.deleted_at == None
    )
    return session.exec(statement).all()

# ❌ WRONG: No user isolation (security vulnerability)
@router.get("/api/v1/tasks")
async def get_tasks_INSECURE(session: Session = Depends(get_db)):
    statement = select(Task)  # ❌ Returns ALL users' tasks
    return session.exec(statement).all()
```

### SQL Injection Prevention

**SQLModel/SQLAlchemy Protection:**
- ✅ All queries use parameterized statements (automatic)
- ✅ ORM escapes user input automatically
- ❌ Avoid raw SQL queries without parameterization

```python
# ✅ Safe: Parameterized query
statement = select(Task).where(Task.title == user_input)

# ❌ DANGEROUS: String concatenation (SQL injection risk)
query = f"SELECT * FROM tasks WHERE title = '{user_input}'"  # NEVER DO THIS
```

### Data Exposure Prevention

**404 for Unauthorized Access:**
```python
# ✅ Correct: Return 404 even if task exists (don't reveal existence)
task = get_task_by_id(session, task_id, user_id)
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
return task

# ❌ WRONG: Different errors reveal information
task = session.get(Task, task_id)
if not task:
    raise HTTPException(status_code=404, detail="Task does not exist")
if task.user_id != user_id:
    raise HTTPException(status_code=403, detail="You don't own this task")
# ☝️ Reveals that task exists to unauthorized user
```

### Soft Delete Security

**Exclude Deleted Tasks:**
```python
# ✅ Correct: Exclude soft-deleted tasks from ALL queries
statement = select(Task).where(
    Task.user_id == user_id,
    Task.deleted_at == None  # ⭐ Critical filter
)

# ❌ WRONG: Exposes deleted tasks
statement = select(Task).where(Task.user_id == user_id)
# ☝️ Returns deleted tasks (deleted_at NOT NULL)
```

---

## 16. Testing Strategy

### Database Test Setup

```python
# backend/tests/conftest.py
import pytest
from sqlmodel import create_engine, Session, SQLModel
from backend.models import Task

# In-memory SQLite for fast tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def session(engine):
    """Create test database session."""
    with Session(engine) as session:
        yield session
```

### Test Cases

**User Isolation Test:**
```python
def test_user_cannot_access_other_users_tasks(session):
    """Verify user A cannot access user B's tasks."""
    # Create tasks for two users
    task_a = Task(user_id="user-a", title="Task A", completed=False)
    task_b = Task(user_id="user-b", title="Task B", completed=False)
    session.add_all([task_a, task_b])
    session.commit()

    # Query as user A
    statement = select(Task).where(
        Task.user_id == "user-a",
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()

    # Should only see user A's task
    assert len(tasks) == 1
    assert tasks[0].user_id == "user-a"
    assert task_b not in tasks
```

**Soft Delete Test:**
```python
def test_soft_deleted_tasks_not_returned(session):
    """Verify soft-deleted tasks are excluded from queries."""
    # Create active task
    task = Task(user_id="user-123", title="Task", completed=False)
    session.add(task)
    session.commit()

    # Soft delete task
    task.deleted_at = datetime.utcnow()
    session.add(task)
    session.commit()

    # Query should return empty
    statement = select(Task).where(
        Task.user_id == "user-123",
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()

    assert len(tasks) == 0
```

**Title Validation Test:**
```python
def test_title_validation():
    """Verify title validation constraints."""
    # Valid task
    task = Task(user_id="user-123", title="Valid Title", completed=False)
    assert task.title == "Valid Title"

    # Invalid: Empty title
    with pytest.raises(ValidationError):
        Task(user_id="user-123", title="", completed=False)

    # Invalid: Title too long
    with pytest.raises(ValidationError):
        Task(user_id="user-123", title="A" * 201, completed=False)

    # Invalid: Whitespace-only title
    with pytest.raises(ValidationError):
        Task(user_id="user-123", title="   ", completed=False)
```

---

## 17. Monitoring and Maintenance

### Query Performance Monitoring

```sql
-- Find slow queries (PostgreSQL)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE '%_pkey';
```

### Database Maintenance

```sql
-- Vacuum tasks table (reclaim storage, update statistics)
VACUUM ANALYZE tasks;

-- Reindex tasks table (rebuild indexes)
REINDEX TABLE tasks;

-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('tasks')) AS table_size;

-- Check index sizes
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND tablename = 'tasks';
```

---

## Summary

This database schema specification provides:

1. **Complete PostgreSQL Schema** for Phase 2 Basic Level features
2. **User Isolation Architecture** with JWT-based authentication
3. **Soft Delete Pattern** for non-destructive task deletion
4. **SQLModel Integration** for type-safe database operations
5. **Alembic Migrations** for version-controlled schema changes
6. **Performance Indexes** for fast multi-user queries
7. **Security Guidelines** for user data isolation
8. **Testing Strategy** for database validation
9. **Future Extensibility** for Phase 3+ features

**Key Takeaways:**
- NO users table in backend (managed by Better Auth)
- `user_id` extracted from JWT tokens (stateless authentication)
- ALL queries filter by `user_id` AND `deleted_at IS NULL`
- Soft deletes preserve data for potential restore (Phase 4)
- Phase 2 fields (priority, tags, due_date, recurrence) exist but unused
- Strategic indexes optimize user isolation and completion filtering
- SQLModel provides Pydantic validation + SQLAlchemy ORM

**Next Steps:**
1. Set up Neon database and get connection string
2. Configure backend `.env` with `DATABASE_URL`
3. Run Alembic migration to create tasks table
4. Implement FastAPI routes using SQLModel queries
5. Test user isolation and soft delete behavior
6. Deploy backend to Vercel/Railway with Neon database

---

**Document Version:** 1.0
**Last Updated:** 2025-12-25
**Status:** ✅ Ready for Implementation
