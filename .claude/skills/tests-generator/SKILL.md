---
name: tests-generator
description: Generate comprehensive test suites for full-stack applications covering all scenarios including happy paths, validation, authentication, edge cases, and integration flows. Use when (1) implementing new features that need tests, (2) user asks to "generate tests" or "add test coverage", (3) following TDD workflow in RED phase, or (4) filling test coverage gaps identified by audits.
license: Complete terms in LICENSE.txt
---

# Tests Generator

Generate comprehensive, production-ready test suites for backend, frontend, and integration scenarios following TDD best practices.

## Workflow

Follow these steps when generating tests:

1. **Analyze feature requirements**
   - Read acceptance criteria from spec
   - Identify user stories
   - List expected behaviors
   - Note validation rules and constraints

2. **Determine test scenarios**
   - Happy path (success cases)
   - Validation errors (400/422)
   - Authentication/authorization (401/403)
   - Not found errors (404)
   - Edge cases (boundaries, special chars, empty values)
   - User isolation (can't access other users' data)

3. **Generate backend tests (Pytest + FastAPI)**
   - Unit tests for route handlers
   - Integration tests for API endpoints
   - Database operation tests
   - Authentication flow tests

4. **Generate frontend tests (Vitest + React Testing Library)**
   - Component rendering tests
   - User interaction tests
   - API integration tests
   - Error handling tests

5. **Generate integration/E2E tests**
   - Full user flows
   - Cross-layer validation
   - Real-world scenarios

## Output Format

Present generated tests using this structure:

```
🧪 Generated Tests: [feature-name]

Source: specs/phase2/features/[feature].md

Test Files to Create:

Backend Tests:
- src/core/backend/tests/unit/test_[feature].py (15 tests)
- src/core/backend/tests/integration/test_[feature]_api.py (8 tests)

Frontend Tests:
- src/core/frontend/tests/unit/[Component].test.tsx (12 tests)
- src/core/frontend/tests/integration/[feature]-flow.test.ts (6 tests)

Coverage:
✅ Happy Paths: 8 scenarios
✅ Validation Errors: 6 scenarios
✅ Auth/Authorization: 4 scenarios
✅ Edge Cases: 10 scenarios
✅ User Isolation: 4 scenarios

Total: 41 tests generated
```

## Test Scenario Categories

### 1. Happy Path Tests (Success Cases)

**Scenarios to generate:**
- Create resource with valid data → 201 Created
- Read single resource → 200 OK
- Read list of resources → 200 OK
- Update resource with valid data → 200 OK
- Delete resource → 204 No Content

**Backend Example (Pytest):**
```python
# src/core/backend/tests/unit/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Generate valid JWT token for testing"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_task_success(client, auth_headers):
    """Happy Path: Create task with valid data"""
    # Arrange
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": 3,
        "tags": ["urgent", "work"]
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["priority"] == 3
    assert data["tags"] == ["urgent", "work"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_task_success(client, auth_headers, create_task):
    """Happy Path: Get single task"""
    # Arrange
    task = create_task(title="Test Task")

    # Act
    response = client.get(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == "Test Task"

def test_get_all_tasks_success(client, auth_headers, create_task):
    """Happy Path: Get list of tasks"""
    # Arrange
    create_task(title="Task 1")
    create_task(title="Task 2")
    create_task(title="Task 3")

    # Act
    response = client.get("/api/v1/tasks", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("id" in task for task in data)

def test_update_task_success(client, auth_headers, create_task):
    """Happy Path: Update task"""
    # Arrange
    task = create_task(title="Original Title")
    update_data = {"title": "Updated Title"}

    # Act
    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json=update_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

def test_delete_task_success(client, auth_headers, create_task):
    """Happy Path: Delete task (soft delete)"""
    # Arrange
    task = create_task(title="Task to Delete")

    # Act
    response = client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 204

    # Verify soft delete
    get_response = client.get(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404
```

