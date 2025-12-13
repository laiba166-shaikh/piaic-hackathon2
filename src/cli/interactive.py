"""
Interactive shell mode for the CLI application.

This module provides an interactive REPL (Read-Eval-Print Loop) that allows
users to execute multiple commands in a single session without losing data
between commands.
"""
import shlex
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from src.config import get_logger, APP_NAME, APP_VERSION

logger = get_logger(__name__)
console = Console()


def display_interactive_welcome() -> None:
    """
    Display welcome message for interactive mode.

    Shows:
    - Application name and version
    - Interactive mode indicator
    - Available commands hint
    - How to exit
    """
    welcome_text = Text()
    welcome_text.append(f"{APP_NAME} ", style="bold cyan")
    welcome_text.append(f"v{APP_VERSION}\n", style="cyan")
    welcome_text.append("Interactive Mode\n\n", style="bold green")
    welcome_text.append("You are now in interactive mode. ", style="white")
    welcome_text.append("Tasks will persist during this session.\n\n", style="white")
    welcome_text.append("Available commands:\n", style="green bold")
    welcome_text.append("  • ", style="white")
    welcome_text.append("add \"task title\"", style="cyan bold")
    welcome_text.append(" - Add a new task\n", style="white")
    welcome_text.append("  • ", style="white")
    welcome_text.append("list", style="cyan bold")
    welcome_text.append(" - View all tasks\n", style="white")
    welcome_text.append("  • ", style="white")
    welcome_text.append("help", style="cyan bold")
    welcome_text.append(" - Show available commands\n", style="white")
    welcome_text.append("  • ", style="white")
    welcome_text.append("exit", style="cyan bold")
    welcome_text.append(" or ", style="white")
    welcome_text.append("quit", style="cyan bold")
    welcome_text.append(" - Exit interactive mode\n\n", style="white")
    welcome_text.append("TIP: ", style="yellow bold")
    welcome_text.append("Press ", style="white")
    welcome_text.append("Ctrl+C", style="cyan")
    welcome_text.append(" to exit at any time", style="white")

    panel = Panel(
        welcome_text,
        title="[bold cyan]Welcome[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    logger.info("Started interactive mode")


def parse_command_line(line: str) -> tuple[str, list[str]]:
    """
    Parse a command line into command name and arguments.

    Args:
        line: Raw command line input

    Returns:
        Tuple of (command_name, arguments_list)

    Examples:
        >>> parse_command_line('add "Buy milk"')
        ('add', ['Buy milk'])
        >>> parse_command_line('list')
        ('list', [])
    """
    try:
        # Use shlex to properly handle quoted strings
        parts = shlex.split(line)
        if not parts:
            return ("", [])

        command = parts[0]
        args = parts[1:]
        return (command, args)
    except ValueError as e:
        # Handle unclosed quotes, etc.
        logger.warning(f"Failed to parse command line: {e}")
        return ("", [])


def run_interactive_shell(cli_group: click.Group) -> None:
    """
    Run the interactive shell loop.

    This function:
    1. Displays welcome message
    2. Shows a prompt for user input
    3. Parses and executes commands
    4. Repeats until user exits

    Args:
        cli_group: The Click group containing all commands
    """
    display_interactive_welcome()

    # Keep track of session
    command_count = 0

    while True:
        try:
            # Show prompt and get input
            line = Prompt.ask("\n[bold cyan]todo[/bold cyan]")

            # Skip empty lines
            if not line.strip():
                continue

            # Parse command
            command, args = parse_command_line(line.strip())

            if not command:
                console.print("[yellow]Invalid command. Type 'help' for available commands.[/yellow]")
                continue

            # Handle exit/quit commands
            if command.lower() in ["exit", "quit"]:
                console.print("\n[cyan]Goodbye! Exiting interactive mode.[/cyan]\n")
                logger.info(f"Interactive session ended. Executed {command_count} commands.")
                break

            # Handle help command
            if command.lower() == "help":
                console.print("\n[bold cyan]Available Commands:[/bold cyan]")
                for name, cmd in cli_group.commands.items():
                    if name not in ["exit"]:  # Don't show the exit command from CLI
                        help_text = cmd.get_short_help_str(limit=60)
                        console.print(f"  [cyan]{name:12}[/cyan] - {help_text}")
                console.print(f"  [cyan]{'exit':12}[/cyan] - Exit interactive mode")
                console.print(f"  [cyan]{'quit':12}[/cyan] - Exit interactive mode")
                console.print(f"  [cyan]{'help':12}[/cyan] - Show this help message\n")
                continue

            # Check if command exists
            if command not in cli_group.commands:
                console.print(f"[red]Unknown command: '{command}'. Type 'help' for available commands.[/red]")
                continue

            # Execute the command
            try:
                # Get the command
                cmd = cli_group.commands[command]

                # Invoke the command using Click's built-in parsing
                # This properly handles arguments, options, and all Click features
                cmd.main(args, standalone_mode=False, obj=cli_group)
                command_count += 1

            except click.ClickException as e:
                # Click exceptions are already formatted nicely
                e.show()
            except click.Abort:
                # User pressed Ctrl+C during command execution
                console.print("\n[yellow]Command cancelled.[/yellow]")
            except SystemExit:
                # Some commands might call sys.exit() - catch and continue
                pass
            except Exception as e:
                # Unexpected error
                console.print(f"[red]Error executing command: {e}[/red]")
                logger.error(f"Error in interactive mode: {e}", exc_info=True)

        except KeyboardInterrupt:
            # User pressed Ctrl+C at the prompt
            console.print("\n\n[cyan]Goodbye! Exiting interactive mode.[/cyan]\n")
            logger.info(f"Interactive session interrupted. Executed {command_count} commands.")
            break

        except EOFError:
            # End of input (Ctrl+D on Unix, Ctrl+Z on Windows)
            console.print("\n\n[cyan]Goodbye! Exiting interactive mode.[/cyan]\n")
            logger.info(f"Interactive session ended (EOF). Executed {command_count} commands.")
            break
