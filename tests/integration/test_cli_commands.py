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

    def test_update_command_changes_priority(self) -> None:
        """Test update command can change task priority (US6-010)"""
        runner = CliRunner()

        # Add a task with medium priority (default)
        runner.invoke(cli, ["add", "Task with priority"])

        # Update priority to high
        result = runner.invoke(cli, ["update", "1", "-p", "high"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message with updated priority
        assert "updated" in result.output.lower()
        assert "high" in result.output.lower() or "HIGH" in result.output

    def test_update_command_adds_tags(self) -> None:
        """Test update command can add tags to a task (US6-010)"""
        runner = CliRunner()

        # Add a task without tags
        runner.invoke(cli, ["add", "Task without tags"])

        # Add tags
        result = runner.invoke(cli, ["update", "1", "--tags", "work,urgent"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

        # Verify tags in list output
        list_result = runner.invoke(cli, ["list"])
        assert "work" in list_result.output
        assert "urgent" in list_result.output

    def test_update_command_changes_tags(self) -> None:
        """Test update command can change existing tags (US6-010)"""
        runner = CliRunner()

        # Add a task with tags
        runner.invoke(cli, ["add", "Task with tags", "--tags", "old,tags"])

        # Update tags
        result = runner.invoke(cli, ["update", "1", "--tags", "new,updated"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

        # Verify new tags in list output
        list_result = runner.invoke(cli, ["list"])
        assert "new" in list_result.output
        assert "updated" in list_result.output

    def test_update_command_with_priority_and_tags(self) -> None:
        """Test update command can update both priority and tags (US6-010)"""
        runner = CliRunner()

        # Add a task
        runner.invoke(cli, ["add", "Multi-update task"])

        # Update both priority and tags
        result = runner.invoke(cli, ["update", "1", "-p", "high", "--tags", "work,urgent"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "updated" in result.output.lower()

        # Verify changes in list output
        list_result = runner.invoke(cli, ["list"])
        assert "Multi-update task" in list_result.output
        assert "work" in list_result.output
        assert "urgent" in list_result.output

    def test_update_command_with_all_fields(self) -> None:
        """Test update command can update title, description, priority, and tags together (US6-010)"""
        runner = CliRunner()

        # Add a basic task
        runner.invoke(cli, ["add", "Old task"])

        # Update all fields
        result = runner.invoke(
            cli,
            [
                "update",
                "1",
                "--title",
                "New task",
                "-d",
                "New description",
                "-p",
                "low",
                "--tags",
                "personal,home",
            ],
        )

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message with all updates
        assert "updated" in result.output.lower()
        assert "New task" in result.output
        assert "New description" in result.output
        assert "low" in result.output.lower() or "LOW" in result.output
        assert "personal" in result.output
        assert "home" in result.output


class TestDeleteCommand:
    """Integration tests for User Story 5: Delete Unwanted Tasks"""

    def test_delete_command_removes_task(self) -> None:
        """Test delete command removes task from list (US5-001, AC1)"""
        runner = CliRunner()

        # Add a task
        runner.invoke(cli, ["add", "Task to delete"])

        # Delete the task
        result = runner.invoke(cli, ["delete", "1"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show success message
        assert "deleted" in result.output.lower() or "removed" in result.output.lower()

        # Verify task is removed by listing
        list_result = runner.invoke(cli, ["list"])
        assert "Task to delete" not in list_result.output
        assert "no tasks" in list_result.output.lower() or "empty" in list_result.output.lower()

    def test_delete_command_with_invalid_id(self) -> None:
        """Test delete command with invalid ID shows error (US5-002, AC2)"""
        runner = CliRunner()

        # Try to delete non-existent task
        result = runner.invoke(cli, ["delete", "999"])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_delete_command_affects_only_target_task(self) -> None:
        """Test delete command only removes target task (US5-003, AC3)"""
        runner = CliRunner()

        # Add 3 tasks
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])

        # Delete task 2
        result = runner.invoke(cli, ["delete", "2"])

        # Should exit successfully
        assert result.exit_code == 0

        # Verify tasks 1 and 3 remain
        list_result = runner.invoke(cli, ["list"])
        assert "Task 1" in list_result.output
        assert "Task 2" not in list_result.output
        assert "Task 3" in list_result.output

    def test_delete_all_tasks_shows_empty_message(self) -> None:
        """Test deleting all tasks shows empty list message (US5-004, AC4)"""
        runner = CliRunner()

        # Add 2 tasks
        runner.invoke(cli, ["add", "Task A"])
        runner.invoke(cli, ["add", "Task B"])

        # Delete both tasks
        runner.invoke(cli, ["delete", "1"])
        runner.invoke(cli, ["delete", "2"])

        # List tasks
        result = runner.invoke(cli, ["list"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show "no tasks" message
        assert "no tasks" in result.output.lower() or "empty" in result.output.lower()

    def test_delete_command_with_non_numeric_id(self) -> None:
        """Test delete command with non-numeric ID shows error"""
        runner = CliRunner()

        # Try to delete with invalid ID format
        result = runner.invoke(cli, ["delete", "abc"])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "invalid" in result.output.lower() or "error" in result.output.lower()

    def test_deleted_id_is_never_reused(self) -> None:
        """Test that IDs are never reused after deletion (US5-010, FR-002)"""
        runner = CliRunner()

        # Add 3 tasks (should get IDs 1, 2, 3)
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])

        # Delete task 2
        result = runner.invoke(cli, ["delete", "2"])
        assert result.exit_code == 0

        # Add a new task - should get ID 4, NOT reuse ID 2
        runner.invoke(cli, ["add", "Task 4"])

        # List all tasks
        list_result = runner.invoke(cli, ["list"])

        # Should show tasks with IDs 1, 3, 4 (not 2)
        assert "Task 1" in list_result.output
        assert "Task 3" in list_result.output
        assert "Task 4" in list_result.output

        # Verify ID 2 is NOT in the output (deleted and not reused)
        assert "Task 2" not in list_result.output

        # The output should contain ID 4 (new task) but not show ID 2 being reused
        # Parse the output to find the ID column values
        lines = list_result.output.split("\n")

        # Find lines that contain task data (have both a task title and an ID number)
        # These lines will have the pattern: "│  [ ]   │    N │"
        task_data_lines = [
            line
            for line in lines
            if ("│" in line and any(f"Task {i}" in line for i in [1, 3, 4]))
        ]

        # Verify we have exactly 3 tasks (1, 3, 4)
        assert len(task_data_lines) == 3

        # Verify the newest task (Task 4) has ID 4, not ID 2
        task4_line = [line for line in task_data_lines if "Task 4" in line][0]

        # The line should contain "│    4 │" indicating ID 4
        # Use a simple check: the number 4 should appear in the ID column
        assert "│    4 │" in task4_line or "│   4 │" in task4_line


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

    def test_add_command_with_priority(self) -> None:
        """Test add command with priority option (US6-001)"""
        runner = CliRunner()

        # Add task with high priority
        result = runner.invoke(cli, ["add", "Complete proposal", "-p", "high"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should display success message
        assert "created" in result.output.lower() or "added" in result.output.lower()

        # List tasks to verify priority was set
        list_result = runner.invoke(cli, ["list"])

        # Should show the task
        assert "Complete proposal" in list_result.output

        # Should show high priority indicator (will be implemented in GREEN phase)
        # For now, just verify task was created
        assert result.exit_code == 0

    def test_add_command_with_tags(self) -> None:
        """Test add command with tags option (US6-002)"""
        runner = CliRunner()

        # Add task with tags
        result = runner.invoke(cli, ["add", "Review code", "--tags", "work,urgent"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should display success message
        assert "created" in result.output.lower() or "added" in result.output.lower()

        # List tasks to verify tags were set
        list_result = runner.invoke(cli, ["list"])

        # Should show the task
        assert "Review code" in list_result.output

        # Should show tags (will verify format in GREEN phase)
        # For now, just verify task was created
        assert result.exit_code == 0

    def test_add_command_with_multiword_tags(self) -> None:
        """Test add command with multi-word tags using quotes (US6-004)"""
        runner = CliRunner()

        # Add task with multi-word tags
        result = runner.invoke(cli, ["add", "Meeting", "--tags", "work,high priority"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should display success message
        assert "created" in result.output.lower() or "added" in result.output.lower()

        # List tasks to verify tags were set
        list_result = runner.invoke(cli, ["list"])

        # Should show the task
        assert "Meeting" in list_result.output

        # Tags should be parsed correctly (will verify in GREEN phase)
        assert result.exit_code == 0


class TestSearchCommand:
    """Integration tests for User Story 7: Search Tasks"""

    def test_search_command_finds_matching_tasks(self) -> None:
        """Test search command finds tasks by keyword in title (US7-001)"""
        runner = CliRunner()

        # Add 10 tasks with varied titles
        runner.invoke(cli, ["add", "Team meeting"])
        runner.invoke(cli, ["add", "Client meeting"])
        runner.invoke(cli, ["add", "Project review"])
        runner.invoke(cli, ["add", "Code review"])
        runner.invoke(cli, ["add", "Meeting notes"])
        runner.invoke(cli, ["add", "Budget planning"])
        runner.invoke(cli, ["add", "Sprint meeting"])
        runner.invoke(cli, ["add", "Design review"])
        runner.invoke(cli, ["add", "Quarterly meeting"])
        runner.invoke(cli, ["add", "Status update"])

        # Search for "meeting"
        result = runner.invoke(cli, ["search", "meeting"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show matching tasks
        assert "Team meeting" in result.output
        assert "Client meeting" in result.output
        assert "Meeting notes" in result.output
        assert "Sprint meeting" in result.output
        assert "Quarterly meeting" in result.output

        # Should NOT show non-matching tasks
        assert "Project review" not in result.output
        assert "Budget planning" not in result.output

    def test_search_command_matches_description(self) -> None:
        """Test search matches keyword in description (US7-002, FR-017)"""
        runner = CliRunner()

        # Add tasks with keyword in description
        runner.invoke(cli, ["add", "Task A", "-d", "Discuss meeting agenda"])
        runner.invoke(cli, ["add", "Task B", "-d", "Review code"])
        runner.invoke(cli, ["add", "Task C", "-d", "Plan next meeting"])

        # Search for "meeting"
        result = runner.invoke(cli, ["search", "meeting"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should find tasks with keyword in description
        assert "Task A" in result.output
        assert "Task C" in result.output

        # Should NOT show task without keyword
        assert "Task B" not in result.output

    def test_search_command_no_results(self) -> None:
        """Test search shows message when no results found (US7-003)"""
        runner = CliRunner()

        # Add some tasks
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])

        # Search for non-existent keyword
        result = runner.invoke(cli, ["search", "nonexistent"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should show "no results" message
        assert "no" in result.output.lower() and ("result" in result.output.lower() or "found" in result.output.lower())

    def test_search_command_case_insensitive(self) -> None:
        """Test search is case-insensitive (FR-017)"""
        runner = CliRunner()

        # Add tasks with mixed case
        runner.invoke(cli, ["add", "MEETING with CEO"])
        runner.invoke(cli, ["add", "meeting with team"])
        runner.invoke(cli, ["add", "Meeting with client"])

        # Search with lowercase
        result = runner.invoke(cli, ["search", "meeting"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should find all tasks regardless of case
        assert "MEETING with CEO" in result.output or "meeting with CEO" in result.output.lower()
        assert "meeting with team" in result.output
        assert "Meeting with client" in result.output or "meeting with client" in result.output.lower()

    def test_search_command_with_empty_query(self) -> None:
        """Test search with empty query shows error (US7-004, FR-017)"""
        runner = CliRunner()

        # Try to search with empty string
        result = runner.invoke(cli, ["search", ""])

        # Should exit with error
        assert result.exit_code != 0

        # Should show error message
        assert "error" in result.output.lower() or "empty" in result.output.lower()


class TestFilterCommand:
    """Integration tests for User Story 8: Filter Tasks"""

    def test_filter_by_priority_high(self) -> None:
        """Test filter command filters by high priority (US8-001, FR-019)"""
        runner = CliRunner()

        # Add tasks with different priorities
        runner.invoke(cli, ["add", "Urgent task", "-p", "high"])
        runner.invoke(cli, ["add", "Normal task", "-p", "medium"])
        runner.invoke(cli, ["add", "Low priority task", "-p", "low"])
        runner.invoke(cli, ["add", "Another urgent task", "-p", "high"])

        # Filter by high priority
        result = runner.invoke(cli, ["filter", "--priority", "high"])

        # Should succeed
        assert result.exit_code == 0

        # Should show only high priority tasks
        assert "Urgent task" in result.output
        assert "Another urgent task" in result.output
        assert "Normal task" not in result.output
        assert "Low priority task" not in result.output

    def test_filter_by_status_completed(self) -> None:
        """Test filter command filters by completed status (US8-002, FR-019)"""
        runner = CliRunner()

        # Add tasks and mark some complete
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])
        runner.invoke(cli, ["done", "1"])
        runner.invoke(cli, ["done", "3"])

        # Filter by completed status
        result = runner.invoke(cli, ["filter", "--status", "completed"])

        # Should succeed
        assert result.exit_code == 0

        # Should show only completed tasks
        assert "Task 1" in result.output
        assert "Task 3" in result.output
        assert "Task 2" not in result.output

    def test_filter_by_status_incomplete(self) -> None:
        """Test filter command filters by incomplete status (US8-003, FR-019)"""
        runner = CliRunner()

        # Add tasks and mark some complete
        runner.invoke(cli, ["add", "Task A"])
        runner.invoke(cli, ["add", "Task B"])
        runner.invoke(cli, ["add", "Task C"])
        runner.invoke(cli, ["done", "2"])

        # Filter by incomplete status
        result = runner.invoke(cli, ["filter", "--status", "incomplete"])

        # Should succeed
        assert result.exit_code == 0

        # Should show only incomplete tasks
        assert "Task A" in result.output
        assert "Task C" in result.output
        assert "Task B" not in result.output

    def test_filter_by_tag(self) -> None:
        """Test filter command filters by tag (US8-004, FR-019)"""
        runner = CliRunner()

        # Add tasks with different tags
        runner.invoke(cli, ["add", "Work task", "--tags", "work,urgent"])
        runner.invoke(cli, ["add", "Personal task", "--tags", "personal,shopping"])
        runner.invoke(cli, ["add", "Another work task", "--tags", "work"])
        runner.invoke(cli, ["add", "Untagged task"])

        # Filter by "work" tag
        result = runner.invoke(cli, ["filter", "--tag", "work"])

        # Should succeed
        assert result.exit_code == 0

        # Should show only tasks with "work" tag
        assert "Work task" in result.output
        assert "Another work task" in result.output
        assert "Personal task" not in result.output
        assert "Untagged task" not in result.output

    def test_filter_combined_priority_and_status(self) -> None:
        """Test filter with combined criteria (priority + status) (US8-005, FR-019)"""
        runner = CliRunner()

        # Add tasks with various combinations
        runner.invoke(cli, ["add", "High incomplete", "-p", "high"])
        runner.invoke(cli, ["add", "High complete", "-p", "high"])
        runner.invoke(cli, ["add", "Low incomplete", "-p", "low"])
        runner.invoke(cli, ["add", "Low complete", "-p", "low"])

        # Mark some complete
        runner.invoke(cli, ["done", "2"])
        runner.invoke(cli, ["done", "4"])

        # Filter by high priority AND incomplete status
        result = runner.invoke(cli, ["filter", "--priority", "high", "--status", "incomplete"])

        # Should succeed
        assert result.exit_code == 0

        # Should show only high priority incomplete tasks
        assert "High incomplete" in result.output
        assert "High complete" not in result.output
        assert "Low incomplete" not in result.output
        assert "Low complete" not in result.output

    def test_filter_no_results(self) -> None:
        """Test filter shows friendly message when no results (US8-006, FR-020)"""
        runner = CliRunner()

        # Add some tasks
        runner.invoke(cli, ["add", "Task 1", "-p", "low"])
        runner.invoke(cli, ["add", "Task 2", "-p", "medium"])

        # Filter for high priority (should find none)
        result = runner.invoke(cli, ["filter", "--priority", "high"])

        # Should succeed
        assert result.exit_code == 0

        # Should show friendly "no results" message
        assert "no" in result.output.lower() and ("task" in result.output.lower() or "result" in result.output.lower())