**Frontend Example (Vitest + RTL):**
```typescript
// src/core/frontend/tests/unit/TaskList.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskList } from '@/components/tasks/TaskList';
import { api } from '@/lib/api';

vi.mock('@/lib/api');

describe('TaskList - Happy Path', () => {
  const mockTasks = [
    { id: 1, title: 'Task 1', description: 'Desc 1', priority: 1, tags: [] },
    { id: 2, title: 'Task 2', description: 'Desc 2', priority: 2, tags: [] },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render list of tasks successfully', async () => {
    // Arrange
    vi.spyOn(api, 'getTasks').mockResolvedValue(mockTasks);

    // Act
    render(<TaskList />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });
  });

  it('should delete task when delete button clicked', async () => {
    // Arrange
    vi.spyOn(api, 'getTasks').mockResolvedValue(mockTasks);
    vi.spyOn(api, 'deleteTask').mockResolvedValue(undefined);

    render(<TaskList />);

    // Act
    const deleteButtons = await screen.findAllByRole('button', { name: /delete/i });
    await userEvent.click(deleteButtons[0]);

    // Assert
    await waitFor(() => {
      expect(api.deleteTask).toHaveBeenCalledWith(1);
    });
  });
});
```

### 2. Validation Error Tests (400/422)

**Scenarios to generate:**
- Missing required fields
- Invalid data types
- Out-of-range values
- String length violations (too short, too long)
- Format validation (email, URL, date)
- Invalid enum values

**Backend Example:**
```python
def test_create_task_missing_title_returns_400(client, auth_headers):
    """Validation: Title is required"""
    # Arrange
    invalid_data = {"description": "No title provided"}

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=invalid_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 400
    error = response.json()
    assert "title" in error["detail"].lower()

def test_create_task_title_too_long_returns_400(client, auth_headers):
    """Validation: Title max length 200 chars"""
    # Arrange
    invalid_data = {"title": "a" * 201}

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=invalid_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 400
    error = response.json()
    assert "title" in error["detail"].lower()
    assert "200" in error["detail"]

def test_create_task_invalid_priority_returns_400(client, auth_headers):
    """Validation: Priority must be 1-5"""
    # Arrange
    invalid_data = {
        "title": "Task",
        "priority": 10  # Out of range
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=invalid_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 400
    error = response.json()
    assert "priority" in error["detail"].lower()

def test_create_task_invalid_type_returns_400(client, auth_headers):
    """Validation: Fields must be correct type"""
    # Arrange
    invalid_data = {
        "title": "Task",
        "priority": "high"  # Should be number
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=invalid_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 422  # Pydantic validation error
```

**Frontend Example:**
```typescript
describe('TaskForm - Validation', () => {
  it('should show error when title is missing', async () => {
    // Arrange
    render(<TaskForm />);

    // Act
    await userEvent.click(screen.getByRole('button', { name: /create/i }));

    // Assert
    expect(screen.getByText(/title is required/i)).toBeInTheDocument();
  });

  it('should show error when title is too long', async () => {
    // Arrange
    render(<TaskForm />);
    const longTitle = 'a'.repeat(201);

    // Act
    await userEvent.type(screen.getByLabelText(/title/i), longTitle);
    await userEvent.click(screen.getByRole('button', { name: /create/i }));

    // Assert
    expect(screen.getByText(/title must be at most 200 characters/i)).toBeInTheDocument();
  });

  it('should show error when priority is out of range', async () => {
    // Arrange
    render(<TaskForm />);

    // Act
    await userEvent.type(screen.getByLabelText(/title/i), 'Task');
    await userEvent.type(screen.getByLabelText(/priority/i), '10');
    await userEvent.click(screen.getByRole('button', { name: /create/i }));

    // Assert
    expect(screen.getByText(/priority must be between 1 and 5/i)).toBeInTheDocument();
  });
});
```

### 3. Authentication/Authorization Tests (401/403)

**Scenarios to generate:**
- Missing authentication token → 401
- Invalid/expired token → 401
- Accessing other user's resource → 404 (user isolation)
- User can only see their own data

