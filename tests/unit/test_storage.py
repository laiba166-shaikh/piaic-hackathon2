"""Unit tests for MemoryStorage implementation"""
from datetime import datetime
import pytest
from src.core.models import Task, Priority
from src.core.exceptions import TaskNotFoundError
from src.core.storage.memory import MemoryStorage


class TestMemoryStorage:
    """Unit tests for MemoryStorage implementation"""

    def test_initialization(self) -> None:
        """Test MemoryStorage initializes with empty storage"""
        storage = MemoryStorage()

        assert storage.list_all() == []

    def test_counter_starts_at_zero(self) -> None:
        """Test that internal counter starts at 0"""
        storage = MemoryStorage()
        task = storage.create(Task(title="First task"))

        # First task should get ID 1
        assert task.id == 1

    def test_create_increments_counter(self) -> None:
        """Test that counter increments with each create"""
        storage = MemoryStorage()

        task1 = storage.create(Task(title="Task 1"))
        task2 = storage.create(Task(title="Task 2"))
        task3 = storage.create(Task(title="Task 3"))

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_create_stores_task(self) -> None:
        """Test that create() stores the task in internal dict"""
        storage = MemoryStorage()
        task = Task(title="Test task", description="Test description")

        created = storage.create(task)

        # Task should be retrievable
        retrieved = storage.get(created.id)  # type: ignore
        assert retrieved is not None
        assert retrieved.title == "Test task"
        assert retrieved.description == "Test description"

    def test_create_sets_created_at(self) -> None:
        """Test that create() sets created_at timestamp"""
        storage = MemoryStorage()
        task = Task(title="Test task")

        created = storage.create(task)

        assert created.created_at is not None
        assert isinstance(created.created_at, datetime)

    def test_create_sets_updated_at(self) -> None:
        """Test that create() sets updated_at timestamp"""
        storage = MemoryStorage()
        task = Task(title="Test task")

        created = storage.create(task)

        assert created.updated_at is not None
        assert isinstance(created.updated_at, datetime)

    def test_get_retrieves_task_by_id(self) -> None:
        """Test that get() retrieves task by ID"""
        storage = MemoryStorage()
        task = storage.create(Task(title="Test task"))

        retrieved = storage.get(task.id)  # type: ignore

        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.title == task.title

    def test_get_returns_none_for_nonexistent_id(self) -> None:
        """Test that get() returns None for non-existent ID"""
        storage = MemoryStorage()

        result = storage.get(999)

        assert result is None

    def test_list_all_empty_storage(self) -> None:
        """Test list_all() with empty storage"""
        storage = MemoryStorage()

        tasks = storage.list_all()

        assert tasks == []

    def test_list_all_returns_all_tasks(self) -> None:
        """Test list_all() returns all tasks"""
        storage = MemoryStorage()

        task1 = storage.create(Task(title="Task 1"))
        task2 = storage.create(Task(title="Task 2"))
        task3 = storage.create(Task(title="Task 3"))

        all_tasks = storage.list_all()

        assert len(all_tasks) == 3
        task_ids = [t.id for t in all_tasks]
        assert task1.id in task_ids
        assert task2.id in task_ids
        assert task3.id in task_ids

    def test_list_all_sorted_by_created_at_descending(self) -> None:
        """Test list_all() returns tasks sorted by created_at descending"""
        import time

        storage = MemoryStorage()

        # Create tasks with slight delays to ensure different timestamps
        task1 = storage.create(Task(title="First"))
        time.sleep(0.001)  # 1ms delay
        task2 = storage.create(Task(title="Second"))
        time.sleep(0.001)  # 1ms delay
        task3 = storage.create(Task(title="Third"))

        all_tasks = storage.list_all()

        # Newest first (task3, task2, task1)
        assert all_tasks[0].id == task3.id
        assert all_tasks[1].id == task2.id
        assert all_tasks[2].id == task1.id

    def test_update_modifies_task(self) -> None:
        """Test update() modifies a task"""
        storage = MemoryStorage()
        task = storage.create(Task(title="Original title"))

        task.title = "Updated title"
        task.description = "New description"
        task.completed = True

        updated = storage.update(task)

        assert updated.title == "Updated title"
        assert updated.description == "New description"
        assert updated.completed is True

    def test_update_sets_updated_at(self) -> None:
        """Test update() updates the updated_at timestamp"""
        storage = MemoryStorage()
        task = storage.create(Task(title="Test task"))

        original_updated_at = task.updated_at
        task.title = "Modified"

        updated = storage.update(task)

        assert updated.updated_at >= original_updated_at

    def test_update_raises_error_for_none_id(self) -> None:
        """Test update() raises ValueError when task.id is None"""
        storage = MemoryStorage()
        task = Task(title="Task without ID")

        with pytest.raises(ValueError, match="Task ID cannot be None"):
            storage.update(task)

    def test_update_raises_error_for_nonexistent_task(self) -> None:
        """Test update() raises TaskNotFoundError for non-existent task"""
        storage = MemoryStorage()
        task = Task(title="Non-existent")
        task.id = 999

        with pytest.raises(TaskNotFoundError) as exc_info:
            storage.update(task)

        assert exc_info.value.task_id == 999

    def test_delete_removes_task(self) -> None:
        """Test delete() removes a task"""
        storage = MemoryStorage()
        task = storage.create(Task(title="To be deleted"))

        result = storage.delete(task.id)  # type: ignore

        assert result is True
        assert storage.get(task.id) is None  # type: ignore

    def test_delete_returns_false_for_nonexistent_id(self) -> None:
        """Test delete() returns False for non-existent ID"""
        storage = MemoryStorage()

        result = storage.delete(999)

        assert result is False

    def test_delete_does_not_affect_other_tasks(self) -> None:
        """Test delete() only removes the specified task"""
        storage = MemoryStorage()

        task1 = storage.create(Task(title="Task 1"))
        task2 = storage.create(Task(title="Task 2"))
        task3 = storage.create(Task(title="Task 3"))

        storage.delete(task2.id)  # type: ignore

        assert storage.get(task1.id) is not None  # type: ignore
        assert storage.get(task2.id) is None  # type: ignore
        assert storage.get(task3.id) is not None  # type: ignore

    def test_counter_never_reuses_ids(self) -> None:
        """Test that counter never reuses IDs even after deletion"""
        storage = MemoryStorage()

        # Create and delete task with ID 1
        task1 = storage.create(Task(title="Task 1"))
        storage.delete(task1.id)  # type: ignore

        # Create new task - should get ID 2, not ID 1
        task2 = storage.create(Task(title="Task 2"))
        assert task2.id == 2

        # Create another - should get ID 3
        task3 = storage.create(Task(title="Task 3"))
        assert task3.id == 3

    def test_multiple_deletes_and_creates(self) -> None:
        """Test complex scenario with multiple deletes and creates"""
        storage = MemoryStorage()

        # Create tasks 1, 2, 3
        t1 = storage.create(Task(title="Task 1"))
        t2 = storage.create(Task(title="Task 2"))
        t3 = storage.create(Task(title="Task 3"))

        # Delete task 2
        storage.delete(t2.id)  # type: ignore

        # Create task 4 (should get ID 4, not 2)
        t4 = storage.create(Task(title="Task 4"))
        assert t4.id == 4

        # Delete tasks 1 and 3
        storage.delete(t1.id)  # type: ignore
        storage.delete(t3.id)  # type: ignore

        # Create task 5 (should get ID 5, not 1, 2, or 3)
        t5 = storage.create(Task(title="Task 5"))
        assert t5.id == 5

        # Only tasks 4 and 5 should exist
        all_tasks = storage.list_all()
        assert len(all_tasks) == 2
        task_ids = [t.id for t in all_tasks]
        assert 4 in task_ids
        assert 5 in task_ids
