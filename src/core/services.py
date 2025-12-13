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
