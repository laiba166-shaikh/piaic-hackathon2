"""
Unit tests for edge cases (POLISH-012)

Tests for:
- Very long titles (200 chars max)
- Whitespace-only titles
- Invalid task IDs (negative, letters, large numbers)
- Special characters in titles/descriptions
- Tags with spaces and special characters
- Past due dates
- Exception classes
"""
import pytest
from datetime import datetime, timedelta
from src.cli.logics.models import Task, Priority, Recurrence
from src.cli.logics.exceptions import TaskNotFoundError, ValidationError, InvalidIDError
from src.cli.logics.validators import parse_tags, parse_due_date


class TestVeryLongTitles:
    """Test handling of very long titles (FR-034)"""

    def test_title_at_max_length_200_chars(self) -> None:
        """Test title at exactly 200 characters is accepted"""
        long_title = "A" * 200
        task = Task(title=long_title)
        assert len(task.title) == 200

    def test_title_exceeds_max_length_raises_error(self) -> None:
        """Test title over 200 characters raises ValueError"""
        too_long_title = "A" * 201
        with pytest.raises(ValueError, match="Title max 200 characters"):
            Task(title=too_long_title)

    def test_title_with_500_chars_raises_error(self) -> None:
        """Test very long title (500 chars) raises ValueError"""
        very_long_title = "B" * 500
        with pytest.raises(ValueError, match="Title max 200 characters"):
            Task(title=very_long_title)


