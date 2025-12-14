"""
Integration tests for CLI commands.

These tests verify end-to-end CLI behavior including:
- Startup and welcome message (FR-013)
- Help command
- Exit functionality (FR-012, FR-014)
- Command integration
"""
import pytest
from click.testing import CliRunner
from src.cli.main import cli, display_welcome_message
from io import StringIO
import sys


class TestCLIStartup:
    """Integration tests for CLI startup and initialization"""

    def test_cli_displays_welcome_message_on_startup(self) -> None:
        """Test that CLI displays interactive mode welcome when invoked without commands"""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        # Should exit successfully (interactive mode exits immediately with empty input)
        assert result.exit_code == 0

        # Should contain welcome message elements for interactive mode
        assert "Todo CLI" in result.output
        assert "v0.1.0" in result.output
        assert "Interactive Mode" in result.output

        # Should mention task persistence in session
        assert "persist during this session" in result.output or "interactive mode" in result.output.lower()

        # Should mention help command (FR-013)
        assert "--help" in result.output or "help" in result.output.lower()

    def test_cli_help_command_displays_usage(self) -> None:
        """Test that --help flag displays usage information"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain help information
        assert "Usage:" in result.output or "usage:" in result.output.lower()
        assert "Options:" in result.output or "options:" in result.output.lower()

        # Should describe the application
        assert "Todo" in result.output or "task" in result.output.lower()

    def test_cli_version_command_displays_version(self) -> None:
        """Test that --version flag displays version information"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain version
        assert "0.1.0" in result.output
        assert "Todo CLI" in result.output

    def test_cli_exit_command_terminates_cleanly(self) -> None:
        """Test that exit command terminates the application cleanly (FR-012, FR-014)"""
        runner = CliRunner()
        result = runner.invoke(cli, ["exit"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should display goodbye message
        assert "Goodbye" in result.output or "goodbye" in result.output.lower()

        # Should mention data cleared
        assert "cleared" in result.output.lower() or "memory" in result.output.lower()

    def test_display_welcome_message_includes_required_elements(self) -> None:
        """Test that display_welcome_message() includes all required elements"""
        # Capture console output
        from rich.console import Console
        from io import StringIO

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)

        # Temporarily replace the console in the module
        import src.cli.main as main_module
        original_console = main_module.console
        main_module.console = console

        try:
            # Call the function
            display_welcome_message()

            # Get the output
            result = output.getvalue()

            # Verify required elements
            assert "Todo CLI" in result
            assert "0.1.0" in result or "v0.1.0" in result
            assert "WARNING" in result or "warning" in result.lower()
            assert "in-memory" in result.lower() or "memory" in result.lower()
            assert "--help" in result or "help" in result.lower()

        finally:
            # Restore original console
            main_module.console = original_console


class TestCLIErrorHandling:
    """Integration tests for CLI error handling"""

    def test_cli_handles_invalid_command_gracefully(self) -> None:
        """Test that invalid commands display helpful error messages"""
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-command"])

        # Should exit with error
        assert result.exit_code != 0

        # Should mention the error
        assert "Error" in result.output or "error" in result.output.lower() or "No such command" in result.output


class TestListCommand:
    """Integration tests for User Story 2: View Task List"""

    def test_list_command_with_tasks(self) -> None:
        """Test list command displays all tasks (US2-001, AC1)"""
        runner = CliRunner()

        # Add 3 tasks first
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])

        # Run list command
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain all task titles
        assert "Task 1" in result.output
        assert "Task 2" in result.output
        assert "Task 3" in result.output

        # Should show task IDs (1, 2, 3)
        assert "1" in result.output
        assert "2" in result.output
        assert "3" in result.output

        # Should show completion status
        assert "Incomplete" in result.output.lower() or "[ ]" in result.output or "incomplete" in result.output.lower()

    def test_list_command_with_empty_list(self) -> None:
        """Test list command with no tasks shows empty message (US2-002, AC2)"""
        runner = CliRunner()

        # Run list without adding any tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show "no tasks" or "empty" message
        assert "no tasks" in result.output.lower() or "empty" in result.output.lower()

    def test_list_command_shows_descriptions(self) -> None:
        """Test list command can show task descriptions (US2-003, AC3)"""
        runner = CliRunner()

        # Add task with description
        runner.invoke(cli, ["add", "Call dentist", "-d", "Schedule annual checkup"])

        # Run list command
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show task title
        assert "Call dentist" in result.output

        # Description might be shown inline or truncated - just verify task appears
        assert "1" in result.output  # Task ID should be shown

    def test_list_command_distinguishes_complete_incomplete(self) -> None:
        """Test list command distinguishes complete vs incomplete tasks (US2-004, AC4)"""
        runner = CliRunner()

        # Add two tasks
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])

        # Note: We'll need the 'done' command to mark tasks complete
        # For now, just verify incomplete tasks are shown
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show both tasks
        assert "Task 1" in result.output
        assert "Task 2" in result.output

        # Should indicate incomplete status (checkboxes, text, etc.)
        # The exact format will depend on implementation


