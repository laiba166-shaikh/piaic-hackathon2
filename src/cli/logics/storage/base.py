"""
ITaskStorage Interface - Abstract base class for task storage.

This interface defines the contract that all storage implementations must follow.
Supports future evolution from in-memory (Phase 1) to database (Phase 2+).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.cli.logics.models import Task


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
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def list_all(self) -> List[Task]:
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass
