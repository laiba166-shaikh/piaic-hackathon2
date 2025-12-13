"""Unit tests for core models (Task, Priority, Recurrence)"""
from datetime import datetime, timedelta
import pytest
from src.core.models import Task, Priority, Recurrence


class TestPriorityEnum:
    """Tests for Priority enum"""

    def test_priority_values(self) -> None:
        """Test Priority enum has correct values"""
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"

    def test_priority_from_string(self) -> None:
        """Test creating Priority from string values"""
        assert Priority("high") == Priority.HIGH
        assert Priority("medium") == Priority.MEDIUM
        assert Priority("low") == Priority.LOW

    def test_priority_invalid_value(self) -> None:
        """Test Priority raises error for invalid value"""
        with pytest.raises(ValueError):
            Priority("invalid")


class TestRecurrenceEnum:
    """Tests for Recurrence enum"""

    def test_recurrence_values(self) -> None:
        """Test Recurrence enum has correct values"""
        assert Recurrence.NONE.value == "none"
        assert Recurrence.DAILY.value == "daily"
        assert Recurrence.WEEKLY.value == "weekly"
        assert Recurrence.MONTHLY.value == "monthly"

    def test_recurrence_from_string(self) -> None:
        """Test creating Recurrence from string values"""
        assert Recurrence("none") == Recurrence.NONE
        assert Recurrence("daily") == Recurrence.DAILY
        assert Recurrence("weekly") == Recurrence.WEEKLY
        assert Recurrence("monthly") == Recurrence.MONTHLY

    def test_recurrence_invalid_value(self) -> None:
        """Test Recurrence raises error for invalid value"""
        with pytest.raises(ValueError):
            Recurrence("invalid")


class TestTaskDataclass:
    """Tests for Task dataclass"""

    def test_task_creation_minimal(self) -> None:
        """Test creating task with only required fields"""
        task = Task(title="Buy milk")

        assert task.title == "Buy milk"
        assert task.description is None
        assert task.completed is False
        assert task.priority == Priority.MEDIUM
        assert task.tags == []
        assert task.due_date is None
        assert task.recurrence == Recurrence.NONE
        assert task.reminder_minutes is None
        assert task.id is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_creation_full(self) -> None:
        """Test creating task with all fields"""
        due_date = datetime(2025, 12, 15, 14, 0)

        task = Task(
            title="Complete proposal",
            description="Q4 project proposal",
            completed=False,
            priority=Priority.HIGH,
            tags=["work", "urgent"],
            due_date=due_date,
            recurrence=Recurrence.WEEKLY,
            reminder_minutes=60,
        )

        assert task.title == "Complete proposal"
        assert task.description == "Q4 project proposal"
        assert task.completed is False
        assert task.priority == Priority.HIGH
        assert task.tags == ["work", "urgent"]
        assert task.due_date == due_date
        assert task.recurrence == Recurrence.WEEKLY
        assert task.reminder_minutes == 60

    def test_task_title_required(self) -> None:
        """Test task title is required (FR-007)"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="")

    def test_task_title_whitespace_only(self) -> None:
        """Test task title cannot be whitespace only"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="   ")

    def test_task_title_max_length(self) -> None:
        """Test task title max 200 characters (FR-001)"""
        valid_title = "x" * 200
        task = Task(title=valid_title)
        assert task.title == valid_title

        # Test exceeding max length
        invalid_title = "x" * 201
        with pytest.raises(ValueError, match="Title max 200 characters"):
            Task(title=invalid_title)

    def test_task_description_max_length(self) -> None:
        """Test task description max 500 characters (FR-001 clarified)"""
        valid_description = "x" * 500
        task = Task(title="Test", description=valid_description)
        assert task.description == valid_description

        # Test exceeding max length
        invalid_description = "x" * 501
        with pytest.raises(ValueError, match="Description max 500 characters"):
            Task(title="Test", description=invalid_description)

    def test_task_reminder_positive_integer(self) -> None:
        """Test reminder must be positive integer (FR-028)"""
        task = Task(title="Test", reminder_minutes=60)
        assert task.reminder_minutes == 60

        # Test zero reminder
        with pytest.raises(ValueError, match="Reminder must be positive minutes"):
            Task(title="Test", reminder_minutes=0)

        # Test negative reminder
        with pytest.raises(ValueError, match="Reminder must be positive minutes"):
            Task(title="Test", reminder_minutes=-10)

    def test_task_default_values(self) -> None:
        """Test task default values"""
        task = Task(title="Test task")

        assert task.completed is False
        assert task.priority == Priority.MEDIUM
        assert task.recurrence == Recurrence.NONE
        assert task.tags == []


class TestTaskIsOverdue:
    """Tests for Task.is_overdue() method"""

    def test_is_overdue_past_due_date(self) -> None:
        """Test task is overdue when due_date is in the past"""
        task = Task(
            title="Overdue task",
            due_date=datetime.now() - timedelta(days=1),
        )
        assert task.is_overdue() is True

    def test_is_overdue_future_due_date(self) -> None:
        """Test task is not overdue when due_date is in the future"""
        task = Task(
            title="Future task",
            due_date=datetime.now() + timedelta(days=1),
        )
        assert task.is_overdue() is False

    def test_is_overdue_no_due_date(self) -> None:
        """Test task is not overdue when no due_date is set"""
        task = Task(title="No due date")
        assert task.is_overdue() is False

    def test_is_overdue_completed_task(self) -> None:
        """Test completed task is not overdue even if past due date"""
        task = Task(
            title="Completed overdue",
            due_date=datetime.now() - timedelta(days=1),
            completed=True,
        )
        assert task.is_overdue() is False


class TestTaskIsDueToday:
    """Tests for Task.is_due_today() method"""

    def test_is_due_today_same_date(self) -> None:
        """Test task is due today when due_date is today"""
        task = Task(
            title="Due today",
            due_date=datetime.now(),
        )
        assert task.is_due_today() is True

    def test_is_due_today_tomorrow(self) -> None:
        """Test task is not due today when due_date is tomorrow"""
        task = Task(
            title="Due tomorrow",
            due_date=datetime.now() + timedelta(days=1),
        )
        assert task.is_due_today() is False

    def test_is_due_today_yesterday(self) -> None:
        """Test task is not due today when due_date is yesterday"""
        task = Task(
            title="Due yesterday",
            due_date=datetime.now() - timedelta(days=1),
        )
        assert task.is_due_today() is False

    def test_is_due_today_no_due_date(self) -> None:
        """Test task is not due today when no due_date is set"""
        task = Task(title="No due date")
        assert task.is_due_today() is False

    def test_is_due_today_completed_task(self) -> None:
        """Test completed task is not due today even if date matches"""
        task = Task(
            title="Completed today",
            due_date=datetime.now(),
            completed=True,
        )
        assert task.is_due_today() is False