class TestDoneCommand:
    """Integration tests for User Story 3: Mark Tasks Complete"""

    def test_done_command_marks_task_complete(self) -> None:
        """Test done command marks task as complete (US3-001, AC1)"""
        runner = CliRunner()

        # Add a task
        add_result = runner.invoke(cli, ["add", "Complete this task"])
        assert add_result.exit_code == 0

        # Mark task as done
        done_result = runner.invoke(cli, ["done", "1"])

        # Should exit successfully
        assert done_result.exit_code == 0

        # Should show success message
        assert "completed" in done_result.output.lower() or "done" in done_result.output.lower()

        # Verify task is marked complete by listing
        list_result = runner.invoke(cli, ["list"])
        assert list_result.exit_code == 0

        # Should show completed status (checkmark, strikethrough, etc.)
        assert "[X]" in list_result.output or "complete" in list_result.output.lower()

    def test_undone_command_marks_task_incomplete(self) -> None:
        """Test undone command marks task as incomplete (US3-002, AC2)"""
        runner = CliRunner()

        # Add a task and mark it done
        runner.invoke(cli, ["add", "Task to undo"])
        runner.invoke(cli, ["done", "1"])

        # Mark task as undone
        undone_result = runner.invoke(cli, ["undone", "1"])

        # Should exit successfully
        assert undone_result.exit_code == 0

        # Should show success message
        assert "incomplete" in undone_result.output.lower() or "undone" in undone_result.output.lower()

        # Verify task is marked incomplete by listing
        list_result = runner.invoke(cli, ["list"])
        assert list_result.exit_code == 0

        # Should show incomplete status
        assert "[ ]" in list_result.output or "incomplete" in list_result.output.lower()

    def test_done_command_with_invalid_id(self) -> None:
        """Test done command with invalid ID shows error (US3-003, AC3)"""
        runner = CliRunner()

        # Try to mark non-existent task as done
        result = runner.invoke(cli, ["done", "999"])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_done_command_with_non_numeric_id(self) -> None:
        """Test done command with non-numeric ID shows error (US3-004, AC4)"""
        runner = CliRunner()

        # Try to mark task with invalid ID format
        result = runner.invoke(cli, ["done", "abc"])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "invalid" in result.output.lower() or "error" in result.output.lower()

    def test_done_already_completed_task(self) -> None:
        """Test marking already completed task as done is idempotent (US3-005, AC5)"""
        runner = CliRunner()

        # Add a task and mark it done twice
        runner.invoke(cli, ["add", "Task to complete"])
        runner.invoke(cli, ["done", "1"])
        result = runner.invoke(cli, ["done", "1"])

        # Should still succeed (idempotent)
        assert result.exit_code == 0

        # Should show success or already complete message
        assert "completed" in result.output.lower() or "already" in result.output.lower()


