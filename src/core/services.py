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
from datetime import datetime
from typing import Optional, List
from src.core.models import Task, Priority, Recurrence
from src.core.validators import parse_due_date
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
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        recurrence: Optional[Recurrence] = None,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """
        Create a new task with validation.

        Args:
            title: Task title (required, 1-200 chars)
            description: Optional task description (max 500 chars)
            priority: Task priority (HIGH, MEDIUM, LOW), defaults to MEDIUM
            tags: List of tags/categories for the task
            recurrence: Recurrence pattern (NONE, DAILY, WEEKLY, MONTHLY), defaults to NONE
            due_date: Optional due date for the task

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
            - Tags default to empty list
            - Default recurrence is NONE
        """
        # Validate title is not empty or whitespace-only
        if not title or not title.strip():
            logger.warning("Attempted to create task with empty title")
            raise ValueError("Title cannot be empty")

        # Create Task object (model will validate constraints)
        task = Task(
            title=title,
            description=description,
            priority=priority if priority is not None else Priority.MEDIUM,
            tags=tags if tags is not None else [],
            recurrence=recurrence if recurrence is not None else Recurrence.NONE,
            due_date=due_date,
        )

        # Persist to storage (storage assigns ID and timestamps)
        created_task = self._storage.create(task)

        logger.info(
            f"Created task ID {created_task.id}: {created_task.title} "
            f"(priority={created_task.priority.value}, tags={created_task.tags})"
        )
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
            - For recurring tasks: creates a new task instance with next due date
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

        # Handle recurring tasks: create next instance
        if task.recurrence != Recurrence.NONE and task.due_date:
            from src.core.recurring import calculate_next_occurrence

            next_due = calculate_next_occurrence(task.due_date, task.recurrence)

            # Create new task with same properties but new due date
            new_task = Task(
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags.copy() if task.tags else [],
                due_date=next_due,
                recurrence=task.recurrence,
            )
            created_task = self._storage.create(new_task)
            logger.info(
                f"Created recurring task ID {created_task.id} from completed task {task_id} "
                f"(next due: {next_due})"
            )

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
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        recurrence: Optional[Recurrence] = None,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """
        Update task title, description, priority, tags, recurrence, and/or due_date.

        Args:
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority level (optional)
            tags: New tags list (optional)
            recurrence: New recurrence pattern (optional, only for incomplete tasks)
            due_date: New due date (optional)

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
            ValueError: If no updates provided, title is empty, or recurrence update on completed task

        Business Rules:
            - At least one field must be provided for update
            - Title cannot be empty or whitespace-only
            - Recurrence can only be updated for incomplete tasks
            - Updates task.updated_at timestamp
        """
        from src.core.exceptions import TaskNotFoundError

        # Validate at least one field is being updated
        if all(field is None for field in [title, description, priority, tags, recurrence, due_date]):
            logger.warning("Attempted to update task with no changes")
            raise ValueError("At least one field (title, description, priority, tags, recurrence, or due_date) must be provided")

        # Retrieve task from storage
        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to update nonexistent task {task_id}")
            raise TaskNotFoundError(task_id)

        # Validate recurrence update is only for incomplete tasks
        if recurrence is not None and task.completed:
            logger.warning(f"Attempted to update recurrence for completed task {task_id}")
            raise ValueError("Cannot update recurrence for completed task")

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

        # Update priority if provided
        if priority is not None:
            task.priority = priority

        # Update tags if provided
        if tags is not None:
            task.tags = tags

        # Update recurrence if provided
        if recurrence is not None:
            task.recurrence = recurrence

        # Update due_date if provided
        if due_date is not None:
            task.due_date = due_date

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

    def search_tasks(self, query: str) -> List[Task]:
        """
        Search for tasks by keyword in title or description.

        Args:
            query: Search keyword (case-insensitive)

        Returns:
            List of tasks matching the search query

        Raises:
            ValueError: If query is empty or whitespace-only

        Business Rules:
            - Case-insensitive substring matching (FR-017)
            - Searches both title and description fields
            - Returns empty list if no matches found
            - Query cannot be empty or whitespace-only
        """
        # Validate query is not empty
        if not query or not query.strip():
            logger.warning("Attempted to search with empty query")
            raise ValueError("Search query cannot be empty")

        # Get all tasks from storage
        all_tasks = self._storage.list_all()

        # Normalize query for case-insensitive matching
        normalized_query = query.lower()

        # Filter tasks by keyword in title or description
        matching_tasks = []
        for task in all_tasks:
            # Check title
            if normalized_query in task.title.lower():
                matching_tasks.append(task)
                continue

            # Check description if present
            if task.description and normalized_query in task.description.lower():
                matching_tasks.append(task)

        logger.info(f"Search for '{query}' returned {len(matching_tasks)} results")
        return matching_tasks

    def filter_tasks(
        self,
        priority: Optional[Priority] = None,
        completed: Optional[bool] = None,
        tag: Optional[str] = None,
        overdue: Optional[bool] = None,
    ) -> List[Task]:
        """
        Filter tasks by criteria (priority, status, tags, overdue).

        Args:
            priority: Filter by priority level (HIGH, MEDIUM, LOW)
            completed: Filter by completion status (True/False)
            tag: Filter by tag (tasks must have this tag)
            overdue: Filter by overdue status (True for overdue tasks, False for not overdue)

        Returns:
            List of tasks matching ALL provided filter criteria (AND logic)

        Raises:
            ValueError: If no filter criteria provided

        Business Rules:
            - At least one filter criterion must be provided (FR-019)
            - Multiple criteria are combined with AND logic
            - Returns empty list if no matches found
            - Tag matching is case-sensitive exact match
            - Overdue: task.is_overdue() for True, not task.is_overdue() for False
        """
        # Validate at least one filter criterion is provided
        if all(criterion is None for criterion in [priority, completed, tag, overdue]):
            logger.warning("Attempted to filter with no criteria")
            raise ValueError("at least one filter criterion must be provided")

        # Get all tasks from storage
        all_tasks = self._storage.list_all()

        # Apply filters (AND logic)
        filtered_tasks = []
        for task in all_tasks:
            # Check priority filter
            if priority is not None and task.priority != priority:
                continue

            # Check completed status filter
            if completed is not None and task.completed != completed:
                continue

            # Check tag filter
            if tag is not None and tag not in task.tags:
                continue

            # Check overdue filter
            if overdue is not None:
                if overdue and not task.is_overdue():
                    continue
                if not overdue and task.is_overdue():
                    continue

            # Task passed all filters
            filtered_tasks.append(task)

        logger.info(
            f"Filter (priority={priority}, completed={completed}, tag={tag}, overdue={overdue}) "
            f"returned {len(filtered_tasks)} results"
        )
        return filtered_tasks

    def sort_tasks(self, by: str, ascending: bool = True) -> List[Task]:
        """
        Sort tasks by specified field.

        Args:
            by: Field to sort by ('priority', 'title', 'created', 'due_date')
            ascending: Sort order (True for ascending, False for descending)

        Returns:
            List of tasks sorted by specified field

        Raises:
            ValueError: If invalid sort field provided

        Business Rules:
            - Priority order: HIGH (1) > MEDIUM (2) > LOW (3)
            - For priority descending: HIGH first, LOW last
            - For priority ascending: LOW first, HIGH last
            - Title: alphabetical (case-insensitive)
            - Created/due_date: chronological order
            - Tasks without due_date appear at end when sorting by due_date
        """
        # Validate sort field
        valid_fields = ["priority", "title", "created", "due_date"]
        if by not in valid_fields:
            logger.warning(f"Invalid sort field: {by}")
            raise ValueError(f"Invalid sort field: {by}. Must be one of {valid_fields}")

        # Get all tasks from storage
        all_tasks = self._storage.list_all()

        if not all_tasks:
            return []

        # Define sort key functions
        # Priority values: HIGH=1, MEDIUM=2, LOW=3 for natural ordering
        priority_order = {Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}

        if by == "priority":
            # Sort by priority
            # ascending=True: LOW (3) -> MEDIUM (2) -> HIGH (1) needs reverse=False on priority_order
            # ascending=False (desc): HIGH (1) -> MEDIUM (2) -> LOW (3) needs reverse=False on priority_order
            # Since HIGH=1 is smallest, default sorted() puts HIGH first
            # For descending (HIGH first), we don't reverse
            # For ascending (LOW first), we reverse
            sorted_tasks = sorted(
                all_tasks,
                key=lambda t: priority_order[t.priority],
                reverse=ascending,  # reverse=True when ascending (to get LOW first)
            )
        elif by == "title":
            # Sort alphabetically (case-insensitive)
            # ascending=True: A-Z (default sorted)
            # ascending=False (desc): Z-A (reversed)
            sorted_tasks = sorted(
                all_tasks,
                key=lambda t: t.title.lower(),
                reverse=not ascending,
            )
        elif by == "created":
            # Sort by created_at timestamp
            # ascending=True: oldest first (default sorted)
            # ascending=False (desc): newest first (reversed)
            sorted_tasks = sorted(
                all_tasks,
                key=lambda t: t.created_at,
                reverse=not ascending,
            )
        elif by == "due_date":
            # Sort by due_date, tasks without due_date at end
            # Use max datetime for None values
            max_date = datetime.max
            sorted_tasks = sorted(
                all_tasks,
                key=lambda t: t.due_date if t.due_date else max_date,
                reverse=not ascending,
            )

        logger.info(f"Sorted {len(sorted_tasks)} tasks by {by} (ascending={ascending})")
        return sorted_tasks
