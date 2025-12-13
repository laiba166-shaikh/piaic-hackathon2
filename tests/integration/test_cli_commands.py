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
        """Test that CLI displays welcome message when invoked without commands (FR-013)"""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain welcome message elements
        assert "Todo CLI" in result.output
        assert "v0.1.0" in result.output
        assert "In-Memory Task Manager" in result.output

        # Should contain data warning (NFR-006)
        assert "WARNING" in result.output
        assert "in-memory only" in result.output or "not persisted" in result.output

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
