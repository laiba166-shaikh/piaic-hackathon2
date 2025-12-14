"""
Color scheme and visual indicators for CLI rendering.

This module defines:
- Priority indicators (text-based for Windows compatibility)
- Status indicators for complete/incomplete tasks
- Color mappings for different task states
"""
from src.core.models import Priority

# Priority indicators: (symbol, color)
# Using text-based indicators instead of emojis for Windows compatibility
PRIORITY_INDICATORS = {
    Priority.HIGH: ("[!]", "red"),
    Priority.MEDIUM: ("[-]", "yellow"),
    Priority.LOW: ("[v]", "blue"),
}

# Status indicators: (symbol, color)
# Complete vs Incomplete task visual distinction
STATUS_INDICATORS = {
    True: ("[X]", "green"),   # Completed task
    False: ("[ ]", "white"),  # Incomplete task
}

# Color scheme for different elements
COLORS = {
    "task_id": "cyan",
    "title": "white",
    "description": "bright_black",
    "tags": "magenta",
    "due_date": "yellow",
    "overdue": "red bold",
    "due_today": "yellow bold",
    "completed": "green",
    "incomplete": "white",
}
