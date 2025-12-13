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


@click.command()
@click.argument("task_id", type=int)
def done(task_id: int) -> None:
    """
    Mark a task as complete.

    Marks the task with the given ID as completed. Completed tasks are
    visually distinguished in the task list.

    \\b
    Examples:
        todo done 1
        todo done 5

    \\b
    Arguments:
        TASK_ID: The ID of the task to mark as complete (positive integer)
    """
    try:
        # Mark task as complete through service layer
        task = _service.mark_complete(task_id)

        # Display success message (FR-009)
        success_text = Text()
        success_text.append("Task marked as completed!\n\n", style="bold green")
        success_text.append("ID: ", style="cyan")
        success_text.append(f"{task.id}\n", style="bold white")
        success_text.append("Title: ", style="cyan")
        success_text.append(f"{task.title}\n", style="white")
        success_text.append("\nStatus: ", style="cyan")
        success_text.append("Completed", style="green")

        panel = Panel(
            success_text,
            title="[bold green]Task Complete[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)

        logger.info(f"User marked task ID {task.id} as complete")

    except ValueError as e:
        # Input validation error
        error_text = Text()
        error_text.append("Invalid input\\n\\n", style="bold red")
        error_text.append(str(e), style="white")

        panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(panel)

        logger.warning(f"Validation error in done command: {e}")
        raise click.ClickException(str(e))

    except Exception as e:
        # Unexpected error (includes TaskNotFoundError)
        console.print(f"\\n[red]Error: {e}[/red]\\n")
        logger.error(f"Error in done command: {e}", exc_info=True)
        raise click.ClickException(str(e))


@click.command()
@click.argument("task_id", type=int)
def undone(task_id: int) -> None:
    """
    Mark a task as incomplete.

    Marks the task with the given ID as not completed. Use this to reopen
    a task that was previously marked as complete.

    \\b
    Examples:
        todo undone 1
        todo undone 5

    \\b
    Arguments:
        TASK_ID: The ID of the task to mark as incomplete (positive integer)
    """
    try:
        # Mark task as incomplete through service layer
        task = _service.mark_incomplete(task_id)

        # Display success message (FR-009)
        success_text = Text()
        success_text.append("Task marked as incomplete!\n\n", style="bold yellow")
        success_text.append("ID: ", style="cyan")
        success_text.append(f"{task.id}\n", style="bold white")
        success_text.append("Title: ", style="cyan")
        success_text.append(f"{task.title}\n", style="white")
        success_text.append("\nStatus: ", style="cyan")
        success_text.append("Incomplete", style="yellow")

        panel = Panel(
            success_text,
            title="[bold yellow]Task Reopened[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print(panel)

        logger.info(f"User marked task ID {task.id} as incomplete")

    except ValueError as e:
        # Input validation error
        error_text = Text()
        error_text.append("Invalid input\\n\\n", style="bold red")
        error_text.append(str(e), style="white")

        panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(panel)

        logger.warning(f"Validation error in undone command: {e}")
        raise click.ClickException(str(e))

    except Exception as e:
        # Unexpected error (includes TaskNotFoundError)
        console.print(f"\\n[red]Error: {e}[/red]\\n")
        logger.error(f"Error in undone command: {e}", exc_info=True)
        raise click.ClickException(str(e))


@click.command()
def list() -> None:
    """
    List all tasks in your todo list.

    Displays all tasks in a formatted table showing:
    - Status: [X] for complete, [ ] for incomplete
    - ID: Unique task identifier
    - Priority: [!] High, [-] Medium, [v] Low
    - Title: Task title
    - Tags: Task categories/labels
    - Due: Due date (if set)

    Tasks are sorted by creation date (newest first).

    \b
    Examples:
        todo list

    \b
    Returns:
        Formatted table of all tasks or empty state message
    """
    try:
        # Retrieve all tasks through service layer
        tasks = _service.list_all()

        if not tasks:
            # Display empty state message
            from src.cli.rendering.table import render_empty_message

            message = render_empty_message()
            console.print(message)
            logger.info("Displayed empty task list")
        else:
            # Display tasks in formatted table
            from src.cli.rendering.table import render_task_table

            table = render_task_table(tasks)
            console.print("\n")
            console.print(table)
            console.print("\n")
            logger.info(f"Displayed {len(tasks)} tasks")

    except Exception as e:
        # Unexpected error
        console.print(f"\n[red]Unexpected error: {e}[/red]\n")
        logger.error(f"Unexpected error in list command: {e}", exc_info=True)
        raise click.ClickException(str(e))
