"""Unit tests for TaskService business logic"""
from datetime import datetime
import pytest
from unittest.mock import Mock, MagicMock
from src.core.models import Task, Priority
from src.core.storage.base import ITaskStorage
from src.core.exceptions import ValidationError


class TestTaskServiceCreateTask:
    """Unit tests for TaskService.create_task() method (US1-005)"""

    def test_create_task_with_title_only(self) -> None:
        """Test create_task with title only calls storage.create()"""
        # Import here to avoid circular dependency before implementation
        from src.core.services import TaskService

        # Mock storage
        mock_storage = Mock(spec=ITaskStorage)
        created_task = Task(title="Buy groceries", id=1, created_at=datetime.now(), updated_at=datetime.now())
        mock_storage.create.return_value = created_task

        # Create service
        service = TaskService(mock_storage)

        # Call create_task
        result = service.create_task(title="Buy groceries")

        # Verify storage.create was called
        assert mock_storage.create.called
        call_args = mock_storage.create.call_args[0][0]  # Get the Task object passed
        assert isinstance(call_args, Task)
        assert call_args.title == "Buy groceries"
        assert call_args.description is None
        assert call_args.completed is False

        # Verify result
        assert result == created_task
        assert result.id == 1

    def test_create_task_with_title_and_description(self) -> None:
        """Test create_task with title and description"""
        from src.core.services import TaskService

        # Mock storage
        mock_storage = Mock(spec=ITaskStorage)
        created_task = Task(
            title="Call dentist",
            description="Schedule annual checkup",
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_storage.create.return_value = created_task

        # Create service
        service = TaskService(mock_storage)

        # Call create_task
        result = service.create_task(title="Call dentist", description="Schedule annual checkup")

        # Verify storage.create was called with correct Task
        assert mock_storage.create.called
        call_args = mock_storage.create.call_args[0][0]
        assert call_args.title == "Call dentist"
        assert call_args.description == "Schedule annual checkup"

        # Verify result
        assert result.title == "Call dentist"
        assert result.description == "Schedule annual checkup"

    def test_create_task_validates_empty_title(self) -> None:
        """Test create_task raises ValidationError for empty title (FR-007)"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        service = TaskService(mock_storage)

        # Empty string should raise ValidationError
        with pytest.raises(ValueError, match="Title cannot be empty"):
            service.create_task(title="")

        # Whitespace-only should raise ValidationError
        with pytest.raises(ValueError, match="Title cannot be empty"):
            service.create_task(title="   ")

        # Storage should not be called
        assert not mock_storage.create.called

    def test_create_task_sets_default_values(self) -> None:
        """Test create_task sets correct default values"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        created_task = Task(title="Test", id=1, created_at=datetime.now(), updated_at=datetime.now())
        mock_storage.create.return_value = created_task

        service = TaskService(mock_storage)
        service.create_task(title="Test")

        # Verify Task object has correct defaults
        call_args = mock_storage.create.call_args[0][0]
        assert call_args.completed is False
        assert call_args.priority == Priority.MEDIUM
        assert call_args.tags == []
        assert call_args.recurrence.value == "none"

    def test_create_task_returns_task_with_assigned_id(self) -> None:
        """Test create_task returns task with ID assigned by storage"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)

        # Storage should assign ID
        created_task = Task(title="Test", id=42, created_at=datetime.now(), updated_at=datetime.now())
        mock_storage.create.return_value = created_task

        service = TaskService(mock_storage)
        result = service.create_task(title="Test")

        # Returned task should have the ID assigned by storage
        assert result.id == 42


class TestTaskServiceListAll:
    """Unit tests for TaskService.list_all() method (US2-005)"""

    def test_list_all_returns_all_tasks(self) -> None:
        """Test list_all returns all tasks from storage"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Task 1", id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task 2", id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task 3", id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        # Create service and call list_all
        service = TaskService(mock_storage)
        result = service.list_all()

        # Verify storage.list_all was called
        assert mock_storage.list_all.called

        # Verify correct tasks returned
        assert result == tasks
        assert len(result) == 3

    def test_list_all_returns_empty_list_when_no_tasks(self) -> None:
        """Test list_all returns empty list when storage has no tasks"""
        from src.core.services import TaskService

        # Mock storage with no tasks
        mock_storage = Mock(spec=ITaskStorage)
        mock_storage.list_all.return_value = []

        # Create service and call list_all
        service = TaskService(mock_storage)
        result = service.list_all()

        # Verify empty list returned
        assert result == []
        assert len(result) == 0

    def test_list_all_returns_tasks_sorted_by_created_at_descending(self) -> None:
        """Test list_all returns tasks sorted by created_at descending (newest first)"""
        from src.core.services import TaskService
        import time

        # Mock storage with tasks in specific order
        mock_storage = Mock(spec=ITaskStorage)

        # Create tasks with different timestamps
        now = datetime.now()
        task1 = Task(title="Old task", id=1, created_at=now, updated_at=now)
        time.sleep(0.001)
        task2 = Task(title="Middle task", id=2, created_at=datetime.now(), updated_at=datetime.now())
        time.sleep(0.001)
        task3 = Task(title="New task", id=3, created_at=datetime.now(), updated_at=datetime.now())

        # Storage returns tasks sorted (newest first per FR-020a)
        mock_storage.list_all.return_value = [task3, task2, task1]

        # Create service and call list_all
        service = TaskService(mock_storage)
        result = service.list_all()

        # Verify tasks are in correct order (newest first)
        assert result[0].title == "New task"
        assert result[1].title == "Middle task"
        assert result[2].title == "Old task"
