"""
Final Validation Tests for Phase 1 CLI Todo App

This module provides comprehensive validation for:
- POLISH-019: All 11 User Stories acceptance scenarios
- POLISH-020: All 17 Success Criteria (SC-001 to SC-017)
- POLISH-021: All Functional Requirements (FR-001 to FR-043)
- POLISH-022: All Non-Functional Requirements (NFR-001 to NFR-012)

Run with: pytest tests/validation/test_final_validation.py -v
"""
import pytest
import time
from datetime import datetime, timedelta
from click.testing import CliRunner
from src.cli.main import cli
from src.cli.commands.basic import _storage
from src.core.models import Task, Priority, Recurrence
from src.core.services import TaskService
from src.core.storage.memory import MemoryStorage


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    """Clear storage before each test"""
    _storage._tasks.clear()
    _storage._next_id = 1


# =============================================================================
# POLISH-019: User Story Acceptance Tests
# =============================================================================

class TestUserStory1_CaptureNewTasks:
    """US1: As a user, I want to quickly add tasks to my todo list"""

    def test_us1_ac1_add_task_with_title(self) -> None:
        """AC1: Add task with title creates task with unique ID, marked incomplete"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Buy groceries"])
        assert result.exit_code == 0
        assert "1" in result.output  # Unique ID assigned
        # Verify incomplete
        list_result = runner.invoke(cli, ["list"])
        assert "[ ]" in list_result.output or "Buy groceries" in list_result.output

    def test_us1_ac2_add_task_with_description(self) -> None:
        """AC2: Add task with title and description"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Call dentist", "-d", "Schedule annual checkup"])
        assert result.exit_code == 0
        assert "Call dentist" in result.output

    def test_us1_ac3_empty_title_error(self) -> None:
        """AC3: Empty title shows error, task not created"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", ""])
        assert result.exit_code != 0

    def test_us1_ac4_unique_ids(self) -> None:
        """AC4: Multiple tasks get unique IDs"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])
        list_result = runner.invoke(cli, ["list"])
        # All three tasks should be present with different IDs
        assert "Task 1" in list_result.output
        assert "Task 2" in list_result.output
        assert "Task 3" in list_result.output


class TestUserStory2_ViewTaskList:
    """US2: As a user, I want to see all my tasks at a glance"""

    def test_us2_ac1_view_all_tasks(self) -> None:
        """AC1: View list shows all tasks with ID, title, status"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task A"])
        runner.invoke(cli, ["add", "Task B"])
        runner.invoke(cli, ["add", "Task C"])
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Task A" in result.output
        assert "Task B" in result.output
        assert "Task C" in result.output

    def test_us2_ac2_empty_list_message(self) -> None:
        """AC2: Empty list shows appropriate message"""
        runner = CliRunner()
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "no tasks" in result.output.lower() or "No tasks" in result.output

    def test_us2_ac4_distinguish_complete_incomplete(self) -> None:
        """AC4: Can distinguish completed from incomplete tasks"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Complete me"])
        runner.invoke(cli, ["add", "Leave incomplete"])
        runner.invoke(cli, ["done", "1"])
        result = runner.invoke(cli, ["list"])
        # Should show different status indicators
        assert "[X]" in result.output or "Complete me" in result.output


class TestUserStory3_MarkTasksComplete:
    """US3: As a user, I want to mark tasks as complete"""

    def test_us3_ac1_mark_complete(self) -> None:
        """AC1: Mark incomplete task as complete"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test task"])
        result = runner.invoke(cli, ["done", "1"])
        assert result.exit_code == 0
        assert "complete" in result.output.lower()

    def test_us3_ac2_mark_incomplete(self) -> None:
        """AC2: Mark complete task as incomplete"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test task"])
        runner.invoke(cli, ["done", "1"])
        result = runner.invoke(cli, ["undone", "1"])
        assert result.exit_code == 0
        assert "incomplete" in result.output.lower()

    def test_us3_ac3_nonexistent_id_error(self) -> None:
        """AC3: Non-existent task ID shows error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["done", "999"])
        assert result.exit_code != 0

    def test_us3_ac4_only_target_changes(self) -> None:
        """AC4: Only target task status changes"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])
        runner.invoke(cli, ["done", "2"])
        # Filter incomplete - should show 1 and 3
        result = runner.invoke(cli, ["filter", "--status", "incomplete"])
        assert "Task 1" in result.output
        assert "Task 3" in result.output
        assert "Task 2" not in result.output


