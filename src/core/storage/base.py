"""
ITaskStorage Interface - Abstract base class for task storage.

This interface defines the contract that all storage implementations must follow.
Supports future evolution from in-memory (Phase 1) to database (Phase 2+).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models import Task


class ITaskStorage(ABC):
    """
    Abstract interface for task storage.

    Implementations:
    - Phase 1: MemoryStorage (dict-based, in-memory)
    - Phase 2+: DatabaseStorage (SQLModel + Neon PostgreSQL)

    All implementations MUST:
    1. Assign unique IDs to tasks (sequential, never reused)
    2. Set created_at on create()
    3. Update updated_at on update()
    4. Return None if task not found (not raise exception in get())
    5. Sort by created_at descending (newest first) in list_all()
    """

    @abstractmethod
    def create(self, task: Task) -> Task:
        """
        Create a new task and assign a unique ID.

        Args:
            task: Task instance (id should be None)

        Returns:
            Task with assigned id, created_at, and updated_at

        Post-conditions:
            - task.id is set to unique integer (sequential, never reused)
            - task.created_at is set to current time
            - task.updated_at is set to current time
        """
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task if found, None otherwise

        Note:
            Does NOT raise exception if task not found (returns None)
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Task]:
        """
        Retrieve all tasks sorted by created_at descending (newest first).

        Returns:
            List of all tasks (empty list if none)
            Sorted by created_at descending per spec clarification

        Note:
            Default sort order: created_at descending (newest first)
        """
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """
        Update an existing task.

        Args:
            task: Task instance with id set

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task.id does not exist
            ValueError: If task.id is None

        Post-conditions:
            - task.updated_at is set to current time
        """
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task was deleted, False if task not found

        Post-conditions:
            - task_id is NOT reused for future tasks (critical requirement)
        """
        pass
