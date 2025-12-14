"""
Validation and parsing functions for task inputs.

This module provides:
- Tag parsing from comma-separated strings
- Input validation helpers
"""
from typing import List


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