**Backend Example:**
```python
def test_create_task_without_auth_returns_401(client):
    """Auth: Authentication required"""
    # Arrange
    task_data = {"title": "Task"}

    # Act
    response = client.post("/api/v1/tasks", json=task_data)
    # No auth headers

    # Assert
    assert response.status_code == 401

def test_create_task_with_invalid_token_returns_401(client):
    """Auth: Invalid token rejected"""
    # Arrange
    task_data = {"title": "Task"}
    invalid_headers = {"Authorization": "Bearer invalid-token"}

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=invalid_headers
    )

    # Assert
    assert response.status_code == 401

def test_get_task_filters_by_user_id(client, auth_headers, create_task_for_other_user):
    """Auth: User isolation - cannot access other user's task"""
    # Arrange
    other_task = create_task_for_other_user(title="Other User's Task")

    # Act
    response = client.get(
        f"/api/v1/tasks/{other_task.id}",
        headers=auth_headers  # Different user's token
    )

    # Assert
    assert response.status_code == 404  # Not found for this user

def test_get_all_tasks_filters_by_user_id(client, auth_headers, create_task, create_task_for_other_user):
    """Auth: User isolation - only see own tasks"""
    # Arrange
    create_task(title="My Task 1")
    create_task(title="My Task 2")
    create_task_for_other_user(title="Other User's Task")

    # Act
    response = client.get("/api/v1/tasks", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2  # Only own tasks
    assert all(task["title"] != "Other User's Task" for task in tasks)

def test_update_other_users_task_returns_404(client, auth_headers, create_task_for_other_user):
    """Auth: Cannot update other user's task"""
    # Arrange
    other_task = create_task_for_other_user(title="Other Task")
    update_data = {"title": "Hacked"}

    # Act
    response = client.put(
        f"/api/v1/tasks/{other_task.id}",
        json=update_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 404

def test_delete_other_users_task_returns_404(client, auth_headers, create_task_for_other_user):
    """Auth: Cannot delete other user's task"""
    # Arrange
    other_task = create_task_for_other_user(title="Other Task")

    # Act
    response = client.delete(
        f"/api/v1/tasks/{other_task.id}",
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 404
```

**Frontend Example:**
```typescript
describe('TaskList - Authentication', () => {
  it('should redirect to login when unauthorized', async () => {
    // Arrange
    const mockPush = vi.fn();
    vi.spyOn(require('next/navigation'), 'useRouter').mockReturnValue({
      push: mockPush
    });

    vi.spyOn(api, 'getTasks').mockRejectedValue(
      new Error('401 Unauthorized')
    );

    // Act
    render(<TaskList />);

    // Assert
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('should handle expired token gracefully', async () => {
    // Arrange
    vi.spyOn(api, 'getTasks').mockRejectedValue(
      new Error('401 Token expired')
    );

    // Act
    render(<TaskList />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/session expired/i)).toBeInTheDocument();
    });
  });
});
```

### 4. Not Found Tests (404)

**Scenarios to generate:**
- Resource doesn't exist
- Soft-deleted resource
- Invalid ID format

**Backend Example:**
```python
def test_get_nonexistent_task_returns_404(client, auth_headers):
    """Not Found: Task doesn't exist"""
    # Act
    response = client.get("/api/v1/tasks/99999", headers=auth_headers)

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_deleted_task_returns_404(client, auth_headers, create_task):
    """Not Found: Soft-deleted task"""
    # Arrange
    task = create_task(title="Task")
    # Soft delete
    client.delete(f"/api/v1/tasks/{task.id}", headers=auth_headers)

    # Act
    response = client.get(f"/api/v1/tasks/{task.id}", headers=auth_headers)

    # Assert
    assert response.status_code == 404

def test_update_nonexistent_task_returns_404(client, auth_headers):
    """Not Found: Cannot update nonexistent task"""
    # Arrange
    update_data = {"title": "Updated"}

    # Act
    response = client.put(
        "/api/v1/tasks/99999",
        json=update_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 404
```

**Frontend Example:**
```typescript
describe('TaskDetail - Not Found', () => {
  it('should show not found message for nonexistent task', async () => {
    // Arrange
    vi.spyOn(api, 'getTask').mockRejectedValue(
      new Error('404 Not found')
    );

    // Act
    render(<TaskDetail id={99999} />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/task not found/i)).toBeInTheDocument();
    });
  });
});
```

### 5. Edge Case Tests

**Scenarios to generate:**
- Empty strings
- Maximum length values
- Minimum/maximum numbers
- Special characters
- Null/undefined values
- Empty arrays
- Boundary values

**Backend Example:**
```python
def test_create_task_with_empty_description(client, auth_headers):
    """Edge: Empty description allowed"""
    # Arrange
    task_data = {
        "title": "Task",
        "description": ""
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["description"] == ""

def test_create_task_with_max_length_title(client, auth_headers):
    """Edge: Maximum title length (200 chars)"""
    # Arrange
    max_title = "a" * 200
    task_data = {"title": max_title}

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert len(response.json()["title"]) == 200

def test_create_task_with_special_characters(client, auth_headers):
    """Edge: Special characters in title"""
    # Arrange
    task_data = {"title": "Task @#$%^&*()_+-={}[]|:;<>,.?/~`"}

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert "@#$%" in response.json()["title"]

