"""
CLI entry point for Phase 1 Todo App.

This module provides the main Click application with:
- Welcome message on startup
- Help command
- Command registration system
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from src.config import APP_NAME, APP_VERSION, APP_DESCRIPTION, get_logger

logger = get_logger(__name__)
console = Console()


def display_welcome_message() -> None:
    """
    Display welcome message on CLI startup (FR-013).

    Shows:
    - Application name and version
    - Brief description
    - Available commands hint
    - Data persistence warning (NFR-006)
    """
    welcome_text = Text()
    welcome_text.append(f"{APP_NAME} ", style="bold cyan")
    welcome_text.append(f"v{APP_VERSION}\n\n", style="cyan")
    welcome_text.append(f"{APP_DESCRIPTION}\n\n", style="white")
    welcome_text.append("WARNING: ", style="yellow bold")
    welcome_text.append("Data is stored in-memory only. All tasks will be lost when you exit.\n\n", style="yellow")
    welcome_text.append("Get started:\n", style="green bold")
    welcome_text.append("  * Run ", style="white")
    welcome_text.append("--help", style="cyan bold")
    welcome_text.append(" to see available commands\n", style="white")
    welcome_text.append("  * Run ", style="white")
    welcome_text.append("exit", style="cyan bold")
    welcome_text.append(" to quit the application", style="white")

    panel = Panel(
        welcome_text,
        title="[bold cyan]Welcome[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    logger.info("Displayed welcome message to user")


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=APP_VERSION, prog_name=APP_NAME)
def cli(ctx: click.Context) -> None:
    """
    Phase 1 CLI Todo App - In-Memory Task Manager

    A simple, feature-rich command-line todo application for managing tasks.

    \b
    Features:
    • Add, list, update, and delete tasks
    • Set priorities (high, medium, low)
    • Organize with tags
    • Set due dates and reminders
    • Search and filter tasks
    • Mark tasks as complete
    • Recurring task support

    \b
    Examples:
      todo add "Buy groceries" --priority high --tags shopping,personal
      todo list
      todo done 1
      todo delete 1

    \b
    Note: Data is stored in-memory only and will be lost on exit.
    """
    # If no command is provided, show welcome message
    if ctx.invoked_subcommand is None:
        display_welcome_message()
        logger.info("Todo CLI started")


@cli.command()
def exit() -> None:
    """Exit the Todo CLI application (FR-012)."""
    console.print("\n[cyan]Goodbye! All tasks have been cleared from memory.[/cyan]\n")
    logger.info("Todo CLI exiting - user requested exit")
    raise SystemExit(0)


def main() -> None:
    """
    Main entry point for the CLI application.

    Called when running: python -m src.cli.main
    """
    try:
        cli()
    except SystemExit:
        # Normal exit, don't log as error
        pass
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
