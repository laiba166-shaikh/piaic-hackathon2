---
name: tdd-conductor
description: Guide test-driven development workflow using Red-Green-Refactor cycle. Use when (1) starting any new feature implementation, (2) user asks to "implement X with TDD", (3) after spec interpretation and before coding, or (4) reviewing implementation approach to ensure tests-first.
license: Complete terms in LICENSE.txt
---

# TDD Conductor

Guide the test-driven development workflow to ensure tests are written before implementation, following the Red-Green-Refactor cycle.

## Workflow

Follow these TDD phases in strict order:

### 🔴 Phase 1: RED - Write Failing Tests

1. **Read acceptance criteria from spec**
   - Extract testable requirements
   - Identify expected behaviors
   - Note edge cases and error conditions

2. **Write test that captures the requirement**
   - Test behavior, not implementation
   - Use descriptive test names
   - Follow Arrange-Act-Assert pattern
   - One test per acceptance criterion

3. **Run test - must FAIL**
   - Execute test suite
   - Verify test fails (not error, but assertion failure)
   - Confirm test fails for the RIGHT reason

4. **Verify failure is correct**
   - Test should fail because feature doesn't exist yet
   - Not because of typos, import errors, or test bugs
   - Failure message should be clear and expected

### 🟢 Phase 2: GREEN - Make Tests Pass

1. **Write minimum code to pass tests**
   - Simplest implementation that works
   - No extra features or "nice to haves"
   - No premature optimization
   - Focus only on making the test green

2. **Run tests - must PASS**
   - Execute full test suite
   - New test passes
   - All existing tests still pass

3. **Verify all tests pass**
   - No skipped tests
   - No intermittent failures
   - Clean test output

### 🔄 Phase 3: REFACTOR - Improve Code

1. **Clean up implementation**
   - Remove duplication
   - Improve naming
   - Extract functions/methods
   - Simplify logic

2. **Run tests - must still PASS**
   - Tests should still pass after refactoring
   - No behavior changes
   - Only structure improvements

3. **Refactor tests if needed**
   - Remove test duplication
   - Improve test clarity
   - Extract test helpers

## Output Format

Present TDD workflow guidance using this structure:

```
🧪 TDD Workflow: [feature-name]

Current Phase: 🔴 RED (write failing tests)

Acceptance Criteria → Test Cases:
1. "User can create a task"
   → test_create_task_returns_201_with_task_data()

2. "Task requires title field"
   → test_create_task_without_title_returns_400()

3. "Task belongs to authenticated user"
   → test_create_task_uses_user_from_jwt()

Suggested Test (RED phase):
[code snippet for failing test]

Next Steps:
1. Write the test above
2. Run test suite (should FAIL)
3. Verify it fails for the right reason
4. Then implement feature (GREEN phase)
```

## Test Patterns by Layer

### Backend Tests (Pytest + FastAPI TestClient)

**Unit Test Pattern:**
```python
# backend/tests/unit/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Login and get JWT token
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_task_returns_201_with_task_data(client, auth_headers):
    """Test: User can create a task"""
    # Arrange
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
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
    assert "id" in data
    assert "created_at" in data

def test_create_task_without_title_returns_400(client, auth_headers):
    """Test: Task requires title field"""
    # Arrange
    invalid_data = {"description": "No title"}

    # Act
    response = client.post(
        "/api/v1/tasks",
        json=invalid_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 400
    assert "title" in response.json()["detail"].lower()

def test_create_task_without_auth_returns_401(client):
    """Test: Authentication required for task creation"""
    # Arrange
    task_data = {"title": "Test"}

    # Act
    response = client.post("/api/v1/tasks", json=task_data)

    # Assert
    assert response.status_code == 401
```

### Frontend Tests (Vitest + React Testing Library)

