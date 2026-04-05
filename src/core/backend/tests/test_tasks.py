"""
Task CRUD API Tests

TDD Red-Green-Refactor Tests for Task CRUD operations.

These tests validate:
1. Task creation with user isolation
2. Task listing (filtered by user)
3. Task retrieval (single task, with ownership check)
4. Task updates (with ownership check)
5. Task deletion (soft delete with ownership check)
6. User isolation (users cannot access each other's tasks)
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from dependencies import get_current_user, get_db
from main import app
from models import Task


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency overrides."""

    def get_session_override():
        return session

    def get_current_user_override():
        """Mock user ID for testing."""
        return "test-user-123"

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="client_user_2")
def client_user_2_fixture(session: Session):
    """Create a test client for a second user."""

    def get_session_override():
        return session

    def get_current_user_override():
        """Mock different user ID for testing user isolation."""
        return "test-user-456"

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


# Helper functions
def create_test_task(session: Session, user_id: str, title: str = "Test Task") -> Task:
    """Helper function to create a task directly in the database."""
    task = Task(user_id=user_id, title=title, description="Test description")
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ===========================
# CREATE TESTS
# ===========================


def test_create_task_success(client: TestClient):
    """Test creating a new task with valid data."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["completed"] is False
    assert data["user_id"] == "test-user-123"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_missing_title(client: TestClient):
    """Test creating a task without a title returns 422."""
    response = client.post("/api/v1/tasks", json={"description": "No title"})

    assert response.status_code == 422


def test_create_task_empty_title(client: TestClient):
    """Test creating a task with empty title returns 422."""
    response = client.post(
        "/api/v1/tasks", json={"title": "", "description": "Empty title"}
    )

    assert response.status_code == 422


def test_create_task_title_too_long(client: TestClient):
    """Test creating a task with title > 200 characters returns 422."""
    long_title = "A" * 201
    response = client.post(
        "/api/v1/tasks", json={"title": long_title, "description": "Too long"}
    )

    assert response.status_code == 422


def test_create_task_user_isolation(client: TestClient, session: Session):
    """Test that tasks are automatically assigned to the authenticated user."""
    response = client.post(
        "/api/v1/tasks", json={"title": "User isolation test"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "test-user-123"  # From mock JWT


# ===========================
# READ LIST TESTS
# ===========================


def test_list_tasks_empty(client: TestClient):
    """Test listing tasks when user has no tasks."""
    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_list_tasks_with_tasks(client: TestClient, session: Session):
    """Test listing tasks returns only user's active tasks."""
    # Create tasks for test user
    create_test_task(session, "test-user-123", "Task 1")
    create_test_task(session, "test-user-123", "Task 2")

    # Create task for different user (should not appear)
    create_test_task(session, "other-user", "Other task")

    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["user_id"] == "test-user-123" for task in data)


def test_list_tasks_excludes_deleted(client: TestClient, session: Session):
    """Test that soft-deleted tasks are not included in list."""
    # Create active task
    create_test_task(session, "test-user-123", "Active task")

    # Create deleted task
    deleted_task = Task(
        user_id="test-user-123",
        title="Deleted task",
        deleted_at=datetime(2024, 1, 1, 0, 0, 0),
    )
    session.add(deleted_task)
    session.commit()

    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Active task"


def test_list_tasks_user_isolation(
    client: TestClient, session: Session
):
    """Test that users only see their own tasks."""
    # Create tasks for authenticated user (test-user-123)
    create_test_task(session, "test-user-123", "User 1 Task")

    # Create tasks for different user directly in database
    create_test_task(session, "other-user-456", "Other User Task")

    # Authenticated user should only see their own task
    response = client.get("/api/v1/tasks")
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "User 1 Task"
    assert data[0]["user_id"] == "test-user-123"


# ===========================
# READ SINGLE TESTS
# ===========================


def test_get_task_success(client: TestClient, session: Session):
    """Test getting a single task by ID."""
    task = create_test_task(session, "test-user-123", "My task")

    response = client.get(f"/api/v1/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == "My task"
    assert data["user_id"] == "test-user-123"


def test_get_task_not_found(client: TestClient):
    """Test getting a non-existent task returns 404."""
    response = client.get("/api/v1/tasks/99999")

    assert response.status_code == 404


def test_get_task_different_user(client: TestClient, session: Session):
    """Test that users cannot access other users' tasks."""
    # Create task owned by different user
    other_task = create_test_task(session, "other-user", "Other's task")

    response = client.get(f"/api/v1/tasks/{other_task.id}")

    assert response.status_code == 404  # Should not reveal existence


def test_get_task_deleted(client: TestClient, session: Session):
    """Test that deleted tasks cannot be retrieved."""
    task = Task(
        user_id="test-user-123",
        title="Deleted",
        deleted_at=datetime(2024, 1, 1, 0, 0, 0)
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.get(f"/api/v1/tasks/{task.id}")

    assert response.status_code == 404


# ===========================
# UPDATE TESTS
# ===========================


def test_update_task_success(client: TestClient, session: Session):
    """Test updating a task's title and description."""
    task = create_test_task(session, "test-user-123", "Original title")

    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated title", "description": "Updated description"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "Updated description"
    # Updated_at should be refreshed (will be tested with actual timestamps)


def test_update_task_partial(client: TestClient, session: Session):
    """Test updating only some fields (partial update)."""
    task = create_test_task(session, "test-user-123", "Original")

    # Update only title
    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={"title": "New title"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["description"] == "Test description"  # Unchanged


def test_update_task_not_found(client: TestClient):
    """Test updating a non-existent task returns 404."""
    response = client.put(
        "/api/v1/tasks/99999",
        json={"title": "Updated"},
    )

    assert response.status_code == 404


def test_update_task_different_user(client: TestClient, session: Session):
    """Test that users cannot update other users' tasks."""
    other_task = create_test_task(session, "other-user", "Other's task")

    response = client.put(
        f"/api/v1/tasks/{other_task.id}",
        json={"title": "Hacked"},
    )

    assert response.status_code == 404


def test_update_task_empty_title(client: TestClient, session: Session):
    """Test updating a task with empty title returns 422."""
    task = create_test_task(session, "test-user-123", "Original")

    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={"title": ""},
    )

    assert response.status_code == 422


# ===========================
# DELETE TESTS
# ===========================


def test_delete_task_success(client: TestClient, session: Session):
    """Test soft deleting a task."""
    task = create_test_task(session, "test-user-123", "To be deleted")

    response = client.delete(f"/api/v1/tasks/{task.id}")

    assert response.status_code == 204

    # Task should no longer appear in list
    list_response = client.get("/api/v1/tasks")
    assert len(list_response.json()) == 0

    # Task should not be retrievable
    get_response = client.get(f"/api/v1/tasks/{task.id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient):
    """Test deleting a non-existent task returns 404."""
    response = client.delete("/api/v1/tasks/99999")

    assert response.status_code == 404


def test_delete_task_different_user(client: TestClient, session: Session):
    """Test that users cannot delete other users' tasks."""
    other_task = create_test_task(session, "other-user", "Other's task")

    response = client.delete(f"/api/v1/tasks/{other_task.id}")

    assert response.status_code == 404


def test_delete_task_already_deleted(client: TestClient, session: Session):
    """Test deleting an already deleted task returns 404."""
    task = Task(
        user_id="test-user-123",
        title="Already deleted",
        deleted_at=datetime(2024, 1, 1, 0, 0, 0)
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.delete(f"/api/v1/tasks/{task.id}")

    assert response.status_code == 404