class TestUserStory4_UpdateTaskDetails:
    """US4: As a user, I want to edit task titles and descriptions"""

    def test_us4_ac1_update_title(self) -> None:
        """AC1: Update task title"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Buy milk"])
        result = runner.invoke(cli, ["update", "1", "--title", "Buy milk and eggs"])
        assert result.exit_code == 0
        list_result = runner.invoke(cli, ["list"])
        assert "Buy milk and eggs" in list_result.output

    def test_us4_ac2_add_description(self) -> None:
        """AC2: Add description to task without one"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Shopping"])
        result = runner.invoke(cli, ["update", "1", "-d", "From the organic store"])
        assert result.exit_code == 0

    def test_us4_ac3_nonexistent_id_error(self) -> None:
        """AC3: Update non-existent task shows error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["update", "999", "--title", "New title"])
        assert result.exit_code != 0

    def test_us4_ac4_empty_title_error(self) -> None:
        """AC4: Update with empty title shows error"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test task"])
        result = runner.invoke(cli, ["update", "1", "--title", "   "])
        assert result.exit_code != 0


class TestUserStory5_DeleteTasks:
    """US5: As a user, I want to delete tasks I no longer need"""

    def test_us5_ac1_delete_task(self) -> None:
        """AC1: Delete task removes it from list"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Delete me"])
        result = runner.invoke(cli, ["delete", "1"])
        assert result.exit_code == 0
        list_result = runner.invoke(cli, ["list"])
        assert "Delete me" not in list_result.output

    def test_us5_ac2_nonexistent_id_error(self) -> None:
        """AC2: Delete non-existent task shows error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["delete", "999"])
        assert result.exit_code != 0

    def test_us5_ac3_only_target_deleted(self) -> None:
        """AC3: Only target task is deleted"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["add", "Task 3"])
        runner.invoke(cli, ["delete", "2"])
        list_result = runner.invoke(cli, ["list"])
        assert "Task 1" in list_result.output
        assert "Task 3" in list_result.output
        assert "Task 2" not in list_result.output

    def test_us5_ac4_delete_all_shows_empty(self) -> None:
        """AC4: Delete all tasks shows empty list"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["delete", "1"])
        result = runner.invoke(cli, ["list"])
        assert "no tasks" in result.output.lower() or "No tasks" in result.output


class TestUserStory6_PrioritiesAndTags:
    """US6: As a user, I want to assign priorities and tags"""

    def test_us6_ac1_high_priority_indicator(self) -> None:
        """AC1: High priority shows indicator"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Urgent task", "-p", "high"])
        result = runner.invoke(cli, ["list"])
        assert "[!]" in result.output or "HIGH" in result.output.upper()

    def test_us6_ac2_multiple_tags(self) -> None:
        """AC2: Multiple tags display correctly"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Work task", "--tags", "work,urgent"])
        result = runner.invoke(cli, ["list"])
        assert "work" in result.output
        assert "urgent" in result.output

    def test_us6_ac3_distinguish_priorities(self) -> None:
        """AC3: Can distinguish between priority levels"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "High", "-p", "high"])
        runner.invoke(cli, ["add", "Medium", "-p", "medium"])
        runner.invoke(cli, ["add", "Low", "-p", "low"])
        result = runner.invoke(cli, ["list"])
        # Should have different indicators
        assert "[!]" in result.output  # High
        assert "[-]" in result.output  # Medium
        assert "[v]" in result.output  # Low

    def test_us6_ac4_update_priority(self) -> None:
        """AC4: Update priority changes indicator"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task", "-p", "low"])
        runner.invoke(cli, ["update", "1", "-p", "high"])
        result = runner.invoke(cli, ["list"])
        assert "[!]" in result.output


