"""
Table rendering utilities for displaying tasks.

This module provides functions to render tasks in a formatted table
using Rich library for enhanced CLI output.
"""
from rich.table import Table
from rich.text import Text
from src.core.models import Task
from src.cli.rendering.colors import PRIORITY_INDICATORS, STATUS_INDICATORS, COLORS


def render_task_table(tasks: list[Task]) -> Table:
    """
    Render a list of tasks as a formatted Rich table.

    Args:
        tasks: List of tasks to display

    Returns:
        Rich Table object ready for printing

    Table Columns:
        - Status: [X] for complete, [ ] for incomplete
        - ID: Task unique identifier
        - Priority: [!] High, [-] Medium, [v] Low
        - Title: Task title (truncated if too long)
        - Tags: Comma-separated tags
        - Due: Due date (if set)
    """
    # Create table with custom styling
    table = Table(
        title="[bold cyan]Your Tasks[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold cyan",
    )

    # Define columns
    table.add_column("Status", justify="center", style="white", width=6)
    table.add_column("ID", justify="right", style="cyan", width=4)
    table.add_column("Priority", justify="center", style="white", width=8)
    table.add_column("Title", style="white", no_wrap=False, max_width=50)
    table.add_column("Tags", style="magenta", max_width=20)
    table.add_column("Due", style="yellow", width=12)

    # Add rows for each task
    for task in tasks:
        # Status indicator
        status_symbol, status_color = STATUS_INDICATORS[task.completed]
        status_text = Text(status_symbol, style=status_color)

        # ID
        task_id = str(task.id)

        # Priority indicator
        priority_symbol, priority_color = PRIORITY_INDICATORS[task.priority]
        priority_text = Text(priority_symbol, style=priority_color)

        # Title (with completion styling)
        if task.completed:
            title_text = Text(task.title, style="dim white strike")
        else:
            title_text = Text(task.title, style=COLORS["title"])

        # Tags
        tags_str = ", ".join(task.tags) if task.tags else ""
        tags_text = Text(tags_str, style=COLORS["tags"])

        # Due date
        if task.due_date:
            # Format: YYYY-MM-DD
            due_str = task.due_date.strftime("%Y-%m-%d")

            # Style based on due date status
            if task.is_overdue():
                due_text = Text(due_str, style=COLORS["overdue"])
            elif task.is_due_today():
                due_text = Text(due_str, style=COLORS["due_today"])
            else:
                due_text = Text(due_str, style=COLORS["due_date"])
        else:
            due_text = Text("", style="dim")

        # Add row to table
        table.add_row(
            status_text,
            task_id,
            priority_text,
            title_text,
            tags_text,
            due_text,
        )

    return table


def render_empty_message() -> Text:
    """
    Render a message when no tasks exist.

    Returns:
        Rich Text object with empty state message
    """
    message = Text()
    message.append("\n")
    message.append("No tasks found. ", style="yellow")
    message.append("Add your first task with: ", style="white")
    message.append("todo add \"Your task title\"", style="cyan bold")
    message.append("\n\n")
    return message
