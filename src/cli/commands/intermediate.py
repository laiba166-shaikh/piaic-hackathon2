"""
Intermediate CLI commands for task management.

This module provides advanced search and filter commands:
- search: Find tasks by keyword
- filter: Filter tasks by criteria
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from src.core.services import TaskService
from src.config import get_logger

# Import shared storage instance from basic commands
# This ensures all commands work with the same data
from src.cli.commands.basic import _storage

logger = get_logger(__name__)
console = Console()

# Share the same service instance
_service = TaskService(_storage)


@click.command()
@click.argument("query")
def search(query: str) -> None:
    """
    Search for tasks by keyword in title or description.

    Searches all tasks for the given QUERY keyword (case-insensitive).
    Matches tasks where the keyword appears in either the title or description.

    \b
    Examples:
        todo search meeting
        todo search "project review"
        todo search urgent

    \b
    Arguments:
        QUERY: Search keyword (case-insensitive, matches substring)

    \b
    Returns:
        Formatted table of matching tasks or message if no results found
    """
    try:
        # Search tasks through service layer
        matching_tasks = _service.search_tasks(query)

        if not matching_tasks:
            # Display no results message (FR-018)
            message_text = Text()
            message_text.append("No tasks found matching your search.\\n\\n", style="bold yellow")
            message_text.append(f"Query: ", style="cyan")
            message_text.append(f"\"{query}\"\\n\\n", style="white")
            message_text.append("Try a different keyword or check your task list with ", style="white")
            message_text.append("todo list", style="cyan")

            panel = Panel(
                message_text,
                title="[bold yellow]No Results[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(panel)
            logger.info(f"Search for '{query}' returned 0 results")
        else:
            # Display matching tasks in formatted table
            from src.cli.rendering.table import render_task_table

            # Add search header
            header_text = Text()
            header_text.append("Search results for: ", style="cyan")
            header_text.append(f"\"{query}\"", style="bold white")
            header_text.append(f" ({len(matching_tasks)} found)", style="dim")

            console.print("\\n")
            console.print(header_text)

            table = render_task_table(matching_tasks)
            console.print(table)
            console.print("\\n")
            logger.info(f"Displayed {len(matching_tasks)} tasks matching '{query}'")

    except ValueError as e:
        # Input validation error (empty query)
        error_text = Text()
        error_text.append("Invalid search query\\n\\n", style="bold red")
        error_text.append(str(e), style="white")

        panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(panel)

        logger.warning(f"Validation error in search command: {e}")
        raise click.ClickException(str(e))

    except Exception as e:
        # Unexpected error
        console.print(f"\\n[red]Unexpected error: {e}[/red]\\n")
        logger.error(f"Unexpected error in search command: {e}", exc_info=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "-p",
    "--priority",
    type=click.Choice(["high", "medium", "low"], case_sensitive=False),
    default=None,
    help="Filter by priority level (high, medium, low)",
)
@click.option(
    "-s",
    "--status",
    type=click.Choice(["completed", "incomplete", "all"], case_sensitive=False),
    default=None,
    help="Filter by completion status (completed, incomplete, all)",
)
@click.option(
    "-t",
    "--tag",
    default=None,
    help="Filter by tag (tasks must have this tag)",
)
@click.option(
    "--overdue",
    is_flag=True,
    default=False,
    help="Filter to show only overdue tasks",
)
def filter(priority: str | None, status: str | None, tag: str | None, overdue: bool) -> None:
    """
    Filter tasks by priority, status, tags, or overdue status.

    Filters all tasks based on the provided criteria. Multiple filters can be
    combined (AND logic). At least one filter must be provided.

    \b
    Examples:
        todo filter --priority high
        todo filter --status completed
        todo filter --tag work
        todo filter --priority high --status incomplete
        todo filter --tag urgent --priority high
        todo filter --overdue
        todo filter --overdue --priority high

    \b
    Options:
        -p, --priority [high|medium|low]: Filter by priority level
        -s, --status [completed|incomplete|all]: Filter by completion status
        -t, --tag TEXT: Filter by tag (case-sensitive)
        --overdue: Show only overdue tasks

    \b
    Returns:
        Formatted table of matching tasks or message if no results found
    """
    try:
        # Parse priority
        from src.core.models import Priority

        priority_enum = None
        if priority:
            priority_map = {"high": Priority.HIGH, "medium": Priority.MEDIUM, "low": Priority.LOW}
            priority_enum = priority_map[priority.lower()]

        # Parse status
        completed_filter = None
        if status:
            if status.lower() == "completed":
                completed_filter = True
            elif status.lower() == "incomplete":
                completed_filter = False
            # "all" means no filter on completion status

        # Convert overdue flag to filter value
        overdue_filter = True if overdue else None

        # Validate at least one filter is provided
        if all(f is None for f in [priority_enum, completed_filter, tag, overdue_filter]):
            error_text = Text()
            error_text.append("No filter criteria provided\\n\\n", style="bold red")
            error_text.append(
                "Please specify at least one filter:\\n", style="white"
            )
            error_text.append("  --priority [high|medium|low]\\n", style="cyan")
            error_text.append("  --status [completed|incomplete|all]\\n", style="cyan")
            error_text.append("  --tag TAG_NAME\\n", style="cyan")
            error_text.append("  --overdue", style="cyan")

            panel = Panel(
                error_text,
                title="[bold red]Error[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print(panel)

            logger.warning("Filter command invoked with no criteria")
            raise click.ClickException("At least one filter criterion must be provided")

        # Filter tasks through service layer
        matching_tasks = _service.filter_tasks(
            priority=priority_enum, completed=completed_filter, tag=tag, overdue=overdue_filter
        )

        if not matching_tasks:
            # Display no results message (FR-020)
            message_text = Text()
            message_text.append("No tasks found matching your filters.\\n\\n", style="bold yellow")

            # Show active filters
            message_text.append("Active filters:\\n", style="cyan")
            if priority:
                message_text.append(f"  • Priority: {priority}\\n", style="white")
            if status:
                message_text.append(f"  • Status: {status}\\n", style="white")
            if tag:
                message_text.append(f"  • Tag: {tag}\\n", style="white")
            if overdue:
                message_text.append("  • Overdue: yes\\n", style="white")

            message_text.append("\\nTry different criteria or check your task list with ", style="white")
            message_text.append("todo list", style="cyan")

            panel = Panel(
                message_text,
                title="[bold yellow]No Results[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(panel)
            logger.info(f"Filter returned 0 results")
        else:
            # Display matching tasks in formatted table
            from src.cli.rendering.table import render_task_table

            # Add filter header
            header_text = Text()
            header_text.append("Filtered tasks", style="cyan")
            if priority or status or tag or overdue:
                header_text.append(" (", style="dim")
                filters = []
                if priority:
                    filters.append(f"priority={priority}")
                if status:
                    filters.append(f"status={status}")
                if tag:
                    filters.append(f"tag={tag}")
                if overdue:
                    filters.append("overdue")
                header_text.append(", ".join(filters), style="dim")
                header_text.append(")", style="dim")
            header_text.append(f" - {len(matching_tasks)} found", style="dim")

            console.print("\\n")
            console.print(header_text)

            table = render_task_table(matching_tasks)
            console.print(table)
            console.print("\\n")
            logger.info(f"Displayed {len(matching_tasks)} filtered tasks")

    except ValueError as e:
        # Input validation error
        error_text = Text()
        error_text.append("Invalid filter criteria\\n\\n", style="bold red")
        error_text.append(str(e), style="white")

        panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(panel)

        logger.warning(f"Validation error in filter command: {e}")
        raise click.ClickException(str(e))

    except click.ClickException:
        # Re-raise ClickException (already logged above)
        raise

    except Exception as e:
        # Unexpected error
        console.print(f"\\n[red]Unexpected error: {e}[/red]\\n")
        logger.error(f"Unexpected error in filter command: {e}", exc_info=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "-b",
    "--by",
    type=click.Choice(["priority", "title", "created", "due_date"], case_sensitive=False),
    default="created",
    help="Field to sort by (priority, title, created, due_date). Default: created",
)
@click.option(
    "-o",
    "--order",
    type=click.Choice(["asc", "desc"], case_sensitive=False),
    default="desc",
    help="Sort order: asc (ascending) or desc (descending). Default: desc",
)
def sort(by: str, order: str) -> None:
    """
    Sort tasks by priority, title, created date, or due date.

    Displays all tasks sorted by the specified field. Default order is descending
    (highest priority first, newest first, Z-A for title).

    \b
    Examples:
        todo sort --by priority              # High -> Medium -> Low
        todo sort --by priority --order asc  # Low -> Medium -> High
        todo sort --by title                 # Z-A (descending)
        todo sort --by title --order asc     # A-Z (ascending)
        todo sort --by created               # Newest first
        todo sort --by created --order asc   # Oldest first

    \b
    Sort Fields:
        priority: HIGH -> MEDIUM -> LOW (desc) or LOW -> MEDIUM -> HIGH (asc)
        title: Alphabetical order (case-insensitive)
        created: By creation timestamp
        due_date: By due date (tasks without due date appear last)

    \b
    Returns:
        Formatted table of sorted tasks or message if no tasks exist
    """
    try:
        # Determine ascending flag from order option
        ascending = order.lower() == "asc"

        # Sort tasks through service layer
        sorted_tasks = _service.sort_tasks(by=by.lower(), ascending=ascending)

        if not sorted_tasks:
            # Display no tasks message
            message_text = Text()
            message_text.append("No tasks to sort.\\n\\n", style="bold yellow")
            message_text.append("Add some tasks first with ", style="white")
            message_text.append("todo add \"Your task\"", style="cyan")

            panel = Panel(
                message_text,
                title="[bold yellow]No Tasks[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(panel)
            logger.info("Sort command invoked with no tasks")
        else:
            # Display sorted tasks in formatted table
            from src.cli.rendering.table import render_task_table

            # Add sort header
            header_text = Text()
            header_text.append("Tasks sorted by ", style="cyan")
            header_text.append(by, style="bold white")
            header_text.append(f" ({order})", style="dim")
            header_text.append(f" - {len(sorted_tasks)} tasks", style="dim")

            console.print("\\n")
            console.print(header_text)

            table = render_task_table(sorted_tasks)
            console.print(table)
            console.print("\\n")
            logger.info(f"Displayed {len(sorted_tasks)} tasks sorted by {by} ({order})")

    except ValueError as e:
        # Invalid sort field error
        error_text = Text()
        error_text.append("Invalid sort option\\n\\n", style="bold red")
        error_text.append(str(e), style="white")

        panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(panel)

        logger.warning(f"Validation error in sort command: {e}")
        raise click.ClickException(str(e))

    except Exception as e:
        # Unexpected error
        console.print(f"\\n[red]Unexpected error: {e}[/red]\\n")
        logger.error(f"Unexpected error in sort command: {e}", exc_info=True)
        raise click.ClickException(str(e))