def test_create_task_with_minimum_priority(client, auth_headers):
    """Edge: Minimum priority value (1)"""
    # Arrange
    task_data = {
        "title": "Task",
        "priority": 1
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["priority"] == 1

def test_create_task_with_maximum_priority(client, auth_headers):
    """Edge: Maximum priority value (5)"""
    # Arrange
    task_data = {
        "title": "Task",
        "priority": 5
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["priority"] == 5

def test_create_task_with_empty_tags_array(client, auth_headers):
    """Edge: Empty tags array"""
    # Arrange
    task_data = {
        "title": "Task",
        "tags": []
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["tags"] == []

def test_create_task_with_many_tags(client, auth_headers):
    """Edge: Many tags"""
    # Arrange
    task_data = {
        "title": "Task",
        "tags": [f"tag{i}" for i in range(50)]
    }

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    assert len(response.json()["tags"]) == 50
```

### 6. Integration Tests (Full Flows)

**Scenarios to generate:**
- Complete CRUD flow
- Authentication → Create → Read → Update → Delete flow
- Multi-step user journeys
- Cross-component interactions

**Backend Integration Example:**
```python
# src/core/backend/tests/integration/test_tasks_full_flow.py
def test_complete_task_lifecycle(client, auth_headers):
    """Integration: Full CRUD lifecycle"""
    # 1. Create task
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "New Task", "priority": 3},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 2. Read task
    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "New Task"

    # 3. Update task
    update_response = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Task"},
        headers=auth_headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"

    # 4. Delete task
    delete_response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 204

    # 5. Verify deletion (soft delete)
    verify_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers
    )
    assert verify_response.status_code == 404
```

**Frontend Integration Example:**
```typescript
// src/core/frontend/tests/integration/task-flow.test.ts
describe('Task Management Flow', () => {
  it('should complete full task lifecycle', async () => {
    // Mock API responses
    const mockTask = { id: 1, title: 'Test Task', description: '', priority: null, tags: [] };

    vi.spyOn(api, 'createTask').mockResolvedValue(mockTask);
    vi.spyOn(api, 'getTasks').mockResolvedValue([mockTask]);
    vi.spyOn(api, 'updateTask').mockResolvedValue({ ...mockTask, title: 'Updated' });
    vi.spyOn(api, 'deleteTask').mockResolvedValue(undefined);

    // 1. Create task
    render(<TaskForm onSuccess={vi.fn()} />);
    await userEvent.type(screen.getByLabelText(/title/i), 'Test Task');
    await userEvent.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(api.createTask).toHaveBeenCalled();
    });

    // 2. View in list
    render(<TaskList />);
    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });

    // 3. Delete task
    await userEvent.click(screen.getByRole('button', { name: /delete/i }));

    await waitFor(() => {
      expect(api.deleteTask).toHaveBeenCalledWith(1);
    });
  });
});
```

## Test Helper Fixtures

Generate reusable fixtures for common operations:

```python
# src/core/backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from backend.main import app
from backend.models.task import Task
from backend.database import get_session

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Test database session"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def auth_headers(client):
    """Generate valid JWT token"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def create_task(db_session):
    """Factory to create tasks"""
    def _create_task(
        title: str = "Test Task",
        user_id: str = "test-user-id",
        **kwargs
    ):
        task = Task(title=title, user_id=user_id, **kwargs)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    return _create_task

@pytest.fixture
def create_task_for_other_user(db_session):
    """Factory to create tasks for different user"""
    def _create_task(
        title: str = "Other Task",
        user_id: str = "other-user-id",
        **kwargs
    ):
        task = Task(title=title, user_id=user_id, **kwargs)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    return _create_task
```

## Key Rules

- **Test all scenarios** - Happy path, validation, auth, edge cases, not found
- **Generate independent tests** - No shared state between tests
- **Use descriptive names** - Test name explains what it tests
- **Follow AAA pattern** - Arrange, Act, Assert structure
- **Mock external dependencies** - Database, API calls, file system
- **Test behavior, not implementation** - Focus on user experience
- **Include fixtures** - Reusable test helpers for common operations
- **User isolation always** - Test that users can't access other users' data
- **Soft deletes** - Test that deleted resources return 404
- **Generate both unit and integration tests** - Cover all layers
- **Type-safe tests** - Use proper TypeScript/Python types
- **Fast tests** - Mock external dependencies, use in-memory database
