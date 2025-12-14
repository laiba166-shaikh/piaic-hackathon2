"""Unit tests for search and filter functionality"""
import pytest
from datetime import datetime
from unittest.mock import Mock
from src.core.models import Task, Priority
from src.core.storage.base import ITaskStorage


class TestSearchTasks:
    """Unit tests for TaskService.search_tasks() method (US7-005)"""

    def test_search_tasks_matches_title_case_insensitive(self) -> None:
        """Test search_tasks matches keyword in title (case-insensitive)"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Team MEETING", id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Project review", id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="meeting notes", id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Search for "meeting" (lowercase)
        results = service.search_tasks("meeting")

        # Should find tasks with "meeting" in title (case-insensitive)
        assert len(results) == 2
        assert results[0].title == "Team MEETING"
        assert results[1].title == "meeting notes"

    def test_search_tasks_matches_description_case_insensitive(self) -> None:
        """Test search_tasks matches keyword in description (case-insensitive)"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(
                title="Task A",
                description="Discuss MEETING agenda",
                id=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Task(
                title="Task B", description="Review code", id=2, created_at=datetime.now(), updated_at=datetime.now()
            ),
            Task(
                title="Task C",
                description="Plan next meeting",
                id=3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Search for "meeting" (lowercase)
        results = service.search_tasks("meeting")

        # Should find tasks with "meeting" in description (case-insensitive)
        assert len(results) == 2
        assert results[0].title == "Task A"
        assert results[1].title == "Task C"

    def test_search_tasks_matches_title_or_description(self) -> None:
        """Test search_tasks matches keyword in either title or description"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Meeting prep", id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(
                title="Task B",
                description="Schedule meeting",
                id=2,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Task(title="Unrelated task", id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Search for "meeting"
        results = service.search_tasks("meeting")

        # Should find tasks with "meeting" in title OR description
        assert len(results) == 2
        assert results[0].title == "Meeting prep"
        assert results[1].title == "Task B"

    def test_search_tasks_returns_empty_list_when_no_matches(self) -> None:
        """Test search_tasks returns empty list when no tasks match"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Task 1", id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task 2", id=2, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Search for non-existent keyword
        results = service.search_tasks("nonexistent")

        # Should return empty list
        assert results == []

    def test_search_tasks_raises_error_for_empty_query(self) -> None:
        """Test search_tasks raises ValueError for empty query"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        service = TaskService(mock_storage)

        # Should raise ValueError for empty query
        with pytest.raises(ValueError, match="empty"):
            service.search_tasks("")

        # Should raise ValueError for whitespace-only query
        with pytest.raises(ValueError, match="empty"):
            service.search_tasks("   ")

    def test_search_tasks_substring_matching(self) -> None:
        """Test search_tasks does substring matching"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Implementation meeting", id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Meet the team", id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Unrelated task", id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Search for "meet" (should match "meeting" and "Meet")
        results = service.search_tasks("meet")

        # Should find tasks with "meet" as substring
        assert len(results) == 2
        assert results[0].title == "Implementation meeting"
        assert results[1].title == "Meet the team"


class TestFilterTasks:
    """Unit tests for TaskService.filter_tasks() method (US8-007)"""

    def test_filter_tasks_by_priority(self) -> None:
        """Test filter_tasks filters by priority"""
        from src.core.services import TaskService

        # Mock storage with tasks of different priorities
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="High task 1", priority=Priority.HIGH, id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Medium task", priority=Priority.MEDIUM, id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="High task 2", priority=Priority.HIGH, id=3, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Low task", priority=Priority.LOW, id=4, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Filter by HIGH priority
        results = service.filter_tasks(priority=Priority.HIGH)

        # Should find only high priority tasks
        assert len(results) == 2
        assert results[0].title == "High task 1"
        assert results[1].title == "High task 2"

    def test_filter_tasks_by_status_completed(self) -> None:
        """Test filter_tasks filters by completed status"""
        from src.core.services import TaskService

        # Mock storage with completed and incomplete tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Task 1", completed=True, id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task 2", completed=False, id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task 3", completed=True, id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Filter by completed status
        results = service.filter_tasks(completed=True)

        # Should find only completed tasks
        assert len(results) == 2
        assert results[0].title == "Task 1"
        assert results[1].title == "Task 3"

    def test_filter_tasks_by_status_incomplete(self) -> None:
        """Test filter_tasks filters by incomplete status"""
        from src.core.services import TaskService

        # Mock storage with completed and incomplete tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Task A", completed=False, id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task B", completed=True, id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task C", completed=False, id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Filter by incomplete status
        results = service.filter_tasks(completed=False)

        # Should find only incomplete tasks
        assert len(results) == 2
        assert results[0].title == "Task A"
        assert results[1].title == "Task C"

    def test_filter_tasks_by_tag(self) -> None:
        """Test filter_tasks filters by tag"""
        from src.core.services import TaskService

        # Mock storage with tasks with various tags
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Work task 1", tags=["work", "urgent"], id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Personal task", tags=["personal"], id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Work task 2", tags=["work"], id=3, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Untagged task", tags=[], id=4, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Filter by "work" tag
        results = service.filter_tasks(tag="work")

        # Should find only tasks with "work" tag
        assert len(results) == 2
        assert results[0].title == "Work task 1"
        assert results[1].title == "Work task 2"

    def test_filter_tasks_combined_criteria(self) -> None:
        """Test filter_tasks with multiple criteria (priority + status)"""
        from src.core.services import TaskService

        # Mock storage with various tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(
                title="High incomplete",
                priority=Priority.HIGH,
                completed=False,
                id=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Task(
                title="High complete",
                priority=Priority.HIGH,
                completed=True,
                id=2,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Task(
                title="Low incomplete",
                priority=Priority.LOW,
                completed=False,
                id=3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Filter by HIGH priority AND incomplete
        results = service.filter_tasks(priority=Priority.HIGH, completed=False)

        # Should find only high priority incomplete tasks
        assert len(results) == 1
        assert results[0].title == "High incomplete"

    def test_filter_tasks_returns_empty_list_when_no_matches(self) -> None:
        """Test filter_tasks returns empty list when no matches found"""
        from src.core.services import TaskService

        # Mock storage with tasks
        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Task 1", priority=Priority.LOW, id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Task 2", priority=Priority.MEDIUM, id=2, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Filter by HIGH priority (none exist)
        results = service.filter_tasks(priority=Priority.HIGH)

        # Should return empty list
        assert results == []

    def test_filter_tasks_raises_error_when_no_criteria(self) -> None:
        """Test filter_tasks raises ValueError when no filter criteria provided"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        service = TaskService(mock_storage)

        # Should raise ValueError when no criteria provided
        with pytest.raises(ValueError, match="at least one filter"):
            service.filter_tasks()