class TestWhitespaceOnlyTitles:
    """Test rejection of whitespace-only titles"""

    def test_empty_title_raises_error(self) -> None:
        """Test empty string title raises ValueError"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="")

    def test_spaces_only_title_raises_error(self) -> None:
        """Test spaces-only title raises ValueError"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="   ")

    def test_tabs_only_title_raises_error(self) -> None:
        """Test tabs-only title raises ValueError"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="\t\t\t")

    def test_newlines_only_title_raises_error(self) -> None:
        """Test newlines-only title raises ValueError"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="\n\n\n")

    def test_mixed_whitespace_only_title_raises_error(self) -> None:
        """Test mixed whitespace-only title raises ValueError"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(title="  \t\n  ")


class TestDescriptionLimits:
    """Test description length limits"""

    def test_description_at_max_length_500_chars(self) -> None:
        """Test description at exactly 500 characters is accepted"""
        long_desc = "D" * 500
        task = Task(title="Test", description=long_desc)
        assert task.description is not None
        assert len(task.description) == 500

    def test_description_exceeds_max_length_raises_error(self) -> None:
        """Test description over 500 characters raises ValueError"""
        too_long_desc = "D" * 501
        with pytest.raises(ValueError, match="Description max 500 characters"):
            Task(title="Test", description=too_long_desc)


class TestSpecialCharactersInTitles:
    """Test special characters in titles and descriptions"""

    def test_title_with_unicode_emoji(self) -> None:
        """Test title with emoji characters"""
        task = Task(title="Task with emoji 🎉✅")
        assert "🎉" in task.title

    def test_title_with_quotes(self) -> None:
        """Test title with single and double quotes"""
        task = Task(title="Task with 'single' and \"double\" quotes")
        assert "'" in task.title
        assert '"' in task.title

    def test_title_with_special_punctuation(self) -> None:
        """Test title with special punctuation"""
        task = Task(title="Task: with; various! punctuation? marks...")
        assert task.title == "Task: with; various! punctuation? marks..."

    def test_title_with_unicode_characters(self) -> None:
        """Test title with international characters"""
        task = Task(title="Tâche avec des caractères spéciaux äöü")
        assert "é" in task.title
        assert "ü" in task.title

    def test_description_with_newlines(self) -> None:
        """Test description with newline characters"""
        task = Task(title="Test", description="Line 1\nLine 2\nLine 3")
        assert "\n" in task.description


class TestTagsWithSpecialCharacters:
    """Test tags with various characters"""

    def test_tags_with_spaces_in_multiword(self) -> None:
        """Test parsing tags with spaces (multi-word tags)"""
        tags = parse_tags("work,high priority,urgent task")
        assert "high priority" in tags
        assert "urgent task" in tags

    def test_tags_with_numbers(self) -> None:
        """Test tags containing numbers"""
        tags = parse_tags("project1,phase2,v3.0")
        assert "project1" in tags
        assert "v3.0" in tags

    def test_tags_with_special_characters(self) -> None:
        """Test tags with special characters"""
        tags = parse_tags("@work,#urgent,$important")
        assert "@work" in tags
        assert "#urgent" in tags

    def test_empty_tags_are_filtered(self) -> None:
        """Test that empty tags from consecutive commas are filtered"""
        tags = parse_tags("work,,urgent,,,important")
        assert "" not in tags
        assert len(tags) == 3


class TestPastDueDates:
    """Test handling of past due dates"""

    def test_task_with_past_due_date_is_overdue(self) -> None:
        """Test that task with past due date is marked overdue"""
        past_date = datetime.now() - timedelta(days=1)
        task = Task(title="Overdue task", due_date=past_date, completed=False)
        assert task.is_overdue() is True

    def test_completed_task_with_past_due_date_not_overdue(self) -> None:
        """Test that completed task is not overdue even with past due date"""
        past_date = datetime.now() - timedelta(days=1)
        task = Task(title="Done task", due_date=past_date, completed=True)
        assert task.is_overdue() is False

    def test_task_due_far_in_past_is_overdue(self) -> None:
        """Test task due very far in past is overdue"""
        very_past_date = datetime.now() - timedelta(days=365)
        task = Task(title="Very overdue", due_date=very_past_date, completed=False)
        assert task.is_overdue() is True

    def test_parse_past_due_date(self) -> None:
        """Test parsing a past due date string"""
        past_date = parse_due_date("2020-01-01")
        assert past_date.year == 2020
        assert past_date.month == 1
        assert past_date.day == 1


class TestExceptionClasses:
    """Test custom exception classes"""

    def test_task_not_found_error_message(self) -> None:
        """Test TaskNotFoundError has correct message"""
        error = TaskNotFoundError(42)
        assert error.task_id == 42
        assert "42" in str(error)
        assert "not found" in str(error).lower()

    def test_task_not_found_error_can_be_raised(self) -> None:
        """Test TaskNotFoundError can be raised and caught"""
        with pytest.raises(TaskNotFoundError) as exc_info:
            raise TaskNotFoundError(123)
        assert exc_info.value.task_id == 123

    def test_invalid_id_error_message(self) -> None:
        """Test InvalidIDError has correct message"""
        error = InvalidIDError(-1)
        assert error.task_id == -1
        assert "-1" in str(error)
        assert "invalid" in str(error).lower()

    def test_invalid_id_error_can_be_raised(self) -> None:
        """Test InvalidIDError can be raised and caught"""
        with pytest.raises(InvalidIDError) as exc_info:
            raise InvalidIDError(-5)
        assert exc_info.value.task_id == -5

    def test_validation_error_can_be_raised(self) -> None:
        """Test ValidationError can be raised and caught"""
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid data")


class TestReminderValidation:
    """Test reminder_minutes validation"""

    def test_positive_reminder_accepted(self) -> None:
        """Test positive reminder minutes is accepted"""
        task = Task(title="Test", reminder_minutes=60)
        assert task.reminder_minutes == 60

    def test_zero_reminder_raises_error(self) -> None:
        """Test zero reminder minutes raises ValueError"""
        with pytest.raises(ValueError, match="Reminder must be positive"):
            Task(title="Test", reminder_minutes=0)

    def test_negative_reminder_raises_error(self) -> None:
        """Test negative reminder minutes raises ValueError"""
        with pytest.raises(ValueError, match="Reminder must be positive"):
            Task(title="Test", reminder_minutes=-10)


class TestDateParsingEdgeCases:
    """Test date parsing edge cases"""

    def test_parse_date_only_format(self) -> None:
        """Test parsing date without time"""
        dt = parse_due_date("2025-06-15")
        assert dt.year == 2025
        assert dt.month == 6
        assert dt.day == 15
        assert dt.hour == 0
        assert dt.minute == 0

    def test_parse_date_with_time(self) -> None:
        """Test parsing date with time"""
        dt = parse_due_date("2025-12-31 23:59")
        assert dt.year == 2025
        assert dt.month == 12
        assert dt.day == 31
        assert dt.hour == 23
        assert dt.minute == 59

    def test_parse_invalid_format_raises_error(self) -> None:
        """Test parsing invalid date format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_due_date("not-a-date")

    def test_parse_empty_date_raises_error(self) -> None:
        """Test parsing empty string raises ValueError"""
        with pytest.raises(ValueError, match="empty"):
            parse_due_date("")

    def test_parse_whitespace_only_raises_error(self) -> None:
        """Test parsing whitespace-only raises ValueError"""
        with pytest.raises(ValueError, match="empty"):
            parse_due_date("   ")

    def test_parse_partial_date_raises_error(self) -> None:
        """Test parsing partial date raises ValueError"""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_due_date("2025-12")

    def test_parse_wrong_separator_raises_error(self) -> None:
        """Test parsing with wrong separator raises ValueError"""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_due_date("2025/12/31")


class TestTaskDueToday:
    """Test is_due_today() method"""

    def test_task_due_today_returns_true(self) -> None:
        """Test task due today returns True"""
        today = datetime.now().replace(hour=23, minute=59)
        task = Task(title="Today task", due_date=today, completed=False)
        assert task.is_due_today() is True

    def test_task_due_yesterday_returns_false(self) -> None:
        """Test task due yesterday returns False for is_due_today"""
        yesterday = datetime.now() - timedelta(days=1)
        task = Task(title="Yesterday task", due_date=yesterday, completed=False)
        assert task.is_due_today() is False

    def test_task_due_tomorrow_returns_false(self) -> None:
        """Test task due tomorrow returns False for is_due_today"""
        tomorrow = datetime.now() + timedelta(days=1)
        task = Task(title="Tomorrow task", due_date=tomorrow, completed=False)
        assert task.is_due_today() is False

    def test_completed_task_due_today_returns_false(self) -> None:
        """Test completed task due today returns False"""
        today = datetime.now()
        task = Task(title="Done today", due_date=today, completed=True)
        assert task.is_due_today() is False

    def test_task_without_due_date_returns_false(self) -> None:
        """Test task without due date returns False"""
        task = Task(title="No due date")
        assert task.is_due_today() is False
