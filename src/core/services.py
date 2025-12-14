"""
TaskService - Business logic layer for task management.

This service provides the core business logic for task operations:
- Creating tasks with validation
- Updating tasks
- Deleting tasks
- Querying tasks

Phase 1: Basic CRUD operations for in-memory storage
Phase 2+: Enhanced with persistence, advanced features
"""
from typing import Optional
from src.core.models import Task
from src.core.storage.base import ITaskStorage
from src.config import get_logger

logger = get_logger(__name__)


class TaskService:
    """
    Service layer for task management operations.

    Responsibilities:
    - Input validation
    - Business logic enforcement
    - Coordinating with storage layer
    - Logging operations
    """

    def __init__(self, storage: ITaskStorage) -> None:
        """
        Initialize TaskService with a storage backend.

        Args:
            storage: Storage implementation (MemoryStorage, DatabaseStorage, etc.)
        """
        self._storage = storage
        logger.debug(f"TaskService initialized with storage: {type(storage).__name__}")

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
    ) -> Task:
        """
        Create a new task with validation.

        Args:
            title: Task title (required, 1-200 chars)
            description: Optional task description (max 500 chars)

        Returns:
            Created task with assigned ID and timestamps

        Raises:
            ValueError: If title is empty or whitespace-only

        Business Rules:
            - Title must not be empty (FR-007)
            - Title max 200 characters (enforced by Task model)
            - Description max 500 characters (enforced by Task model)
            - Tasks start as incomplete (completed=False)
            - Default priority is MEDIUM
        """
        # Validate title is not empty or whitespace-only
        if not title or not title.strip():
            logger.warning("Attempted to create task with empty title")
            raise ValueError("Title cannot be empty")

        # Create Task object (model will validate constraints)
        task = Task(
            title=title,
            description=description,
        )

        # Persist to storage (storage assigns ID and timestamps)
        created_task = self._storage.create(task)

        logger.info(f"Created task ID {created_task.id}: {created_task.title}")
        return created_task

    def list_all(self) -> list[Task]:
        """
        Retrieve all tasks sorted by creation date (newest first).

        Returns:
            List of all tasks, sorted by created_at descending (newest first)

        Business Rules:
            - Default sort order: created_at descending (FR-020a)
            - Storage layer handles the sorting
            - Returns empty list if no tasks exist
        """
        tasks = self._storage.list_all()
        logger.debug(f"Retrieved {len(tasks)} tasks from storage")
        return tasks

    def mark_complete(self, task_id: int) -> Task:
        """
        Mark a task as complete.

        Args:
            task_id: The ID of the task to mark complete

        Returns:
            Updated task with completed=True

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist

        Business Rules:
            - Sets task.completed to True
            - Updates task.updated_at timestamp
            - Idempotent - marking already completed task succeeds
        """
        from src.core.exceptions import TaskNotFoundError

        # Retrieve task from storage
        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to mark nonexistent task {task_id} as complete")
            raise TaskNotFoundError(task_id)

        # Update task status
        task.completed = True

        # Persist changes
        self._storage.update(task)

        logger.info(f"Marked task ID {task_id} as complete")
        return task

    def mark_incomplete(self, task_id: int) -> Task:
        """
        Mark a task as incomplete.

        Args:
            task_id: The ID of the task to mark incomplete

        Returns:
            Updated task with completed=False

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist

        Business Rules:
            - Sets task.completed to False
            - Updates task.updated_at timestamp
            - Idempotent - marking already incomplete task succeeds
        """
        from src.core.exceptions import TaskNotFoundError

        # Retrieve task from storage
        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to mark nonexistent task {task_id} as incomplete")
            raise TaskNotFoundError(task_id)

        # Update task status
        task.completed = False

        # Persist changes
        self._storage.update(task)

        logger.info(f"Marked task ID {task_id} as incomplete")
        return task

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Task:
        """
        Update task title and/or description.

        Args:
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
            ValueError: If no updates provided or title is empty

        Business Rules:
            - At least one of title or description must be provided
            - Title cannot be empty or whitespace-only
            - Updates task.updated_at timestamp
        """
        from src.core.exceptions import TaskNotFoundError

        # Validate at least one field is being updated
        if title is None and description is None:
            logger.warning("Attempted to update task with no changes")
            raise ValueError("At least one of title or description must be provided")

        # Retrieve task from storage
        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to update nonexistent task {task_id}")
            raise TaskNotFoundError(task_id)

        # Update title if provided
        if title is not None:
            # Validate title is not empty
            if not title or not title.strip():
                logger.warning(f"Attempted to update task {task_id} with empty title")
                raise ValueError("Title cannot be empty")
            task.title = title

        # Update description if provided
        if description is not None:
            task.description = description

        # Persist changes
        self._storage.update(task)

        logger.info(f"Updated task ID {task_id}")
        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if task was deleted, False if task didn't exist

        Business Rules:
            - Returns False if task doesn't exist (no error raised)
            - Permanently removes task from storage
            - Cannot be undone
        """
        # Attempt to delete task from storage
        deleted = self._storage.delete(task_id)

        if deleted:
            logger.info(f"Deleted task ID {task_id}")
        else:
            logger.warning(f"Attempted to delete nonexistent task {task_id}")

        return deleted
