"""
Task Model

SQLModel definition for tasks with user isolation and soft delete support.
"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    """Base task model with common fields."""

    title: str = Field(max_length=200, min_length=1)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """
    Task database model with full schema.

    This model represents a task in the database with user isolation
    and soft delete support.

    Fields:
        id: Primary key, auto-incremented
        user_id: User who owns this task (from JWT sub claim)
        title: Task title (required, max 200 chars)
        description: Optional task description
        completed: Task completion status (default: False)
        deleted_at: Soft delete timestamp (NULL = active task)
        created_at: Task creation timestamp
        updated_at: Last update timestamp (auto-updated)

    Indexes:
        - user_id (for filtering user's tasks)
        - deleted_at (for filtering active vs deleted)
        - (user_id, deleted_at) composite for common queries

    User Isolation:
        All queries MUST filter by user_id to prevent cross-user access.
    """

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(
        max_length=255,
        nullable=False,
        index=True,
        description="User ID from JWT token (sub claim)",
    )
    deleted_at: datetime | None = Field(
        default=None, index=True, description="Soft delete timestamp"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp",
    )


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.

    Does NOT include user_id (extracted from JWT token).
    Does NOT include id, timestamps, or deleted_at (auto-generated).
    """

    pass


class TaskUpdate(SQLModel):
    """
    Schema for updating an existing task.

    All fields are optional to allow partial updates.
    """

    title: str | None = Field(default=None, max_length=200, min_length=1)
    description: str | None = Field(default=None)
    completed: bool | None = Field(default=None)


class TaskPublic(TaskBase):
    """
    Public task schema returned to clients.

    Includes all fields except deleted_at (internal).
    """

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
