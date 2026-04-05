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
from src.cli.logics.models import Task, Priority, Recurrence
from src.cli.logics.validators import parse_due_date
from src.cli.logics.storage.base import ITaskStorage
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
        if not title or not title.strip():
            logger.warning("Attempted to create task with empty title")
            raise ValueError("Title cannot be empty")

        task = Task(
            title=title,
            description=description,
            priority=priority if priority is not None else Priority.MEDIUM,
            tags=tags if tags is not None else [],
            recurrence=recurrence if recurrence is not None else Recurrence.NONE,
            due_date=due_date,
        )

        created_task = self._storage.create(task)
        logger.info(
            f"Created task ID {created_task.id}: {created_task.title} "
            f"(priority={created_task.priority.value}, tags={created_task.tags})"
        )
        return created_task

    def list_all(self) -> list[Task]:
        tasks = self._storage.list_all()
        logger.debug(f"Retrieved {len(tasks)} tasks from storage")
        return tasks

    def mark_complete(self, task_id: int) -> Task:
        from src.cli.logics.exceptions import TaskNotFoundError

        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to mark nonexistent task {task_id} as complete")
            raise TaskNotFoundError(task_id)

        task.completed = True
        self._storage.update(task)
        logger.info(f"Marked task ID {task_id} as complete")

        if task.recurrence != Recurrence.NONE and task.due_date:
            from src.cli.logics.recurring import calculate_next_occurrence

            next_due = calculate_next_occurrence(task.due_date, task.recurrence)
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
        from src.cli.logics.exceptions import TaskNotFoundError

        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to mark nonexistent task {task_id} as incomplete")
            raise TaskNotFoundError(task_id)

        task.completed = False
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
        from src.cli.logics.exceptions import TaskNotFoundError

        if all(field is None for field in [title, description, priority, tags, recurrence, due_date]):
            logger.warning("Attempted to update task with no changes")
            raise ValueError("At least one field (title, description, priority, tags, recurrence, or due_date) must be provided")

        task = self._storage.get(task_id)
        if task is None:
            logger.warning(f"Attempted to update nonexistent task {task_id}")
            raise TaskNotFoundError(task_id)

        if recurrence is not None and task.completed:
            logger.warning(f"Attempted to update recurrence for completed task {task_id}")
            raise ValueError("Cannot update recurrence for completed task")

        if title is not None:
            if not title or not title.strip():
                logger.warning(f"Attempted to update task {task_id} with empty title")
                raise ValueError("Title cannot be empty")
            task.title = title

        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if tags is not None:
            task.tags = tags
        if recurrence is not None:
            task.recurrence = recurrence
        if due_date is not None:
            task.due_date = due_date

        self._storage.update(task)
        logger.info(f"Updated task ID {task_id}")
        return task

    def delete_task(self, task_id: int) -> bool:
        deleted = self._storage.delete(task_id)
        if deleted:
            logger.info(f"Deleted task ID {task_id}")
        else:
            logger.warning(f"Attempted to delete nonexistent task {task_id}")
        return deleted

    def search_tasks(self, query: str) -> List[Task]:
        if not query or not query.strip():
            logger.warning("Attempted to search with empty query")
            raise ValueError("Search query cannot be empty")

        all_tasks = self._storage.list_all()
        normalized_query = query.lower()

        matching_tasks = []
        for task in all_tasks:
            if normalized_query in task.title.lower():
                matching_tasks.append(task)
                continue
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
        if all(criterion is None for criterion in [priority, completed, tag, overdue]):
            logger.warning("Attempted to filter with no criteria")
            raise ValueError("at least one filter criterion must be provided")

        all_tasks = self._storage.list_all()
        filtered_tasks = []
        for task in all_tasks:
            if priority is not None and task.priority != priority:
                continue
            if completed is not None and task.completed != completed:
                continue
            if tag is not None and tag not in task.tags:
                continue
            if overdue is not None:
                if overdue and not task.is_overdue():
                    continue
                if not overdue and task.is_overdue():
                    continue
            filtered_tasks.append(task)

        logger.info(
            f"Filter (priority={priority}, completed={completed}, tag={tag}, overdue={overdue}) "
            f"returned {len(filtered_tasks)} results"
        )
        return filtered_tasks

    def sort_tasks(self, by: str, ascending: bool = True) -> List[Task]:
        valid_fields = ["priority", "title", "created", "due_date"]
        if by not in valid_fields:
            logger.warning(f"Invalid sort field: {by}")
            raise ValueError(f"Invalid sort field: {by}. Must be one of {valid_fields}")

        all_tasks = self._storage.list_all()
        if not all_tasks:
            return []

        priority_order = {Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}

        if by == "priority":
            sorted_tasks = sorted(all_tasks, key=lambda t: priority_order[t.priority], reverse=ascending)
        elif by == "title":
            sorted_tasks = sorted(all_tasks, key=lambda t: t.title.lower(), reverse=not ascending)
        elif by == "created":
            sorted_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=not ascending)
        elif by == "due_date":
            max_date = datetime.max
            sorted_tasks = sorted(
                all_tasks,
                key=lambda t: t.due_date if t.due_date else max_date,
                reverse=not ascending,
            )

        logger.info(f"Sorted {len(sorted_tasks)} tasks by {by} (ascending={ascending})")
        return sorted_tasks
