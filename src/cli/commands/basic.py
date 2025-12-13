"""
Basic CLI commands for task management.

This module provides the core commands:
- add: Create new tasks
- list: View all tasks
- update: Modify existing tasks
- delete: Remove tasks
- done: Mark tasks as complete
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from src.core.services import TaskService
from src.core.storage.memory import MemoryStorage
from src.config import get_logger

logger = get_logger(__name__)
console = Console()

# Global storage instance (in-memory for Phase 1)
# This will be replaced with dependency injection in Phase 2+
_storage = MemoryStorage()
_service = TaskService(_storage)


@click.command()
@click.argument("title")
@click.option(
    "-d",
    "--description",
    default=None,
    help="Optional task description",
)
def add(title: str, description: str | None) -> None:
    """
    Add a new task to your todo list.

    Creates a task with the given TITLE and optional description.
    The task will be assigned a unique ID and marked as incomplete.

    \b
    Examples:
        todo add "Buy groceries"
        todo add "Call dentist" -d "Schedule annual checkup"
        todo add "Submit report" --description "Q4 financial summary"

    \b
    Arguments:
        TITLE: The task title (required, 1-200 characters)

    \b
    Options:
        -d, --description TEXT: Optional task description (max 500 characters)
    """
    try:
        # Create task through service layer
        task = _service.create_task(title=title, description=description)

        # Display success message with task details (FR-009)
        success_text = Text()
        success_text.append("Task created successfully!\n\n", style="bold green")
        success_text.append("ID: ", style="cyan")
        success_text.append(f"{task.id}\n", style="bold white")
        success_text.append("Title: ", style="cyan")
        success_text.append(f"{task.title}\n", style="white")

        if task.description:
            success_text.append("Description: ", style="cyan")
            success_text.append(f"{task.description}\n", style="white")

        success_text.append("\nStatus: ", style="cyan")
        success_text.append("Incomplete", style="yellow")

        panel = Panel(
            success_text,
            title="[bold green]New Task[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)

        logger.info(f"User added task ID {task.id}: {task.title}")

    except ValueError as e:
        # Input validation error (FR-010)
        error_text = Text()
        error_text.append("Invalid input\n\n", style="bold red")
        error_text.append(str(e), style="white")

        panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(panel)

        logger.warning(f"Validation error in add command: {e}")
        raise click.ClickException(str(e))

    except Exception as e:
        # Unexpected error
        console.print(f"\n[red]Unexpected error: {e}[/red]\n")
        logger.error(f"Unexpected error in add command: {e}", exc_info=True)
        raise click.ClickException(str(e))
