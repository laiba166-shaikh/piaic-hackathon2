---
name: test-coverage-auditor
description: Verify test coverage meets acceptance criteria by mapping tests to requirements and identifying gaps. Use when (1) after implementing features, (2) before marking tasks complete, (3) during code review, or (4) user asks "is this tested?".
license: Complete terms in LICENSE.txt
---

# Test Coverage Auditor

Audit test coverage to ensure all acceptance criteria have corresponding tests and identify coverage gaps.

## Workflow

Follow these steps when auditing test coverage:

1. **Map acceptance criteria to test cases**
   - Read acceptance criteria from spec
   - Identify existing test files
   - Match each criterion to specific tests
   - Note which criteria lack tests

2. **Identify untested code paths**
   - Check happy path coverage
   - Verify error case coverage
   - Look for edge case tests
   - Note missing test scenarios

3. **Check test quality (not just quantity)**
   - Tests are behavior-focused
   - Tests are independent
   - Tests use proper assertions
   - Tests have clear names

4. **Verify edge cases are covered**
   - Empty/null values
   - Maximum/minimum boundaries
   - Special characters
   - Concurrent operations

5. **Report coverage gaps**
   - List untested acceptance criteria
   - Identify missing error cases
   - Note untested edge cases
   - Suggest additional tests

## Output Format

Present test coverage audit using this structure:

```
🧪 Test Coverage Audit: [feature-name]

Source Specification: specs/phase2/features/tasks.md

Acceptance Criteria Coverage:

✅ TESTED:
1. "User can create a task with title and description"
   → src/core/backend/tests/unit/test_tasks.py::test_create_task
   → src/core/frontend/tests/unit/TaskForm.test.tsx::should create task

2. "Task requires a title (validation)"
   → src/core/backend/tests/unit/test_tasks.py::test_create_task_without_title_returns_400
   → src/core/frontend/tests/unit/TaskForm.test.tsx::should show error for missing title

❌ UNTESTED:
3. "Task shows created date in user's timezone"
   → NO TESTS FOUND
   → Suggest: Add test_task_created_at_format in backend
   → Suggest: Add should display formatted date in frontend

4. "User cannot access other users' tasks"
   → PARTIAL: Backend has test_get_tasks_filters_by_user
   → Missing: Frontend test for 403 forbidden handling

Test Files Reviewed:
- src/core/backend/tests/unit/test_tasks.py (12 tests)
- src/core/backend/tests/integration/test_tasks_api.py (8 tests)
- src/core/frontend/tests/unit/TaskList.test.tsx (6 tests)
- src/core/frontend/tests/unit/TaskForm.test.tsx (5 tests)

Coverage Statistics:
- Acceptance Criteria: 8 total, 6 tested (75%)
- Happy Paths: 8/8 tested (100%)
- Error Cases: 5/8 tested (63%)
- Edge Cases: 3/8 tested (38%)
- User Isolation: 4/4 tested (100%)

Coverage Gaps:

1. Missing: Error handling for 500 server errors
   Location: Frontend TaskForm component
   Severity: Medium
   Fix: Add test for network failure scenario

2. Missing: Edge case for maximum title length (200 chars)
   Location: Backend validation tests
   Severity: Low
   Fix: Add test_create_task_with_max_length_title

3. Missing: Concurrent task creation test
   Location: Backend integration tests
   Severity: Low
   Fix: Add test_concurrent_task_creation

Recommendations:
1. Add 3 missing tests for untested acceptance criteria
2. Improve edge case coverage (currently 38%, target 80%)
3. Add integration test for full create-read-update-delete flow
```

## Coverage Requirements Checklist

For each feature, verify these test categories:

### ✅ Happy Path Tests

**What to Test:**
- Success scenarios with valid input
- Expected responses and status codes
- Data persistence and retrieval
- Correct state changes

**Example (Backend):**
```python
def test_create_task_returns_201_with_task_data(client, auth_headers):
    """Happy path: Create task with valid data"""
    response = client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "description": "Test Description"
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "created_at" in data
```

**Example (Frontend):**
```typescript
it('should create task successfully', async () => {
  render(<TaskForm onSuccess={mockOnSuccess} />);

  await userEvent.type(screen.getByLabelText(/title/i), 'New Task');
  await userEvent.click(screen.getByRole('button', { name: /create/i }));

  await waitFor(() => {
    expect(mockOnSuccess).toHaveBeenCalled();
  });
});
```

**Checklist:**
- [ ] Test passes with valid input
- [ ] Correct status code returned
- [ ] Response data matches schema
- [ ] Database updated correctly
- [ ] UI updates as expected