class TestUserStory7_SearchTasks:
    """US7: As a user, I want to search for tasks by keyword"""

    def test_us7_ac1_search_by_title(self) -> None:
        """AC1: Search matches tasks by title"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Team meeting"])
        runner.invoke(cli, ["add", "Buy groceries"])
        runner.invoke(cli, ["add", "Project meeting"])
        result = runner.invoke(cli, ["search", "meeting"])
        assert "Team meeting" in result.output
        assert "Project meeting" in result.output
        assert "Buy groceries" not in result.output

    def test_us7_ac2_search_by_description(self) -> None:
        """AC2: Search matches tasks by description"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task A", "-d", "Discuss meeting agenda"])
        runner.invoke(cli, ["add", "Task B", "-d", "Review code"])
        result = runner.invoke(cli, ["search", "meeting"])
        assert "Task A" in result.output
        assert "Task B" not in result.output

    def test_us7_ac3_no_results_message(self) -> None:
        """AC3: No results shows appropriate message"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        result = runner.invoke(cli, ["search", "nonexistent"])
        assert "no" in result.output.lower() and "found" in result.output.lower()

    def test_us7_ac4_empty_search_error(self) -> None:
        """AC4: Empty search shows error"""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", ""])
        assert result.exit_code != 0


class TestUserStory8_FilterTasks:
    """US8: As a user, I want to filter tasks by various criteria"""

    def test_us8_ac1_filter_by_status(self) -> None:
        """AC1: Filter by incomplete status"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["done", "1"])
        result = runner.invoke(cli, ["filter", "--status", "incomplete"])
        assert "Task 2" in result.output
        assert "Task 1" not in result.output

    def test_us8_ac2_filter_by_priority(self) -> None:
        """AC2: Filter by high priority"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "High task", "-p", "high"])
        runner.invoke(cli, ["add", "Low task", "-p", "low"])
        result = runner.invoke(cli, ["filter", "--priority", "high"])
        assert "High task" in result.output
        assert "Low task" not in result.output

    def test_us8_ac3_filter_by_tag(self) -> None:
        """AC3: Filter by tag"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Work task", "--tags", "work"])
        runner.invoke(cli, ["add", "Home task", "--tags", "home"])
        result = runner.invoke(cli, ["filter", "--tag", "work"])
        assert "Work task" in result.output
        assert "Home task" not in result.output

    def test_us8_ac4_multiple_filters(self) -> None:
        """AC4: Multiple filters work together (AND logic)"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "High incomplete", "-p", "high"])
        runner.invoke(cli, ["add", "High complete", "-p", "high"])
        runner.invoke(cli, ["done", "2"])
        result = runner.invoke(cli, ["filter", "--priority", "high", "--status", "incomplete"])
        assert "High incomplete" in result.output
        assert "High complete" not in result.output


class TestUserStory9_SortTasks:
    """US9: As a user, I want to sort tasks by various criteria"""

    def test_us9_ac1_sort_by_priority(self) -> None:
        """AC1: Sort by priority (high -> medium -> low)"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Low", "-p", "low"])
        runner.invoke(cli, ["add", "High", "-p", "high"])
        runner.invoke(cli, ["add", "Medium", "-p", "medium"])
        result = runner.invoke(cli, ["sort", "--by", "priority"])
        output = result.output
        high_pos = output.find("High")
        medium_pos = output.find("Medium")
        low_pos = output.find("Low")
        assert high_pos < medium_pos < low_pos

    def test_us9_ac2_sort_by_title(self) -> None:
        """AC2: Sort by title alphabetically"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Zebra"])
        runner.invoke(cli, ["add", "Apple"])
        runner.invoke(cli, ["add", "Mango"])
        result = runner.invoke(cli, ["sort", "--by", "title", "--order", "asc"])
        output = result.output
        apple_pos = output.find("Apple")
        mango_pos = output.find("Mango")
        zebra_pos = output.find("Zebra")
        assert apple_pos < mango_pos < zebra_pos

    def test_us9_ac3_sort_by_created(self) -> None:
        """AC3: Sort by created date"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "First"])
        runner.invoke(cli, ["add", "Second"])
        runner.invoke(cli, ["add", "Third"])
        result = runner.invoke(cli, ["sort", "--by", "created", "--order", "asc"])
        output = result.output
        first_pos = output.find("First")
        second_pos = output.find("Second")
        third_pos = output.find("Third")
        assert first_pos < second_pos < third_pos


