"""
Recurring task utilities.

This module provides functions for calculating next occurrences of recurring tasks.
"""
from datetime import datetime
from calendar import monthrange
from src.cli.logics.models import Recurrence
from src.config import get_logger

logger = get_logger(__name__)


def calculate_next_occurrence(due_date: datetime | None, recurrence: Recurrence) -> datetime:
    """
    Calculate the next occurrence date for a recurring task.

    Args:
        due_date: Current due date of the task
        recurrence: Recurrence pattern (DAILY, WEEKLY, MONTHLY)

    Returns:
        datetime: Next occurrence date

    Raises:
        ValueError: If due_date is None or recurrence is NONE

    Business Rules:
        - DAILY: Adds 1 day
        - WEEKLY: Adds 7 days
        - MONTHLY: Adds 1 month, handling month-end edge cases
        - Time component is preserved
        - Month-end dates (e.g., Jan 31) are capped to the last day of the next month
    """
    if due_date is None:
        logger.warning("Cannot calculate next occurrence: due_date is None")
        raise ValueError("due_date cannot be None for recurring tasks")

    if recurrence == Recurrence.NONE:
        logger.warning("Cannot calculate next occurrence for NONE recurrence")
        raise ValueError("Cannot calculate next occurrence for NONE recurrence")

    if recurrence == Recurrence.DAILY:
        # Add 1 day
        next_date = due_date.replace(day=due_date.day + 1) if due_date.day < 28 else _add_days(due_date, 1)
        logger.info(f"Daily recurrence: {due_date} -> {next_date}")
        return next_date

    elif recurrence == Recurrence.WEEKLY:
        # Add 7 days
        next_date = _add_days(due_date, 7)
        logger.info(f"Weekly recurrence: {due_date} -> {next_date}")
        return next_date

    elif recurrence == Recurrence.MONTHLY:
        # Add 1 month, handling edge cases
        next_date = _add_months(due_date, 1)
        logger.info(f"Monthly recurrence: {due_date} -> {next_date}")
        return next_date

    # Should never reach here due to enum constraints
    raise ValueError(f"Unknown recurrence type: {recurrence}")


def _add_days(dt: datetime, days: int) -> datetime:
    """Add days to a datetime, handling month/year boundaries."""
    from datetime import timedelta
    return dt + timedelta(days=days)


def _add_months(dt: datetime, months: int) -> datetime:
    """
    Add months to a datetime, handling month-end edge cases.

    For example:
    - Jan 31 + 1 month = Feb 28 (or 29 in leap year)
    - Mar 31 + 1 month = Apr 30
    """
    # Calculate target year and month
    new_month = dt.month + months
    new_year = dt.year

    while new_month > 12:
        new_month -= 12
        new_year += 1

    while new_month < 1:
        new_month += 12
        new_year -= 1

    # Get the maximum day for the target month
    max_day = monthrange(new_year, new_month)[1]

    # Cap the day to the max day of the target month
    new_day = min(dt.day, max_day)

    return dt.replace(year=new_year, month=new_month, day=new_day)
