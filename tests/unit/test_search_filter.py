"""Unit tests for search and filter functionality"""
import pytest
from datetime import datetime, timedelta
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


class TestSortTasks:
    """Unit tests for TaskService.sort_tasks() method (US9-007)"""

    def test_sort_tasks_by_priority_descending(self) -> None:
        """Test sort_tasks sorts by priority high -> medium -> low"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Low task", priority=Priority.LOW, id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="High task", priority=Priority.HIGH, id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Medium task", priority=Priority.MEDIUM, id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Sort by priority descending (high -> medium -> low)
        results = service.sort_tasks(by="priority", ascending=False)

        assert len(results) == 3
        assert results[0].priority == Priority.HIGH
        assert results[1].priority == Priority.MEDIUM
        assert results[2].priority == Priority.LOW

    def test_sort_tasks_by_priority_ascending(self) -> None:
        """Test sort_tasks sorts by priority low -> medium -> high when ascending"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="High task", priority=Priority.HIGH, id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Low task", priority=Priority.LOW, id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Medium task", priority=Priority.MEDIUM, id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Sort by priority ascending (low -> medium -> high)
        results = service.sort_tasks(by="priority", ascending=True)

        assert len(results) == 3
        assert results[0].priority == Priority.LOW
        assert results[1].priority == Priority.MEDIUM
        assert results[2].priority == Priority.HIGH

    def test_sort_tasks_by_title_alphabetically(self) -> None:
        """Test sort_tasks sorts by title A-Z"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        tasks = [
            Task(title="Zebra", id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Apple", id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Task(title="Mango", id=3, created_at=datetime.now(), updated_at=datetime.now()),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Sort by title ascending (A-Z)
        results = service.sort_tasks(by="title", ascending=True)

        assert len(results) == 3
        assert results[0].title == "Apple"
        assert results[1].title == "Mango"
        assert results[2].title == "Zebra"

    def test_sort_tasks_by_created_date(self) -> None:
        """Test sort_tasks sorts by created_at newest first"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        now = datetime.now()
        tasks = [
            Task(title="First", id=1, created_at=now - timedelta(hours=2), updated_at=now),
            Task(title="Third", id=2, created_at=now, updated_at=now),
            Task(title="Second", id=3, created_at=now - timedelta(hours=1), updated_at=now),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Sort by created descending (newest first)
        results = service.sort_tasks(by="created", ascending=False)

        assert len(results) == 3
        assert results[0].title == "Third"
        assert results[1].title == "Second"
        assert results[2].title == "First"

    def test_sort_tasks_by_created_date_ascending(self) -> None:
        """Test sort_tasks sorts by created_at oldest first when ascending"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        now = datetime.now()
        tasks = [
            Task(title="Third", id=1, created_at=now, updated_at=now),
            Task(title="First", id=2, created_at=now - timedelta(hours=2), updated_at=now),
            Task(title="Second", id=3, created_at=now - timedelta(hours=1), updated_at=now),
        ]
        mock_storage.list_all.return_value = tasks

        service = TaskService(mock_storage)

        # Sort by created ascending (oldest first)
        results = service.sort_tasks(by="created", ascending=True)

        assert len(results) == 3
        assert results[0].title == "First"
        assert results[1].title == "Second"
        assert results[2].title == "Third"

    def test_sort_tasks_returns_empty_list_when_no_tasks(self) -> None:
        """Test sort_tasks returns empty list when no tasks exist"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        mock_storage.list_all.return_value = []

        service = TaskService(mock_storage)

        results = service.sort_tasks(by="priority")

        assert results == []

    def test_sort_tasks_raises_error_for_invalid_field(self) -> None:
        """Test sort_tasks raises ValueError for invalid sort field"""
        from src.core.services import TaskService

        mock_storage = Mock(spec=ITaskStorage)
        service = TaskService(mock_storage)

        with pytest.raises(ValueError, match="Invalid sort field"):
            service.sort_tasks(by="invalid_field")
