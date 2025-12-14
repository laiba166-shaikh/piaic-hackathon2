"""
Contract tests for ITaskStorage interface.

These tests verify that any storage implementation (MemoryStorage, DatabaseStorage, etc.)
complies with the ITaskStorage interface contract.
"""
from datetime import datetime, timedelta
import pytest
from src.core.models import Task, Priority, Recurrence
from src.core.exceptions import TaskNotFoundError
from src.core.storage.base import ITaskStorage
from src.core.storage.memory import MemoryStorage


@pytest.fixture
def storage() -> ITaskStorage:
    """Create a fresh storage instance for each test"""
    return MemoryStorage()


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing"""
    return Task(
        title="Test task",
        description="Test description",
        priority=Priority.HIGH,
        tags=["test", "sample"],
    )


class TestStorageInterfaceContract:
    """Contract tests that all ITaskStorage implementations must pass"""

    def test_create_assigns_unique_sequential_id(self, storage: ITaskStorage) -> None:
        """Test that create() assigns unique sequential IDs that are never reused"""
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        task3 = Task(title="Task 3")

        created1 = storage.create(task1)
        created2 = storage.create(task2)
        created3 = storage.create(task3)

        # IDs should be sequential
        assert created1.id == 1
        assert created2.id == 2
        assert created3.id == 3

        # IDs should be unique
        assert created1.id != created2.id
        assert created2.id != created3.id
        assert created1.id != created3.id

    def test_create_sets_timestamps(self, storage: ITaskStorage, sample_task: Task) -> None:
        """Test that create() sets created_at and updated_at timestamps"""
        before = datetime.now()
        created = storage.create(sample_task)
        after = datetime.now()

        assert created.created_at is not None
        assert created.updated_at is not None
        assert before <= created.created_at <= after
        assert before <= created.updated_at <= after

    def test_get_returns_task_when_exists(self, storage: ITaskStorage, sample_task: Task) -> None:
        """Test that get() returns the task when it exists"""
        created = storage.create(sample_task)
        retrieved = storage.get(created.id)  # type: ignore

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == created.title
        assert retrieved.description == created.description

    def test_get_returns_none_when_not_found(self, storage: ITaskStorage) -> None:
        """Test that get() returns None when task doesn't exist"""
        result = storage.get(999)
        assert result is None

    def test_list_all_returns_empty_list_when_no_tasks(self, storage: ITaskStorage) -> None:
        """Test that list_all() returns empty list when no tasks exist"""
        tasks = storage.list_all()
        assert tasks == []

    def test_list_all_returns_all_tasks(self, storage: ITaskStorage) -> None:
        """Test that list_all() returns all tasks"""
        task1 = storage.create(Task(title="Task 1"))
        task2 = storage.create(Task(title="Task 2"))
        task3 = storage.create(Task(title="Task 3"))

        all_tasks = storage.list_all()

        assert len(all_tasks) == 3
        assert task1 in all_tasks
        assert task2 in all_tasks
        assert task3 in all_tasks

    def test_list_all_returns_newest_first(self, storage: ITaskStorage) -> None:
        """Test that list_all() returns tasks sorted by created_at descending (newest first)"""
        import time

        # Create tasks with slight delays to ensure different timestamps
        task1 = storage.create(Task(title="First task"))
        time.sleep(0.001)  # 1ms delay
        task2 = storage.create(Task(title="Second task"))
        time.sleep(0.001)  # 1ms delay
        task3 = storage.create(Task(title="Third task"))

        all_tasks = storage.list_all()

        # Newest (task3) should be first, oldest (task1) should be last
        assert all_tasks[0].id == task3.id
        assert all_tasks[1].id == task2.id
        assert all_tasks[2].id == task1.id

    def test_update_modifies_task(self, storage: ITaskStorage, sample_task: Task) -> None:
        """Test that update() modifies an existing task"""
        created = storage.create(sample_task)

        # Modify the task
        created.title = "Updated title"
        created.description = "Updated description"
        created.completed = True

        updated = storage.update(created)

        assert updated.title == "Updated title"
        assert updated.description == "Updated description"
        assert updated.completed is True

    def test_update_sets_updated_at_timestamp(self, storage: ITaskStorage, sample_task: Task) -> None:
        """Test that update() updates the updated_at timestamp"""
        created = storage.create(sample_task)
        original_updated_at = created.updated_at

        # Small delay to ensure different timestamp
        created.title = "Modified"
        updated = storage.update(created)

        assert updated.updated_at >= original_updated_at

    def test_update_raises_error_when_task_not_found(self, storage: ITaskStorage) -> None:
        """Test that update() raises TaskNotFoundError when task doesn't exist"""
        task = Task(title="Non-existent task")
        task.id = 999

        with pytest.raises(TaskNotFoundError) as exc_info:
            storage.update(task)

        assert exc_info.value.task_id == 999

    def test_update_raises_error_when_id_is_none(self, storage: ITaskStorage) -> None:
        """Test that update() raises ValueError when task.id is None"""
        task = Task(title="Task without ID")

        with pytest.raises(ValueError, match="Task ID cannot be None"):
            storage.update(task)

    def test_delete_removes_task(self, storage: ITaskStorage, sample_task: Task) -> None:
        """Test that delete() removes a task"""
        created = storage.create(sample_task)

        result = storage.delete(created.id)  # type: ignore

        assert result is True
        assert storage.get(created.id) is None  # type: ignore

    def test_delete_returns_false_when_not_found(self, storage: ITaskStorage) -> None:
        """Test that delete() returns False when task doesn't exist"""
        result = storage.delete(999)
        assert result is False

    def test_delete_does_not_reuse_id(self, storage: ITaskStorage) -> None:
        """Test that IDs are never reused after deletion (critical requirement)"""
        # Create task with ID 1
        task1 = storage.create(Task(title="Task 1"))
        assert task1.id == 1

        # Create task with ID 2
        task2 = storage.create(Task(title="Task 2"))
        assert task2.id == 2

        # Create task with ID 3
        task3 = storage.create(Task(title="Task 3"))
        assert task3.id == 3

        # Delete task 2
        storage.delete(task2.id)  # type: ignore

        # Create a new task - it should get ID 4, NOT ID 2
        task4 = storage.create(Task(title="Task 4"))
        assert task4.id == 4, "ID should not be reused after deletion"

        # Verify task 2 is still deleted
        assert storage.get(2) is None

    def test_create_multiple_tasks_maintains_counter(self, storage: ITaskStorage) -> None:
        """Test that ID counter increments correctly across multiple operations"""
        tasks = []
        for i in range(1, 6):
            task = storage.create(Task(title=f"Task {i}"))
            tasks.append(task)
            assert task.id == i

        # Delete some tasks
        storage.delete(tasks[1].id)  # Delete ID 2  # type: ignore
        storage.delete(tasks[3].id)  # Delete ID 4  # type: ignore

        # Create new tasks - they should get IDs 6 and 7, not 2 and 4
        new_task1 = storage.create(Task(title="Task 6"))
        new_task2 = storage.create(Task(title="Task 7"))

        assert new_task1.id == 6
        assert new_task2.id == 7
