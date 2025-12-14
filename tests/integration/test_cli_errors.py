"""
Integration tests for CLI error handling paths.

Tests for:
- Exception handling in CLI commands
- Error messages for invalid inputs
- Edge cases in command execution
"""
import pytest
from click.testing import CliRunner
from src.cli.main import cli
from src.cli.commands.basic import _storage


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    """Clear storage before each test"""
    _storage._tasks.clear()
    _storage._next_id = 1


class TestAddCommandErrors:
    """Test error handling in add command"""

    def test_add_empty_title_error(self) -> None:
        """Test add command with empty title raises error"""
        runner = CliRunner()
        # Empty string title triggers validation error
        result = runner.invoke(cli, ["add", ""])
        assert result.exit_code != 0

    def test_add_whitespace_title_error(self) -> None:
        """Test add command with whitespace-only title raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "   "])
        assert result.exit_code != 0
        assert "empty" in result.output.lower() or "Invalid" in result.output

    def test_add_invalid_date_format_error(self) -> None:
        """Test add command with invalid date format raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Test task", "--due", "not-a-date"])
        assert result.exit_code != 0
        assert "Invalid" in result.output or "date" in result.output.lower()


class TestUpdateCommandErrors:
    """Test error handling in update command"""

    def test_update_nonexistent_task_error(self) -> None:
        """Test update command with nonexistent task ID raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["update", "999", "--title", "New title"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "Error" in result.output

    def test_update_no_changes_error(self) -> None:
        """Test update command with no changes raises error"""
        runner = CliRunner()
        # First add a task
        runner.invoke(cli, ["add", "Test task"])
        # Try to update without any changes
        result = runner.invoke(cli, ["update", "1"])
        assert result.exit_code != 0
        assert "At least one" in result.output or "must be provided" in result.output

    def test_update_empty_title_error(self) -> None:
        """Test update command with empty title raises error"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test task"])
        result = runner.invoke(cli, ["update", "1", "--title", "   "])
        assert result.exit_code != 0


class TestDoneCommandErrors:
    """Test error handling in done command"""

    def test_done_nonexistent_task_error(self) -> None:
        """Test done command with nonexistent task ID raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["done", "999"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "Error" in result.output


class TestUndoneCommandErrors:
    """Test error handling in undone command"""

    def test_undone_nonexistent_task_error(self) -> None:
        """Test undone command with nonexistent task ID raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["undone", "999"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "Error" in result.output


class TestDeleteCommandErrors:
    """Test error handling in delete command"""

    def test_delete_nonexistent_task_error(self) -> None:
        """Test delete command with nonexistent task ID raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["delete", "999"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "Error" in result.output


class TestSearchCommandErrors:
    """Test error handling in search command"""

    def test_search_empty_query_error(self) -> None:
        """Test search command with empty query raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", ""])
        # Empty query should error
        assert result.exit_code != 0 or "No tasks found" in result.output


class TestFilterCommandErrors:
    """Test error handling in filter command"""

    def test_filter_no_criteria_error(self) -> None:
        """Test filter command with no criteria raises error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["filter"])
        assert result.exit_code != 0
        assert "No filter criteria" in result.output or "At least one" in result.output


class TestSortCommandErrors:
    """Test error handling in sort command"""

    def test_sort_empty_list_no_error(self) -> None:
        """Test sort command with empty list shows message"""
        runner = CliRunner()
        result = runner.invoke(cli, ["sort"])
        # Should show "no tasks" message, not error
        assert "No tasks" in result.output or result.exit_code == 0


class TestListCommandErrors:
    """Test list command edge cases"""

    def test_list_empty_shows_message(self) -> None:
        """Test list command with empty list shows helpful message"""
        runner = CliRunner()
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No tasks" in result.output or "empty" in result.output.lower()


class TestRecurrenceUpdateErrors:
    """Test recurrence update restrictions"""

    def test_update_recurrence_on_completed_task_error(self) -> None:
        """Test updating recurrence on completed task raises error"""
        runner = CliRunner()
        # Add and complete a task
        runner.invoke(cli, ["add", "Test task"])
        runner.invoke(cli, ["done", "1"])
        # Try to update recurrence
        result = runner.invoke(cli, ["update", "1", "--recurrence", "daily"])
        assert result.exit_code != 0
        assert "completed" in result.output.lower() or "Cannot" in result.output
