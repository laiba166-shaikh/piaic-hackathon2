"""
MemoryStorage - In-memory implementation of ITaskStorage for Phase 1.

This implementation uses a Python dict for storage and maintains a sequential
counter for task IDs that never reuses deleted IDs.
"""
from datetime import datetime
from typing import Dict, List, Optional
from src.core.models import Task
from src.core.storage.base import ITaskStorage
from src.core.exceptions import TaskNotFoundError


class MemoryStorage(ITaskStorage):
    """
    In-memory task storage using Python dict.

    Phase 1 Implementation:
    - Uses dict for fast O(1) lookups
    - Maintains sequential counter that never reuses IDs
    - Data is lost when application exits (no persistence)

    Thread Safety:
    - Not thread-safe (single-user CLI application)
    - Phase 2+ will add locking for multi-user web app
    """

    def __init__(self) -> None:
        """Initialize empty storage with counter starting at 0"""
        self._counter: int = 0
        self._tasks: Dict[int, Task] = {}

    def create(self, task: Task) -> Task:
        """
        Create a new task and assign a unique sequential ID.

        Args:
            task: Task instance (id should be None)

        Returns:
            Task with assigned id, created_at, and updated_at

        Implementation:
            - Increments counter to get next ID
            - Sets created_at and updated_at to current time
            - Stores task in internal dict
            - Never reuses IDs (counter only increments)
        """
        # Increment counter to get next ID (starts at 1)
        self._counter += 1
        task.id = self._counter

        # Set timestamps
        now = datetime.now()
        task.created_at = now
        task.updated_at = now

        # Store in dict
        self._tasks[task.id] = task

        return task

    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task if found, None otherwise

        Note:
            Returns None instead of raising exception (per interface contract)
        """
        return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        """
        Retrieve all tasks sorted by created_at descending (newest first).

        Returns:
            List of all tasks sorted by created_at descending

        Implementation:
            - Converts dict values to list
            - Sorts by created_at in descending order (newest first)
            - Returns empty list if no tasks
        """
        tasks = list(self._tasks.values())

        # Sort by created_at descending (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks

    def update(self, task: Task) -> Task:
        """
        Update an existing task.

        Args:
            task: Task instance with id set

        Returns:
            Updated task

        Raises:
            ValueError: If task.id is None
            TaskNotFoundError: If task.id does not exist

        Implementation:
            - Validates task.id is not None
            - Checks task exists
            - Updates updated_at timestamp
            - Stores updated task in dict
        """
        # Validate task has an ID
        if task.id is None:
            raise ValueError("Task ID cannot be None")

        # Check if task exists
        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)

        # Update timestamp
        task.updated_at = datetime.now()

        # Store updated task
        self._tasks[task.id] = task

        return task

    def delete(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task was deleted, False if task not found

        Implementation:
            - Removes task from dict if exists
            - Does NOT decrement counter (IDs never reused)
            - Returns False if task doesn't exist
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True

        return False
