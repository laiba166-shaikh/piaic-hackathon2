"""
Validation and parsing functions for task inputs.

This module provides:
- Tag parsing from comma-separated strings
- Date parsing from string inputs
- Input validation helpers
"""
from datetime import datetime
from typing import List, Optional


def parse_tags(tags_input: str) -> List[str]:
    """
    Parse comma-separated tags into a list.

    Handles:
    - Comma-separated values: "work,urgent,personal"
    - Whitespace trimming: "work, urgent , personal"
    - Multi-word tags: "work,high priority,meeting"
    - Empty strings and removal of empty tags

    Args:
        tags_input: Comma-separated string of tags

    Returns:
        List of tag strings with whitespace trimmed

    Examples:
        >>> parse_tags("work,urgent,personal")
        ['work', 'urgent', 'personal']

        >>> parse_tags("work, high priority, meeting")
        ['work', 'high priority', 'meeting']

        >>> parse_tags("")
        []
    """
    if not tags_input or not tags_input.strip():
        return []

    # Split by comma
    tags = tags_input.split(",")

    # Strip whitespace from each tag and filter out empty strings
    tags = [tag.strip() for tag in tags if tag.strip()]

    return tags


def parse_due_date(date_input: str) -> datetime:
    """
    Parse a due date string into a datetime object.

    Supports formats:
    - YYYY-MM-DD (date only, time defaults to 00:00)
    - YYYY-MM-DD HH:MM (date and time)

    Args:
        date_input: Date string to parse

    Returns:
        datetime object

    Raises:
        ValueError: If date format is invalid

    Examples:
        >>> parse_due_date("2025-12-31")
        datetime(2025, 12, 31, 0, 0)

        >>> parse_due_date("2025-12-31 14:30")
        datetime(2025, 12, 31, 14, 30)
    """
    if not date_input or not date_input.strip():
        raise ValueError("Due date cannot be empty")

    date_input = date_input.strip()

    # Try date with time format first
    try:
        return datetime.strptime(date_input, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Try date only format
    try:
        return datetime.strptime(date_input, "%Y-%m-%d")
    except ValueError:
        pass

    raise ValueError(
        f"Invalid date format: '{date_input}'. "
        "Use YYYY-MM-DD or YYYY-MM-DD HH:MM format."
    )