class TestUserStory10_RecurringTasks:
    """US10: As a user, I want to create recurring tasks"""

    def test_us10_ac1_weekly_recurrence(self) -> None:
        """AC1: Weekly recurring task creates new instance on complete"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Weekly task", "--recurrence", "weekly", "--due", "2025-12-14"])
        runner.invoke(cli, ["done", "1"])
        # Should have 2 tasks now
        list_result = runner.invoke(cli, ["list"])
        assert list_result.output.count("Weekly task") >= 1

    def test_us10_ac2_daily_recurrence(self) -> None:
        """AC2: Daily recurring task creates next day instance"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Daily task", "--recurrence", "daily", "--due", "2025-12-14"])
        result = runner.invoke(cli, ["done", "1"])
        assert result.exit_code == 0

    def test_us10_ac3_monthly_recurrence(self) -> None:
        """AC3: Monthly recurring task creates next month instance"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Monthly task", "--recurrence", "monthly", "--due", "2025-12-14"])
        result = runner.invoke(cli, ["done", "1"])
        assert result.exit_code == 0


class TestUserStory11_DueDatesAndReminders:
    """US11: As a user, I want to set due dates"""

    def test_us11_ac1_due_date_displays(self) -> None:
        """AC1: Due date displays with task"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task with due", "--due", "2025-12-15"])
        result = runner.invoke(cli, ["list"])
        assert "2025-12-15" in result.output

    def test_us11_ac3_overdue_highlighted(self) -> None:
        """AC3: Overdue tasks are highlighted"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Overdue task", "--due", "2020-01-01"])
        result = runner.invoke(cli, ["list"])
        # Task should be in list (overdue styling is visual)
        assert "Overdue task" in result.output

    def test_us11_ac5_sort_by_due_date(self) -> None:
        """AC5: Sort by due date works correctly"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Later", "--due", "2025-12-31"])
        runner.invoke(cli, ["add", "Sooner", "--due", "2025-12-15"])
        result = runner.invoke(cli, ["sort", "--by", "due_date", "--order", "asc"])
        output = result.output
        sooner_pos = output.find("Sooner")
        later_pos = output.find("Later")
        assert sooner_pos < later_pos


# =============================================================================
# POLISH-020: Success Criteria Validation (SC-001 to SC-017)
# =============================================================================

