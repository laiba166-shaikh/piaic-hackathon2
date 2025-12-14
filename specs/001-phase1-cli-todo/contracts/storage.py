"""
ITaskStorage Interface Contract

Storage abstraction for Phase 1 (in-memory) and Phase 2+ (database).
All storage implementations MUST comply with this interface.

Contract Tests: tests/contract/test_storage_interface.py

Phase Evolution:
- Phase 1: MemoryStorage (dict-based, in-memory)
- Phase 2+: DatabaseStorage (SQLModel + Neon PostgreSQL)

Date: 2025-12-10
Branch: 001-phase1-cli-todo
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models import Task


class ITaskStorage(ABC):
    """Abstract interface for task storage.

    Contract Requirements (ALL implementations MUST comply):
    1. Assign unique IDs sequentially, NEVER reuse (even after delete)
    2. Set created_at timestamp on create()
    3. Update updated_at timestamp on update()
    4. Return None if task not found (NOT raise exception on get())
    5. Default sort: created_at descending (newest first) in list_all()
    6. Thread-safe operations (Phase 2+ requirement, optional Phase 1)
    """

    @abstractmethod
    def create(self, task: Task) -> Task:
        """Create a new task and assign a unique ID.

        Args:
            task: Task instance (id should be None)

        Returns:
            Task with assigned id, created_at, and updated_at

        Raises:
            ValueError: If task.id is already set (must be None)

        Post-conditions:
            - task.id is set to unique integer (sequential, never reused)
            - task.created_at is set to current time
            - task.updated_at is set to current time

        Example:
            task = Task(title="Buy milk")
            created_task = storage.create(task)
            assert created_task.id == 1  # First task
        """
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task if found, None otherwise (does NOT raise exception)

        Example:
            task = storage.get(1)
            if task:
                print(task.title)
            else:
                print("Task not found")
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Task]:
        """Retrieve all tasks, sorted by created_at descending (newest first).

        Returns:
            List of all tasks (empty list if none exist)

        Note:
            Default sort order per spec clarification: "Created date (newest first)"

        Example:
            tasks = storage.list_all()
            # Task created at 14:00 appears before task created at 13:00
        """
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update an existing task.

        Args:
            task: Task instance with id set

        Returns:
            Updated task with refreshed updated_at timestamp

        Raises:
            TaskNotFoundError: If task.id does not exist in storage
            ValueError: If task.id is None

        Post-conditions:
            - task.updated_at is set to current time
            - All other fields updated to task values

        Example:
            task = storage.get(1)
            task.title = "Updated title"
            updated_task = storage.update(task)
            assert updated_task.updated_at > task.created_at
        """
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task was deleted
            False if task not found (does NOT raise exception)

        Post-conditions:
            - task_id is NEVER reused for future tasks (per spec clarification)
            - Sequential counter continues (e.g., delete ID 3, next is ID 4)

        Example:
            success = storage.delete(1)
            if success:
                print("Task deleted")
                # Next created task will have ID > 1 (never reuse 1)
        """
        pass


# ============================================================================
# Contract Compliance Test Requirements
# ============================================================================
#
# All implementations MUST pass these test cases (tests/contract/test_storage_interface.py):
#
# 1. test_create_assigns_unique_sequential_id()
#    - First task gets ID 1
#    - Second task gets ID 2
#    - IDs never repeat
#
# 2. test_create_sets_timestamps()
#    - created_at is set
#    - updated_at is set
#    - Both are approximately now()
#
# 3. test_get_returns_none_if_not_found()
#    - get(999) returns None (not exception)
#
# 4. test_list_all_returns_newest_first()
#    - Create task A at time T1
#    - Create task B at time T2 (T2 > T1)
#    - list_all() returns [B, A]
#
# 5. test_update_sets_updated_at()
#    - updated_at is newer after update()
#
# 6. test_delete_does_not_reuse_id()
#    - Create task (ID 1)
#    - Delete task (ID 1)
#    - Create new task → ID is 2 (not 1)
#
# 7. test_delete_nonexistent_returns_false()
#    - delete(999) returns False (not exception)
#
# 8. test_update_nonexistent_raises_error()
#    - update(task with id=999) raises TaskNotFoundError
#
# Phase 2+ only:
# 9. test_thread_safety()
#    - Concurrent creates from multiple threads
#    - All get unique IDs
#    - No race conditions
