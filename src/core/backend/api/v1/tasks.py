"""
Task CRUD API Endpoints

RESTful API for task management with user isolation and soft delete.

Endpoints:
    POST   /api/v1/tasks       - Create a new task
    GET    /api/v1/tasks       - List all user's tasks (excluding deleted)
    GET    /api/v1/tasks/{id}  - Get a single task by ID
    PUT    /api/v1/tasks/{id}  - Update a task
    DELETE /api/v1/tasks/{id}  - Soft delete a task
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from dependencies import get_current_user, get_db
from models import Task, TaskCreate, TaskPublic, TaskUpdate

router = APIRouter(prefix="/api/v1", tags=["tasks"])


# ===========================
# CREATE
# ===========================


@router.post("/tasks", response_model=TaskPublic, status_code=201)
def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Task:
    """
    Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title, description, completed)
        user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        Created task with all fields

    Raises:
        422: Validation error (missing title, title too long, etc.)
    """
    # Create task with user_id from JWT token
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# ===========================
# READ LIST
# ===========================


@router.get("/tasks", response_model=list[TaskPublic])
def list_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[Task]:
    """
    List all active tasks for the authenticated user.

    Filters:
        - user_id = authenticated user (user isolation)
        - deleted_at IS NULL (exclude soft-deleted tasks)

    Args:
        user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        List of tasks (may be empty)
    """
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None,  # noqa: E711 (SQLModel requires == None)
    )

    tasks = session.exec(statement).all()
    return list(tasks)


# ===========================
# READ SINGLE
# ===========================


@router.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Task:
    """
    Get a single task by ID.

    Enforces user isolation: users can only access their own tasks.

    Args:
        task_id: Task ID to retrieve
        user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        Task with matching ID and user_id

    Raises:
        404: Task not found, deleted, or belongs to different user
    """
    task = get_user_task(task_id, user_id, session)
    return task


# ===========================
# UPDATE
# ===========================


@router.put("/tasks/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Task:
    """
    Update a task's fields.

    Supports partial updates (only provided fields are updated).
    Automatically refreshes updated_at timestamp.

    Args:
        task_id: Task ID to update
        task_update: Fields to update (all optional)
        user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        Updated task

    Raises:
        404: Task not found, deleted, or belongs to different user
        422: Validation error (empty title, title too long, etc.)
    """
    task = get_user_task(task_id, user_id, session)

    # Update only provided fields (partial update)
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # Refresh updated_at timestamp (trigger will handle this in DB)
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# ===========================
# DELETE
# ===========================


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """
    Soft delete a task.

    Sets deleted_at timestamp instead of removing from database.
    Deleted tasks are excluded from list queries.

    Args:
        task_id: Task ID to delete
        user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        None (204 No Content)

    Raises:
        404: Task not found, already deleted, or belongs to different user
    """
    task = get_user_task(task_id, user_id, session)

    # Soft delete: set deleted_at timestamp
    task.deleted_at = datetime.utcnow()

    session.add(task)
    session.commit()

    # Return 204 No Content (no response body)
    return None


# ===========================
# HELPER FUNCTIONS
# ===========================


def get_user_task(task_id: int, user_id: str, session: Session) -> Task:
    """
    Get a task by ID with user isolation and soft delete filtering.

    This helper function is used by GET, PUT, and DELETE endpoints
    to ensure users can only access their own active tasks.

    Args:
        task_id: Task ID to retrieve
        user_id: Authenticated user ID (for isolation)
        session: Database session

    Returns:
        Task if found and owned by user

    Raises:
        404: Task not found, deleted, or belongs to different user
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted_at == None,  # noqa: E711
    )

    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task
