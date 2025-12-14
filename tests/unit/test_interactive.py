"""
Unit tests for interactive shell mode.

Tests for:
- parse_command_line function
- display_interactive_welcome function
- run_interactive_shell function (with mocking)
"""
import pytest
from unittest.mock import MagicMock, patch
import click
from src.cli.interactive import parse_command_line, display_interactive_welcome, run_interactive_shell


class TestParseCommandLine:
    """Test command line parsing functionality"""

    def test_parse_simple_command(self) -> None:
        """Test parsing a simple command without arguments"""
        command, args = parse_command_line("list")
        assert command == "list"
        assert args == []

    def test_parse_command_with_quoted_argument(self) -> None:
        """Test parsing command with quoted string argument"""
        command, args = parse_command_line('add "Buy milk"')
        assert command == "add"
        assert args == ["Buy milk"]

    def test_parse_command_with_multiple_arguments(self) -> None:
        """Test parsing command with multiple arguments"""
        command, args = parse_command_line("update 1 --title New")
        assert command == "update"
        assert args == ["1", "--title", "New"]

    def test_parse_empty_line(self) -> None:
        """Test parsing empty line returns empty command"""
        command, args = parse_command_line("")
        assert command == ""
        assert args == []

    def test_parse_whitespace_only(self) -> None:
        """Test parsing whitespace-only line returns empty command"""
        command, args = parse_command_line("   ")
        assert command == ""
        assert args == []

    def test_parse_unclosed_quote_returns_empty(self) -> None:
        """Test parsing unclosed quote returns empty command"""
        command, args = parse_command_line('add "unclosed')
        assert command == ""
        assert args == []

    def test_parse_command_with_options(self) -> None:
        """Test parsing command with flag options"""
        command, args = parse_command_line("filter --priority high --overdue")
        assert command == "filter"
        assert args == ["--priority", "high", "--overdue"]

    def test_parse_complex_quoted_string(self) -> None:
        """Test parsing command with complex quoted string"""
        command, args = parse_command_line('add "Task with \\"quotes\\" inside"')
        assert command == "add"
        assert "quotes" in args[0]


class TestDisplayInteractiveWelcome:
    """Test welcome message display"""

    @patch("src.cli.interactive.console")
    def test_display_welcome_prints_panel(self, mock_console: MagicMock) -> None:
        """Test that welcome message is displayed"""
        display_interactive_welcome()
        mock_console.print.assert_called_once()
        # Verify a Panel was printed
        call_args = mock_console.print.call_args[0][0]
        from rich.panel import Panel
        assert isinstance(call_args, Panel)


class TestRunInteractiveShell:
    """Test interactive shell loop with mocking"""

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_exit_command_terminates_loop(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that 'exit' command terminates the loop"""
        mock_prompt.return_value = "exit"

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Verify goodbye message was printed
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_quit_command_terminates_loop(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that 'quit' command terminates the loop"""
        mock_prompt.return_value = "quit"

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Verify goodbye message was printed
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_empty_input_continues_loop(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that empty input continues the loop without error"""
        mock_prompt.side_effect = ["", "   ", "exit"]

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Should have processed all inputs
        assert mock_prompt.call_count == 3

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_help_command_shows_commands(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that 'help' command shows available commands"""
        mock_prompt.side_effect = ["help", "exit"]

        @click.command()
        def test_cmd() -> None:
            """Test command"""
            pass

        cli_group = click.Group()
        cli_group.add_command(test_cmd)

        run_interactive_shell(cli_group)

        # Verify help was displayed
        assert any("Available Commands" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_unknown_command_shows_error(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that unknown command shows error message"""
        mock_prompt.side_effect = ["unknown_cmd", "exit"]

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Verify error message was shown
        assert any("Unknown command" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_invalid_command_parsing_shows_error(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that invalid command parsing shows error"""
        mock_prompt.side_effect = ['add "unclosed', "exit"]

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Verify invalid command message
        assert any("Invalid command" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_keyboard_interrupt_exits_gracefully(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that Ctrl+C exits the shell gracefully"""
        mock_prompt.side_effect = KeyboardInterrupt()

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Verify goodbye message was printed
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_eof_exits_gracefully(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that EOF (Ctrl+D/Ctrl+Z) exits the shell gracefully"""
        mock_prompt.side_effect = EOFError()

        cli_group = click.Group()
        run_interactive_shell(cli_group)

        # Verify goodbye message was printed
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_command_execution_increments_count(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test successful command execution increments command count"""
        mock_prompt.side_effect = ["test_cmd", "exit"]

        @click.command()
        def test_cmd() -> None:
            """Test command that does nothing"""
            pass

        cli_group = click.Group()
        cli_group.add_command(test_cmd)

        run_interactive_shell(cli_group)

        # Verify the shell completed without error
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_click_exception_handling(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that ClickException is handled gracefully"""
        mock_prompt.side_effect = ["test_cmd", "exit"]

        @click.command()
        def test_cmd() -> None:
            """Test command that raises ClickException"""
            raise click.ClickException("Test error")

        cli_group = click.Group()
        cli_group.add_command(test_cmd)

        # Should not raise, should handle gracefully
        run_interactive_shell(cli_group)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_system_exit_handling(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that SystemExit is caught and loop continues"""
        mock_prompt.side_effect = ["test_cmd", "exit"]

        @click.command()
        def test_cmd() -> None:
            """Test command that raises SystemExit"""
            raise SystemExit(0)

        cli_group = click.Group()
        cli_group.add_command(test_cmd)

        # Should not exit the shell, should continue
        run_interactive_shell(cli_group)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_unexpected_exception_handling(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that unexpected exceptions are handled gracefully"""
        mock_prompt.side_effect = ["test_cmd", "exit"]

        @click.command()
        def test_cmd() -> None:
            """Test command that raises unexpected error"""
            raise RuntimeError("Unexpected error")

        cli_group = click.Group()
        cli_group.add_command(test_cmd)

        # Should not raise, should handle gracefully and continue
        run_interactive_shell(cli_group)

        # Verify shell completed (error was handled and we got to exit)
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)

    @patch("src.cli.interactive.Prompt.ask")
    @patch("src.cli.interactive.console")
    def test_click_abort_handling(self, mock_console: MagicMock, mock_prompt: MagicMock) -> None:
        """Test that click.Abort (Ctrl+C during command) is handled"""
        mock_prompt.side_effect = ["test_cmd", "exit"]

        @click.command()
        def test_cmd() -> None:
            """Test command that raises Abort"""
            raise click.Abort()

        cli_group = click.Group()
        cli_group.add_command(test_cmd)

        # Should handle abort gracefully and continue
        run_interactive_shell(cli_group)

        # Verify shell completed (abort was handled and we got to exit)
        assert any("Goodbye" in str(call) for call in mock_console.print.call_args_list)
