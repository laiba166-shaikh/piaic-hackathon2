"""Unit tests for recurring task functionality"""
import pytest
from datetime import datetime, timedelta
from src.core.models import Recurrence


class TestCalculateNextOccurrence:
    """Unit tests for calculate_next_occurrence() function (US10-005)"""

    def test_daily_recurrence_next_day(self) -> None:
        """Test daily recurrence returns next day"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 1, 1, 9, 0)  # Jan 1, 2025 at 9:00 AM
        next_due = calculate_next_occurrence(current_due, Recurrence.DAILY)

        assert next_due == datetime(2025, 1, 2, 9, 0)  # Jan 2, 2025 at 9:00 AM

    def test_weekly_recurrence_next_week(self) -> None:
        """Test weekly recurrence returns same day next week"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 1, 1, 9, 0)  # Wednesday Jan 1, 2025
        next_due = calculate_next_occurrence(current_due, Recurrence.WEEKLY)

        assert next_due == datetime(2025, 1, 8, 9, 0)  # Wednesday Jan 8, 2025

    def test_monthly_recurrence_next_month(self) -> None:
        """Test monthly recurrence returns same day next month"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 1, 15, 14, 30)  # Jan 15, 2025 at 2:30 PM
        next_due = calculate_next_occurrence(current_due, Recurrence.MONTHLY)

        assert next_due == datetime(2025, 2, 15, 14, 30)  # Feb 15, 2025 at 2:30 PM

    def test_monthly_recurrence_end_of_month_overflow(self) -> None:
        """Test monthly recurrence handles month-end dates (Jan 31 -> Feb 28)"""
        from src.core.recurring import calculate_next_occurrence

        # Jan 31, 2025 -> Feb doesn't have 31 days
        current_due = datetime(2025, 1, 31, 9, 0)
        next_due = calculate_next_occurrence(current_due, Recurrence.MONTHLY)

        # Should return Feb 28, 2025 (last day of Feb in non-leap year)
        assert next_due == datetime(2025, 2, 28, 9, 0)

    def test_monthly_recurrence_leap_year(self) -> None:
        """Test monthly recurrence handles leap year (Jan 31 -> Feb 29 in leap year)"""
        from src.core.recurring import calculate_next_occurrence

        # Jan 31, 2024 (2024 is a leap year)
        current_due = datetime(2024, 1, 31, 9, 0)
        next_due = calculate_next_occurrence(current_due, Recurrence.MONTHLY)

        # Should return Feb 29, 2024 (leap year)
        assert next_due == datetime(2024, 2, 29, 9, 0)

    def test_daily_recurrence_preserves_time(self) -> None:
        """Test daily recurrence preserves the time component"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 3, 15, 17, 45, 30)  # 5:45:30 PM
        next_due = calculate_next_occurrence(current_due, Recurrence.DAILY)

        assert next_due.hour == 17
        assert next_due.minute == 45
        assert next_due.second == 30

    def test_none_recurrence_raises_error(self) -> None:
        """Test NONE recurrence raises ValueError"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 1, 1, 9, 0)

        with pytest.raises(ValueError, match="Cannot calculate next occurrence for NONE"):
            calculate_next_occurrence(current_due, Recurrence.NONE)

    def test_none_due_date_raises_error(self) -> None:
        """Test None due_date raises ValueError"""
        from src.core.recurring import calculate_next_occurrence

        with pytest.raises(ValueError, match="due_date cannot be None"):
            calculate_next_occurrence(None, Recurrence.DAILY)  # type: ignore

    def test_monthly_recurrence_december_to_january(self) -> None:
        """Test monthly recurrence handles year boundary"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 12, 15, 9, 0)  # Dec 15, 2025
        next_due = calculate_next_occurrence(current_due, Recurrence.MONTHLY)

        assert next_due == datetime(2026, 1, 15, 9, 0)  # Jan 15, 2026

    def test_weekly_recurrence_year_boundary(self) -> None:
        """Test weekly recurrence handles year boundary"""
        from src.core.recurring import calculate_next_occurrence

        current_due = datetime(2025, 12, 29, 9, 0)  # Dec 29, 2025
        next_due = calculate_next_occurrence(current_due, Recurrence.WEEKLY)

        assert next_due == datetime(2026, 1, 5, 9, 0)  # Jan 5, 2026