### ✅ Validation Error Tests

**What to Test:**
- Missing required fields
- Invalid data types
- Out-of-range values
- Format validation (email, date, etc.)

**Example (Backend):**
```python
def test_create_task_without_title_returns_400(client, auth_headers):
    """Validation: Title is required"""
    response = client.post("/api/v1/tasks", json={
        "description": "No title"
    }, headers=auth_headers)

    assert response.status_code == 400
    assert "title" in response.json()["detail"].lower()

def test_create_task_with_invalid_priority_returns_400(client, auth_headers):
    """Validation: Priority must be 1-5"""
    response = client.post("/api/v1/tasks", json={
        "title": "Task",
        "priority": 10  # Invalid: out of range
    }, headers=auth_headers)

    assert response.status_code == 400
```

**Example (Frontend):**
```typescript
it('should show error for missing title', async () => {
  render(<TaskForm />);

  await userEvent.click(screen.getByRole('button', { name: /create/i }));

  expect(screen.getByText(/title is required/i)).toBeInTheDocument();
});

it('should show error for invalid priority', async () => {
  render(<TaskForm />);

  await userEvent.type(screen.getByLabelText(/priority/i), '10');
  await userEvent.click(screen.getByRole('button', { name: /create/i }));

  expect(screen.getByText(/priority must be between 1 and 5/i)).toBeInTheDocument();
});
```

**Checklist:**
- [ ] Missing required fields tested
- [ ] Invalid types tested
- [ ] Out-of-range values tested
- [ ] Format validation tested
- [ ] Error messages are clear

### ✅ Authentication/Authorization Tests

**What to Test:**
- Missing authentication token (401)
- Invalid/expired token (401)
- Accessing other user's data (403/404)
- User isolation enforced

**Example (Backend):**
```python
def test_create_task_without_auth_returns_401(client):
    """Auth: Authentication required"""
    response = client.post("/api/v1/tasks", json={
        "title": "Task"
    })  # No auth headers

    assert response.status_code == 401

def test_get_task_filters_by_user_id(client, auth_headers, other_user_task):
    """Auth: Cannot access other user's task"""
    response = client.get(
        f"/api/v1/tasks/{other_user_task.id}",
        headers=auth_headers
    )

    assert response.status_code == 404  # Not found for this user
```

**Example (Frontend):**
```typescript
it('should redirect to login when unauthorized', async () => {
  const mockPush = jest.fn();
  jest.spyOn(require('next/navigation'), 'useRouter').mockReturnValue({
    push: mockPush
  });

  // Mock API to return 401
  global.fetch = jest.fn().mockResolvedValue({
    ok: false,
    status: 401,
  });

  render(<TaskList />);

  await waitFor(() => {
    expect(mockPush).toHaveBeenCalledWith('/login');
  });
});
```

**Checklist:**
- [ ] 401 for missing token
- [ ] 401 for invalid token
- [ ] User isolation enforced
- [ ] No cross-user data access
- [ ] Proper redirects to login

### ✅ Not Found Tests

**What to Test:**
- Resource doesn't exist (404)
- Soft-deleted resource (404)
- Invalid ID format

**Example (Backend):**
```python
def test_get_nonexistent_task_returns_404(client, auth_headers):
    """Not Found: Task doesn't exist"""
    response = client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert response.status_code == 404

def test_get_deleted_task_returns_404(client, auth_headers, deleted_task):
    """Not Found: Soft-deleted task not accessible"""
    response = client.get(
        f"/api/v1/tasks/{deleted_task.id}",
        headers=auth_headers
    )
    assert response.status_code == 404
```

**Checklist:**
- [ ] 404 for nonexistent resource
- [ ] 404 for soft-deleted resource
- [ ] Clear error message
- [ ] Frontend handles gracefully

### ✅ Edge Case Tests

**What to Test:**
- Empty strings
- Maximum length values
- Special characters
- Null/undefined values
- Empty arrays/lists
- Boundary values (0, -1, MAX_INT)

**Example (Backend):**
```python
def test_create_task_with_max_length_title(client, auth_headers):
    """Edge: Maximum title length (200 chars)"""
    long_title = "a" * 200
    response = client.post("/api/v1/tasks", json={
        "title": long_title
    }, headers=auth_headers)

    assert response.status_code == 201
    assert len(response.json()["title"]) == 200

def test_create_task_with_empty_description(client, auth_headers):
    """Edge: Empty description allowed"""
    response = client.post("/api/v1/tasks", json={
        "title": "Task",
        "description": ""
    }, headers=auth_headers)

    assert response.status_code == 201

def test_create_task_with_special_chars_in_title(client, auth_headers):
    """Edge: Special characters in title"""
    response = client.post("/api/v1/tasks", json={
        "title": "Task @#$%^&*() with symbols"
    }, headers=auth_headers)

    assert response.status_code == 201
```

