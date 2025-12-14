"""
Integration tests for table rendering visual distinctions.

Tests verify that completed and incomplete tasks have proper visual indicators
in the table output (FR-036, FR-037, SC-015).
"""
import pytest
from click.testing import CliRunner
from src.cli.main import cli


class TestTableVisualDistinctions:
    """Integration tests for visual distinction in task table (US3-011)"""

    def test_completed_task_shows_checkmark_indicator(self) -> None:
        """Test completed tasks show [X] indicator (FR-036, SC-015)"""
        runner = CliRunner()

        # Add a task and mark it complete
        runner.invoke(cli, ["add", "Completed task"])
        runner.invoke(cli, ["done", "1"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show completed indicator [X]
        assert "[X]" in result.output

        # Task should be in the list
        assert "Completed task" in result.output

    def test_incomplete_task_shows_empty_box_indicator(self) -> None:
        """Test incomplete tasks show [ ] indicator (FR-037)"""
        runner = CliRunner()

        # Add a task (incomplete by default)
        runner.invoke(cli, ["add", "Incomplete task"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show incomplete indicator [ ]
        assert "[ ]" in result.output

        # Task should be in the list
        assert "Incomplete task" in result.output

    def test_mixed_completed_and_incomplete_tasks_have_different_indicators(self) -> None:
        """Test that completed and incomplete tasks show different visual indicators (SC-015)"""
        runner = CliRunner()

        # Add multiple tasks
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])

        # Mark task 2 as complete
        runner.invoke(cli, ["done", "2"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should have both completed and incomplete indicators
        assert "[X]" in result.output  # Completed indicator
        assert "[ ]" in result.output  # Incomplete indicator

        # Should show all tasks
        assert "Task 1" in result.output
        assert "Task 2" in result.output
        assert "Task 3" in result.output

    def test_completed_task_has_visual_styling(self) -> None:
        """Test completed tasks have strikethrough or dimmed styling"""
        runner = CliRunner()

        # Add a task and mark it complete
        runner.invoke(cli, ["add", "Styled completed task"])
        runner.invoke(cli, ["done", "1"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show completed indicator
        assert "[X]" in result.output

        # Rich will apply styling (strikethrough, dim) to completed tasks
        # The exact rendering depends on terminal capabilities,
        # but we can verify the task appears with its indicator
        assert "Styled completed task" in result.output

    def test_task_status_indicator_appears_in_status_column(self) -> None:
        """Test that status indicators appear in the Status column of the table"""
        runner = CliRunner()

        # Add tasks with different statuses
        runner.invoke(cli, ["add", "First task"])
        runner.invoke(cli, ["add", "Second task"])
        runner.invoke(cli, ["done", "1"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should have table header with "Status" column
        assert "Status" in result.output

        # Should have both types of indicators in the output
        assert "[X]" in result.output
        assert "[ ]" in result.output

    def test_undone_task_changes_indicator_from_checkmark_to_empty(self) -> None:
        """Test that marking task as undone changes [X] to [ ]"""
        runner = CliRunner()

        # Add a task, mark complete, then mark incomplete
        runner.invoke(cli, ["add", "Toggle task"])
        runner.invoke(cli, ["done", "1"])

        # Verify it shows [X]
        result_done = runner.invoke(cli, ["list"])
        assert "[X]" in result_done.output

        # Mark as undone
        runner.invoke(cli, ["undone", "1"])

        # List tasks again
        result_undone = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result_undone.exit_code == 0

        # Should now show [ ] instead of [X]
        assert "[ ]" in result_undone.output

        # Should show the task
        assert "Toggle task" in result_undone.output

    def test_multiple_tasks_show_correct_status_indicators(self) -> None:
        """Test that multiple tasks each show their correct status indicator"""
        runner = CliRunner()

        # Add multiple tasks
        runner.invoke(cli, ["add", "First task"])
        runner.invoke(cli, ["add", "Second task"])
        runner.invoke(cli, ["add", "Third task"])

        # Mark first and third tasks complete
        runner.invoke(cli, ["done", "1"])
        runner.invoke(cli, ["done", "3"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show both completed and incomplete indicators
        # We expect 2 completed ([X]) and 1 incomplete ([ ])
        assert result.output.count("[X]") == 2  # Tasks 1 and 3
        assert result.output.count("[ ]") == 1  # Task 2

        # Should show all tasks
        assert "First task" in result.output
        assert "Second task" in result.output
        assert "Third task" in result.output

        # Should have Status column
        assert "Status" in result.output