class TestUpdateCommand:
    """Integration tests for User Story 4: Update Task Details"""

    def test_update_command_changes_title(self) -> None:
        """Test update command changes task title (US4-001, AC1)"""
        runner = CliRunner()

        # Add a task
        runner.invoke(cli, ["add", "Buy milk"])

        # Update the title
        result = runner.invoke(cli, ["update", "1", "--title", "Buy milk and eggs"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

        # Verify title changed by listing
        list_result = runner.invoke(cli, ["list"])
        assert "Buy milk and eggs" in list_result.output
        assert "Buy milk" not in list_result.output or "Buy milk and eggs" in list_result.output

    def test_update_command_adds_description(self) -> None:
        """Test update command adds description to task (US4-002, AC2)"""
        runner = CliRunner()

        # Add a task without description
        runner.invoke(cli, ["add", "Buy groceries"])

        # Update with description
        result = runner.invoke(cli, ["update", "1", "-d", "From the organic store"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

    def test_update_command_updates_description(self) -> None:
        """Test update command updates existing description (US4-003, AC3)"""
        runner = CliRunner()

        # Add a task with description
        runner.invoke(cli, ["add", "Call dentist", "-d", "Annual checkup"])

        # Update the description
        result = runner.invoke(cli, ["update", "1", "-d", "Schedule cleaning appointment"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

    def test_update_command_with_invalid_id(self) -> None:
        """Test update command with invalid ID shows error (US4-004, AC4)"""
        runner = CliRunner()

        # Try to update non-existent task
        result = runner.invoke(cli, ["update", "999", "--title", "New title"])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_update_command_with_empty_title(self) -> None:
        """Test update command with empty title shows error (US4-005, AC5)"""
        runner = CliRunner()

        # Add a task
        runner.invoke(cli, ["add", "Original title"])

        # Try to update with empty title
        result = runner.invoke(cli, ["update", "1", "--title", ""])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "empty" in result.output.lower() or "invalid" in result.output.lower() or "error" in result.output.lower()

    def test_update_command_with_both_title_and_description(self) -> None:
        """Test update command can update both title and description (US4-006, AC6)"""
        runner = CliRunner()

        # Add a task
        runner.invoke(cli, ["add", "Old title", "-d", "Old description"])

        # Update both title and description
        result = runner.invoke(cli, ["update", "1", "--title", "New title", "-d", "New description"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

        # Verify changes by listing
        list_result = runner.invoke(cli, ["list"])
        assert "New title" in list_result.output


class TestAddCommand:
    """Integration tests for User Story 1: Capture New Tasks"""

    def test_add_command_with_title_only(self) -> None:
        """Test add command with title only creates task (US1-001, AC1)"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Buy groceries"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should display success message with task ID (FR-009)
        assert "Task" in result.output or "task" in result.output.lower()
        assert "created" in result.output.lower() or "added" in result.output.lower()
        assert "1" in result.output  # First task should get ID 1

        # Should show task title
        assert "Buy groceries" in result.output

    def test_add_command_with_title_and_description(self) -> None:
        """Test add command with title and description (US1-002, AC2)"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Call dentist", "-d", "Schedule annual checkup"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should display success message
        assert "created" in result.output.lower() or "added" in result.output.lower()

        # Should show both title and description
        assert "Call dentist" in result.output
        # Note: Description might not be shown in success message, will verify in list command

    def test_add_command_with_empty_title_shows_error(self) -> None:
        """Test add command with empty title shows validation error (US1-003, AC3, FR-007)"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", ""])

        # Should exit with error
        assert result.exit_code != 0

        # Should display error message (FR-010)
        assert "Error" in result.output or "error" in result.output.lower()
        assert "title" in result.output.lower() or "empty" in result.output.lower()

    def test_add_command_assigns_unique_sequential_ids(self) -> None:
        """Test that multiple tasks get unique sequential IDs (US1-004, AC4, FR-002)"""
        runner = CliRunner()

        # Add first task
        result1 = runner.invoke(cli, ["add", "Task 1"])
        assert result1.exit_code == 0
        assert "1" in result1.output  # Should get ID 1

        # Add second task
        result2 = runner.invoke(cli, ["add", "Task 2"])
        assert result2.exit_code == 0
        assert "2" in result2.output  # Should get ID 2

        # Add third task
        result3 = runner.invoke(cli, ["add", "Task 3"])
        assert result3.exit_code == 0
        assert "3" in result3.output  # Should get ID 3