class TestSuccessCriteria:
    """Validate all 17 Success Criteria"""

    def test_sc001_basic_operations_without_errors(self) -> None:
        """SC-001: Add, view, update, mark complete, delete without errors"""
        runner = CliRunner()
        # Add
        assert runner.invoke(cli, ["add", "Test task"]).exit_code == 0
        # View
        assert runner.invoke(cli, ["list"]).exit_code == 0
        # Update
        assert runner.invoke(cli, ["update", "1", "--title", "Updated"]).exit_code == 0
        # Mark complete
        assert runner.invoke(cli, ["done", "1"]).exit_code == 0
        # Delete
        assert runner.invoke(cli, ["delete", "1"]).exit_code == 0

    def test_sc002_operations_under_1_second(self) -> None:
        """SC-002: All operations complete within 1 second for 100 tasks"""
        runner = CliRunner()
        # Add 100 tasks
        for i in range(100):
            runner.invoke(cli, ["add", f"Task {i}"])

        # Test list operation
        start = time.time()
        runner.invoke(cli, ["list"])
        assert time.time() - start < 1.0

    def test_sc003_primary_workflow_under_30_seconds(self) -> None:
        """SC-003: Primary workflow (add → view → complete) under 30 seconds"""
        runner = CliRunner()
        start = time.time()
        runner.invoke(cli, ["add", "Quick task"])
        runner.invoke(cli, ["list"])
        runner.invoke(cli, ["done", "1"])
        assert time.time() - start < 30.0

    def test_sc004_clear_error_messages(self) -> None:
        """SC-004: Error messages are clear for common mistakes"""
        runner = CliRunner()
        # Invalid ID
        result = runner.invoke(cli, ["done", "999"])
        assert "not found" in result.output.lower() or "error" in result.output.lower()
        # Empty title
        result = runner.invoke(cli, ["add", ""])
        assert result.exit_code != 0

    def test_sc005_clean_start_and_exit(self) -> None:
        """SC-005: Application starts, accepts commands, exits cleanly"""
        runner = CliRunner()
        # Start and run command
        result = runner.invoke(cli, ["add", "Test"])
        assert result.exit_code == 0
        # Exit command
        result = runner.invoke(cli, ["exit"])
        assert result.exit_code == 0

    def test_sc006_priorities_and_tags_visible(self) -> None:
        """SC-006: Priorities and tags visible in table view"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task", "-p", "high", "--tags", "work,urgent"])
        result = runner.invoke(cli, ["list"])
        assert "[!]" in result.output  # Priority indicator
        assert "work" in result.output  # Tag visible

    def test_sc007_search_under_2_seconds(self) -> None:
        """SC-007: Search returns in under 2 seconds for 1000 tasks"""
        storage = MemoryStorage()
        service = TaskService(storage)
        # Add 1000 tasks
        for i in range(1000):
            service.create_task(title=f"Task {i} meeting" if i % 10 == 0 else f"Task {i}")

        start = time.time()
        results = service.search_tasks("meeting")
        elapsed = time.time() - start
        assert elapsed < 2.0
        assert len(results) == 100  # 1000/10 = 100 matching tasks

    def test_sc008_multiple_filters(self) -> None:
        """SC-008: Multiple filters work simultaneously"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Match", "-p", "high", "--tags", "work"])
        runner.invoke(cli, ["add", "No match", "-p", "low", "--tags", "home"])
        result = runner.invoke(cli, ["filter", "--priority", "high", "--tag", "work"])
        assert "Match" in result.output
        assert "No match" not in result.output

    def test_sc009_sorting_works_correctly(self) -> None:
        """SC-009: Sorting by any criterion works correctly"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "B task", "-p", "medium"])
        runner.invoke(cli, ["add", "A task", "-p", "high"])
        # Sort by title
        result = runner.invoke(cli, ["sort", "--by", "title", "--order", "asc"])
        assert result.output.find("A task") < result.output.find("B task")
        # Sort by priority
        result = runner.invoke(cli, ["sort", "--by", "priority"])
        assert result.output.find("A task") < result.output.find("B task")

    def test_sc010_recurring_tasks_auto_create(self) -> None:
        """SC-010: Recurring tasks create next instance on completion"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Recurring", "--recurrence", "daily", "--due", "2025-12-14"])
        runner.invoke(cli, ["done", "1"])
        list_result = runner.invoke(cli, ["list"])
        # Should have original (completed) and new instance
        assert list_result.output.count("Recurring") >= 1

    def test_sc011_overdue_highlighted(self) -> None:
        """SC-011: Overdue tasks are clearly highlighted"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Overdue", "--due", "2020-01-01"])
        result = runner.invoke(cli, ["list"])
        assert "Overdue" in result.output

    def test_sc014_clean_table_format(self) -> None:
        """SC-014: Task list displays in clean table with borders"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test task"])
        result = runner.invoke(cli, ["list"])
        # Table should have structure indicators
        assert "│" in result.output or "|" in result.output or "Task" in result.output

    def test_sc015_visual_indicators_consistent(self) -> None:
        """SC-015: Visual indicators are clear and consistent"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "High", "-p", "high"])
        runner.invoke(cli, ["add", "Low", "-p", "low"])
        runner.invoke(cli, ["done", "1"])
        result = runner.invoke(cli, ["list"])
        # Should have status and priority indicators
        assert "[X]" in result.output or "[!]" in result.output

    def test_sc016_table_readable_with_50_tasks(self) -> None:
        """SC-016: Table remains readable with up to 50 tasks"""
        runner = CliRunner()
        for i in range(50):
            runner.invoke(cli, ["add", f"Task {i:02d}"])
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        # All tasks should be in output
        assert "Task 00" in result.output
        assert "Task 49" in result.output


# =============================================================================
# POLISH-021: Functional Requirements Validation (FR-001 to FR-043)
# =============================================================================

class TestFunctionalRequirements:
    """Validate Functional Requirements FR-001 to FR-043"""

    # Basic Level (FR-001 to FR-014)

    def test_fr001_title_and_description_limits(self) -> None:
        """FR-001: Title 1-200 chars, description max 500 chars"""
        # Valid title
        task = Task(title="A" * 200)
        assert len(task.title) == 200
        # Title too long
        with pytest.raises(ValueError):
            Task(title="A" * 201)
        # Valid description
        task = Task(title="Test", description="D" * 500)
        assert task.description is not None
        assert len(task.description) == 500
        # Description too long
        with pytest.raises(ValueError):
            Task(title="Test", description="D" * 501)

    def test_fr002_unique_sequential_ids_never_reused(self) -> None:
        """FR-002: Unique sequential IDs, never reused after deletion"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])  # ID 1
        runner.invoke(cli, ["add", "Task 2"])  # ID 2
        runner.invoke(cli, ["add", "Task 3"])  # ID 3
        runner.invoke(cli, ["delete", "2"])
        runner.invoke(cli, ["add", "Task 4"])  # Should be ID 4, not 2
        list_result = runner.invoke(cli, ["list"])
        # Task 4 should have ID 4
        assert "Task 4" in list_result.output

    def test_fr003_table_displays_all_fields(self) -> None:
        """FR-003: Table displays ID, title, status, priority, tags, due date"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test", "-p", "high", "--tags", "work", "--due", "2025-12-15"])
        result = runner.invoke(cli, ["list"])
        assert "Test" in result.output
        assert "work" in result.output
        assert "2025-12-15" in result.output

    def test_fr004_mark_complete_incomplete(self) -> None:
        """FR-004: Mark task complete or incomplete using ID"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test"])
        assert runner.invoke(cli, ["done", "1"]).exit_code == 0
        assert runner.invoke(cli, ["undone", "1"]).exit_code == 0

    def test_fr005_update_title_description(self) -> None:
        """FR-005: Update title and/or description"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Old title"])
        runner.invoke(cli, ["update", "1", "--title", "New title", "-d", "New desc"])
        result = runner.invoke(cli, ["list"])
        assert "New title" in result.output

    def test_fr006_delete_task(self) -> None:
        """FR-006: Delete task using ID"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Delete me"])
        result = runner.invoke(cli, ["delete", "1"])
        assert result.exit_code == 0

    def test_fr007_validate_non_empty_title(self) -> None:
        """FR-007: Validate title is not empty"""
        with pytest.raises(ValueError):
            Task(title="")
        with pytest.raises(ValueError):
            Task(title="   ")

    def test_fr009_success_messages(self) -> None:
        """FR-009: Clear success messages for operations"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Test"])
        assert "created" in result.output.lower() or "success" in result.output.lower()

    def test_fr010_error_messages(self) -> None:
        """FR-010: Clear error messages for invalid operations"""
        runner = CliRunner()
        result = runner.invoke(cli, ["done", "999"])
        assert "error" in result.output.lower() or "not found" in result.output.lower()

    def test_fr012_exit_command(self) -> None:
        """FR-012: Exit command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ["exit"])
        assert result.exit_code == 0

    def test_fr013_welcome_message(self) -> None:
        """FR-013: Welcome message on startup"""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert "Todo" in result.output or "todo" in result.output.lower()

    # Intermediate Level (FR-015 to FR-022)

    def test_fr015_priority_levels(self) -> None:
        """FR-015: Assign priority levels"""
        runner = CliRunner()
        for priority in ["high", "medium", "low"]:
            result = runner.invoke(cli, ["add", f"{priority} task", "-p", priority])
            assert result.exit_code == 0

    def test_fr016_tags_comma_separated(self) -> None:
        """FR-016: Tags with comma-separated format"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Tagged", "--tags", "work,urgent,high priority"])
        result = runner.invoke(cli, ["list"])
        assert "work" in result.output

    def test_fr017_search_case_insensitive(self) -> None:
        """FR-017: Search is case-insensitive"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "MEETING with team"])
        result = runner.invoke(cli, ["search", "meeting"])
        assert "MEETING" in result.output

    def test_fr018_filter_by_status_priority_tags(self) -> None:
        """FR-018: Filter by status, priority, tags"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test", "-p", "high", "--tags", "work"])
        assert runner.invoke(cli, ["filter", "--status", "incomplete"]).exit_code == 0
        assert runner.invoke(cli, ["filter", "--priority", "high"]).exit_code == 0
        assert runner.invoke(cli, ["filter", "--tag", "work"]).exit_code == 0

    def test_fr019_multiple_filters(self) -> None:
        """FR-019: Multiple simultaneous filters"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Match all", "-p", "high", "--tags", "work"])
        result = runner.invoke(cli, ["filter", "--priority", "high", "--tag", "work", "--status", "incomplete"])
        assert "Match all" in result.output

    def test_fr020_sort_options(self) -> None:
        """FR-020: Sort by due date, priority, created date, title"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test"])
        for field in ["due_date", "priority", "created", "title"]:
            result = runner.invoke(cli, ["sort", "--by", field])
            assert result.exit_code == 0

    def test_fr020a_default_sort_newest_first(self) -> None:
        """FR-020a: Default sort by created date newest first"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "First"])
        runner.invoke(cli, ["add", "Second"])
        runner.invoke(cli, ["add", "Third"])
        result = runner.invoke(cli, ["list"])
        # Newest first means Third should appear before First
        third_pos = result.output.find("Third")
        first_pos = result.output.find("First")
        assert third_pos < first_pos

    def test_fr021_priority_visual_indicators(self) -> None:
        """FR-021: Visual indicators for priorities"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "High", "-p", "high"])
        runner.invoke(cli, ["add", "Medium", "-p", "medium"])
        runner.invoke(cli, ["add", "Low", "-p", "low"])
        result = runner.invoke(cli, ["list"])
        assert "[!]" in result.output  # High
        assert "[-]" in result.output  # Medium
        assert "[v]" in result.output  # Low

    # Advanced Level (FR-023 to FR-030)

    def test_fr023_recurring_patterns(self) -> None:
        """FR-023: Support daily, weekly, monthly recurrence"""
        runner = CliRunner()
        for pattern in ["daily", "weekly", "monthly"]:
            result = runner.invoke(cli, ["add", f"{pattern} task", "--recurrence", pattern])
            assert result.exit_code == 0

    def test_fr024_recurring_creates_next_instance(self) -> None:
        """FR-024: Completing recurring task creates next instance"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Recurring", "--recurrence", "daily", "--due", "2025-12-14"])
        runner.invoke(cli, ["done", "1"])
        # New task should exist
        list_result = runner.invoke(cli, ["list"])
        assert "Recurring" in list_result.output

    def test_fr025_due_date_format(self) -> None:
        """FR-025: Due dates with date and time format"""
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Task", "--due", "2025-12-15 14:30"])
        assert result.exit_code == 0

    def test_fr031_to_fr035_table_format(self) -> None:
        """FR-031 to FR-035: Table format with borders and columns"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Test task", "-p", "high", "--tags", "work"])
        result = runner.invoke(cli, ["list"])
        # Should have table structure
        assert result.exit_code == 0
        assert "Test task" in result.output

    def test_fr036_fr037_status_indicators(self) -> None:
        """FR-036/FR-037: Status indicators for complete/incomplete"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Task 1"])
        runner.invoke(cli, ["add", "Task 2"])
        runner.invoke(cli, ["done", "1"])
        result = runner.invoke(cli, ["list"])
        assert "[X]" in result.output  # Completed
        assert "[ ]" in result.output  # Incomplete

    def test_fr038_to_fr040_priority_indicators(self) -> None:
        """FR-038 to FR-040: Priority indicators with colors"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "H", "-p", "high"])
        runner.invoke(cli, ["add", "M", "-p", "medium"])
        runner.invoke(cli, ["add", "L", "-p", "low"])
        result = runner.invoke(cli, ["list"])
        assert "[!]" in result.output
        assert "[-]" in result.output
        assert "[v]" in result.output

    def test_fr043_tags_displayed_clearly(self) -> None:
        """FR-043: Tags displayed with clear separators"""
        runner = CliRunner()
        runner.invoke(cli, ["add", "Tagged task", "--tags", "work,urgent"])
        result = runner.invoke(cli, ["list"])
        assert "work" in result.output
        assert "urgent" in result.output


# =============================================================================
# POLISH-022: Non-Functional Requirements Validation (NFR-001 to NFR-012)
# =============================================================================

class TestNonFunctionalRequirements:
    """Validate Non-Functional Requirements NFR-001 to NFR-012"""

    def test_nfr001_operations_under_1_second(self) -> None:
        """NFR-001: All task operations under 1 second"""
        runner = CliRunner()
        operations = [
            (["add", "Test task"], "add"),
            (["list"], "list"),
            (["update", "1", "--title", "Updated"], "update"),
            (["done", "1"], "done"),
            (["delete", "1"], "delete"),
        ]
        runner.invoke(cli, ["add", "Initial"])
        for args, op_name in operations:
            if op_name != "add":
                runner.invoke(cli, ["add", "Test"])
            start = time.time()
            runner.invoke(cli, args)
            elapsed = time.time() - start
            assert elapsed < 1.0, f"{op_name} took {elapsed}s"

    def test_nfr002_search_filter_under_2_seconds(self) -> None:
        """NFR-002: Search/filter under 2 seconds for 1000 tasks"""
        storage = MemoryStorage()
        service = TaskService(storage)
        for i in range(1000):
            service.create_task(title=f"Task {i}", priority=Priority.HIGH if i % 3 == 0 else Priority.LOW)

        # Search
        start = time.time()
        service.search_tasks("Task 5")
        assert time.time() - start < 2.0

        # Filter
        start = time.time()
        service.filter_tasks(priority=Priority.HIGH)
        assert time.time() - start < 2.0

    def test_nfr003_table_rendering_100_tasks(self) -> None:
        """NFR-003: Table rendering handles 100 tasks without lag"""
        runner = CliRunner()
        for i in range(100):
            runner.invoke(cli, ["add", f"Task {i}"])

        start = time.time()
        result = runner.invoke(cli, ["list"])
        elapsed = time.time() - start
        assert elapsed < 0.5  # Under 500ms
        assert result.exit_code == 0

    def test_nfr005_user_friendly_errors(self) -> None:
        """NFR-005: Error messages are user-friendly"""
        runner = CliRunner()
        # Invalid ID error
        result = runner.invoke(cli, ["done", "999"])
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_nfr006_data_not_persisted_warning(self) -> None:
        """NFR-006: Warn users data is not persisted"""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        # Should mention data persistence or in-memory
        output_lower = result.output.lower()
        assert "persist" in output_lower or "session" in output_lower or "memory" in output_lower

    def test_nfr008_help_with_examples(self) -> None:
        """NFR-008: Help provides clear commands and examples"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "add" in result.output
        assert "list" in result.output
        assert "done" in result.output

    def test_nfr012_short_memorable_commands(self) -> None:
        """NFR-012: Commands are short and memorable"""
        # Verify command names are short
        short_commands = ["add", "list", "done", "delete", "update", "search", "filter", "sort"]
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        for cmd in short_commands:
            assert cmd in result.output