**Component Test Pattern:**
```typescript
// frontend/tests/unit/TaskList.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskList } from '@/components/tasks/TaskList';

describe('TaskList', () => {
  const mockTasks = [
    { id: 1, title: 'Task 1', description: 'Desc 1' },
    { id: 2, title: 'Task 2', description: 'Desc 2' }
  ];

  it('renders list of tasks', () => {
    // Arrange & Act
    render(<TaskList tasks={mockTasks} onDelete={vi.fn()} />);

    // Assert
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });

  it('calls onDelete when delete button clicked', async () => {
    // Arrange
    const handleDelete = vi.fn();
    render(<TaskList tasks={mockTasks} onDelete={handleDelete} />);

    // Act
    const deleteButton = screen.getAllByRole('button', { name: /delete/i })[0];
    await userEvent.click(deleteButton);

    // Assert
    expect(handleDelete).toHaveBeenCalledWith(1);
  });

  it('shows empty state when no tasks', () => {
    // Arrange & Act
    render(<TaskList tasks={[]} onDelete={vi.fn()} />);

    // Assert
    expect(screen.getByText(/no tasks/i)).toBeInTheDocument();
  });
});
```

**API Integration Test Pattern:**
```typescript
// frontend/tests/integration/api.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from '@/lib/api';

// Mock fetch
global.fetch = vi.fn();

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getTasks includes auth header', async () => {
    // Arrange
    const mockTasks = [{ id: 1, title: 'Test' }];
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks
    });

    // Act
    await api.getTasks();

    // Assert
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/tasks'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': expect.stringContaining('Bearer ')
        })
      })
    );
  });

  it('createTask sends correct data', async () => {
    // Arrange
    const taskData = { title: 'New Task' };
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, ...taskData })
    });

    // Act
    await api.createTask(taskData);

    // Assert
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/tasks'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(taskData)
      })
    );
  });
});
```

## Test Coverage Checklist

For each feature, ensure tests cover:

**✅ Happy Path:**
- [ ] Success case with valid input
- [ ] Correct status code (200, 201, 204)
- [ ] Response matches expected schema
- [ ] Data persisted correctly

**✅ Validation Errors:**
- [ ] Missing required fields (400)
- [ ] Invalid data types (400)
- [ ] Out of range values (400)
- [ ] Format validation (email, date, etc.)

**✅ Authentication/Authorization:**
- [ ] Missing auth token (401)
- [ ] Invalid/expired token (401)
- [ ] Accessing other user's data (403)

**✅ Not Found Errors:**
- [ ] Resource doesn't exist (404)
- [ ] Soft-deleted resource (404)

**✅ Edge Cases:**
- [ ] Empty strings
- [ ] Maximum length values
- [ ] Special characters
- [ ] Null/undefined values
- [ ] Empty arrays/lists

**✅ User Isolation:**
- [ ] Can only access own data
- [ ] Can't see other users' data
- [ ] User_id from JWT, not URL/body

## Anti-Patterns to Flag

**❌ Implementation Before Tests:**
```
User: "Let me implement the feature first, then add tests"
Assistant: "STOP! TDD requires tests first. Let's write failing tests now."
```

**❌ Tests That Always Pass:**
```python
def test_task_creation():
    # This test passes even if create_task is broken!
    assert True
```

**❌ Testing Implementation Details:**
```typescript
// BAD: Testing internal state
expect(component.state.isLoading).toBe(false);

// GOOD: Testing behavior
expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
```

**❌ Skipping Refactor Phase:**
```
# After getting tests to pass
User: "Great, let's move to the next feature"
Assistant: "Wait! Let's refactor first. I see duplication we can remove."
```

**❌ Mocking Everything:**
```python
# BAD: Over-mocking makes tests brittle
@patch('module.function1')
@patch('module.function2')
@patch('module.function3')
def test_something(mock3, mock2, mock1):
    # Test knows too much about implementation
```

## Key Rules

- **Never implement before writing tests** - Red phase always comes first
- **Tests must fail before implementation** - Verify red, then make green
- **One test at a time** - Don't write all tests upfront, iterate
- **Test behavior, not implementation** - Focus on what, not how
- **Acceptance criteria drive tests** - Each criterion needs test coverage
- **Mock external dependencies** - Database, API calls, file system
- **Refactor is mandatory** - Don't skip cleanup phase
- **Keep tests fast** - Use mocks, avoid slow operations
- **Independent tests** - No shared state between tests
- **Descriptive test names** - Should read like documentation
