"""
MemoryStorage - In-memory implementation of ITaskStorage for Phase 1.

This implementation uses a Python dict for storage and maintains a sequential
counter for task IDs that never reuses deleted IDs.
"""
from datetime import datetime
from typing import Dict, List, Optional
from src.cli.logics.models import Task
from src.cli.logics.storage.base import ITaskStorage
from src.cli.logics.exceptions import TaskNotFoundError


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
        """
        self._counter += 1
        task.id = self._counter

        now = datetime.now()
        task.created_at = now
        task.updated_at = now

        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID. Returns None if not found.
        """
        return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        """
        Retrieve all tasks sorted by created_at descending (newest first).
        """
        tasks = list(self._tasks.values())
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def update(self, task: Task) -> Task:
        """
        Update an existing task.

        Raises:
            ValueError: If task.id is None
            TaskNotFoundError: If task.id does not exist
        """
        if task.id is None:
            raise ValueError("Task ID cannot be None")

        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)

        task.updated_at = datetime.now()
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> bool:
        """
        Delete a task by its ID. Returns True if deleted, False if not found.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