**Checklist:**
- [ ] Empty string tested
- [ ] Maximum length tested
- [ ] Special characters tested
- [ ] Null/undefined tested
- [ ] Boundary values tested

## Test Quality Checks

Beyond coverage, verify test quality:

### ✅ Behavior-Focused Tests

**Good (tests behavior):**
```typescript
it('should display error when task creation fails', async () => {
  // Mock API failure
  jest.spyOn(api, 'createTask').mockRejectedValue(new Error('Failed'));

  render(<TaskForm />);
  await userEvent.type(screen.getByLabelText(/title/i), 'Task');
  await userEvent.click(screen.getByRole('button', { name: /create/i }));

  expect(screen.getByText(/failed to create task/i)).toBeInTheDocument();
});
```

**Bad (tests implementation):**
```typescript
it('should set error state', async () => {
  const { result } = renderHook(() => useTaskForm());

  await act(async () => {
    await result.current.handleSubmit(mockEvent);
  });

  expect(result.current.error).toBe('Failed');  // Testing internal state
});
```

### ✅ Descriptive Test Names

**Good:**
- `test_create_task_without_title_returns_400`
- `should display error when title is missing`
- `test_user_cannot_access_other_users_tasks`

**Bad:**
- `test_task_1`
- `test_error`
- `should work correctly`

### ✅ Arrange-Act-Assert Pattern

```python
def test_update_task_changes_title(client, auth_headers, task):
    # Arrange: Set up test data
    new_title = "Updated Title"
    update_data = {"title": new_title}

    # Act: Perform the action
    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json=update_data,
        headers=auth_headers
    )

    # Assert: Verify the outcome
    assert response.status_code == 200
    assert response.json()["title"] == new_title
```

### ✅ Independent Tests

**Good (independent):**
```python
@pytest.fixture
def task(db_session, user_id):
    task = Task(title="Test", user_id=user_id)
    db_session.add(task)
    db_session.commit()
    return task

def test_delete_task(client, auth_headers, task):
    # Uses fixture, doesn't depend on other tests
    response = client.delete(f"/api/v1/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 204
```

**Bad (dependent):**
```python
task_id = None

def test_create_task(client, auth_headers):
    global task_id
    response = client.post("/api/v1/tasks", ...)
    task_id = response.json()["id"]  # Sets global state

def test_delete_task(client, auth_headers):
    global task_id
    response = client.delete(f"/api/v1/tasks/{task_id}", ...)  # Depends on previous test
```

### ✅ Fast Tests (with Mocks)

**Good (mocked external dependencies):**
```typescript
it('should fetch tasks on mount', async () => {
  jest.spyOn(api, 'getTasks').mockResolvedValue(mockTasks);  // Mock API

  render(<TaskList />);

  await waitFor(() => {
    expect(screen.getByText('Task 1')).toBeInTheDocument();
  });
});
```

**Bad (real API calls):**
```typescript
it('should fetch tasks on mount', async () => {
  // No mocking - makes real API call (slow and brittle)
  render(<TaskList />);

  await waitFor(() => {
    expect(screen.getByText('Task 1')).toBeInTheDocument();
  }, { timeout: 5000 });
});
```

## Coverage Gap Analysis

Systematically identify what's missing:

**1. Map Acceptance Criteria → Tests:**
- List all acceptance criteria from spec
- Find corresponding tests
- Mark as ✅ tested or ❌ untested

**2. Check Error Cases:**
- Validation errors (400)
- Auth errors (401)
- Not found errors (404)
- Server errors (500)

**3. Check Edge Cases:**
- Empty/null values
- Boundaries (min/max)
- Special characters
- Concurrency

**4. Check User Isolation:**
- Can only access own data
- Can't access other users' data
- User_id from JWT enforced

## Key Rules

- **Every acceptance criterion needs a test** - No criterion should be untested
- **Test coverage ≠ test quality** - 100% line coverage with bad tests is useless
- **Behavior over implementation** - Test what users experience, not internal code
- **Auth and user isolation always tested** - Security is non-negotiable
- **Edge cases matter** - Empty, null, boundaries must be covered
- **Independent tests** - No shared state between tests
- **Fast tests** - Mock external dependencies (API, DB, file system)
- **Descriptive names** - Test name should explain what it tests
- **Gaps must be fixed** - Untested code is risky code
- **Review before merge** - No PRs merged with untested features
