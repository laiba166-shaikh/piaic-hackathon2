"""Core domain models for the Todo application"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class Priority(Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recurrence(Enum):
    """Task recurrence patterns"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 500 characters)
        completed: Task completion status (default: False)
        priority: Task priority level (default: MEDIUM)
        tags: List of tags for categorization (default: empty list)
        due_date: Optional due date with time
        recurrence: Recurrence pattern (default: NONE)
        reminder_minutes: Minutes before due date to remind (must be positive)
        id: Unique task identifier (assigned by storage)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """

    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Recurrence = Recurrence.NONE
    reminder_minutes: Optional[int] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task data after initialization"""
        # Validate title (FR-007, FR-001)
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        if len(self.title) > 200:
            raise ValueError("Title max 200 characters")

        # Validate description (FR-001 clarified)
        if self.description and len(self.description) > 500:
            raise ValueError("Description max 500 characters")

        # Validate reminder (FR-028)
        if self.reminder_minutes is not None and self.reminder_minutes <= 0:
            raise ValueError("Reminder must be positive minutes")

    def is_overdue(self) -> bool:
        """
        Check if task is overdue.

        A task is overdue if:
        - It has a due_date set
        - The due_date is in the past
        - The task is not completed

        Returns:
            True if task is overdue, False otherwise
        """
        if not self.due_date or self.completed:
            return False
        return datetime.now() > self.due_date

    def is_due_today(self) -> bool:
        """
        Check if task is due today.

        A task is due today if:
        - It has a due_date set
        - The due_date is today (same calendar date)
        - The task is not completed

        Returns:
            True if task is due today, False otherwise
        """
        if not self.due_date or self.completed:
            return False
        return self.due_date.date() == datetime.now().date()
