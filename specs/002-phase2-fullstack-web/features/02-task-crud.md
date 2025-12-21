# Feature: Task CRUD Operations

## Overview

Task CRUD operations form the foundation of the web-based todo application, enabling users to create, read, update, and delete their personal tasks through a RESTful API and web interface. This feature implements multi-user task management with strict user isolation, ensuring each authenticated user can only access and modify their own tasks. All task operations require JWT authentication and follow Phase 2 architectural patterns including soft deletes and user_id filtering.

## Priority

**Level:** Critical

**Rationale:** Task CRUD is the core feature that all other task-related features depend on (priority, tags, due dates, completion tracking). Without basic task operations, the application cannot function. This is the first feature to implement in Phase 2 and blocks all subsequent feature development.

## Dependencies

**Required Before Implementation:**
- User Authentication: Need valid JWT tokens with user_id claims for all operations
- Database Setup: PostgreSQL database with tasks table and required indexes
- Backend Framework: FastAPI application structure with middleware for JWT validation
- Frontend Framework: Next.js application structure with centralized API client

**Optional/Nice-to-Have:**
- None

**External Dependencies:**
- Neon PostgreSQL database (serverless PostgreSQL hosting)
- Better Auth library (JWT token generation and validation)
- SQLModel (Python ORM for type-safe database operations)

## User Stories

### Story 1: Create New Task
**As a** logged-in user
**I want** to create a new task with a title and optional description
**So that** I can track work items I need to complete

### Story 2: View All My Tasks
**As a** logged-in user
**I want** to see a list of all my tasks
**So that** I can review what I need to do

### Story 3: View Single Task Details
**As a** logged-in user
**I want** to view the full details of a specific task
**So that** I can see all information about that task

### Story 4: Update Task Information
**As a** logged-in user
**I want** to edit a task's title and description
**So that** I can keep my task information accurate and up-to-date

### Story 5: Delete Task
**As a** logged-in user
**I want** to delete a task I no longer need
**So that** my task list stays clean and relevant

### Story 6: User Isolation
**As a** logged-in user
**I want** to only see and manage my own tasks
**So that** my personal task data remains private and separate from other users

## Acceptance Criteria

### AC1: Create Task with Title Only
**Given** I am authenticated with a valid JWT token
**When** I submit a request to create a task with title "Buy groceries"
**Then** the task is created in the database with my user_id from the JWT
**And** the response includes the task with id, title, created_at, and updated_at fields
**And** the task has completed=false as default

### AC2: Create Task with Title and Description
**Given** I am authenticated with a valid JWT token
**When** I submit a request to create a task with title "Project meeting" and description "Discuss Q4 goals"
**Then** the task is created with both title and description stored
**And** the response includes all task fields including the description
**And** the task is associated with my user_id

### AC3: Title Validation
**Given** I am authenticated and creating a task
**When** I submit a task without a title (empty or null)
**Then** I receive a 400 Bad Request error
**And** the error message states "Title is required"
**And** no task is created in the database

### AC4: Title Length Validation
**Given** I am authenticated and creating a task
**When** I submit a task with a title longer than 200 characters
**Then** I receive a 400 Bad Request error
**And** the error message states "Title must not exceed 200 characters"
**And** no task is created in the database

### AC5: List All User Tasks
**Given** I am authenticated with user_id "user123"
**And** I have 3 tasks in the database
**And** another user "user456" has 5 tasks
**When** I request the list of tasks
**Then** I receive only my 3 tasks in the response
**And** the response does not include tasks from "user456"
**And** all returned tasks have deleted_at = null (non-deleted tasks only)

### AC6: Get Single Task by ID
**Given** I am authenticated as "user123"
**And** I have a task with id=10
**When** I request GET /api/v1/tasks/10
**Then** I receive the complete task details
**And** the task includes all fields (id, title, description, completed, user_id, created_at, updated_at, deleted_at)

### AC7: Cannot Access Other User's Task
**Given** I am authenticated as "user123"
**And** a task with id=20 exists but belongs to "user456"
**When** I request GET /api/v1/tasks/20
**Then** I receive a 404 Not Found error
**And** the error message states "Task not found"
**And** the task owner information is not exposed in the error

### AC8: Update Task Title
**Given** I am authenticated and have a task with id=5 and title "Old title"
**When** I send a PUT request with title "New title"
**Then** the task title is updated to "New title"
**And** the updated_at timestamp is refreshed to the current time
**And** the created_at timestamp remains unchanged
**And** the response includes the updated task

### AC9: Update Task Description
**Given** I am authenticated and have a task with id=7
**When** I send a PUT request with description "Updated description"
**Then** the task description is updated
**And** the updated_at timestamp is refreshed
**And** other fields (title, completed, etc.) remain unchanged

### AC10: Update Multiple Fields
**Given** I am authenticated and have a task with id=8
**When** I send a PUT request with both title and description changes
**Then** both fields are updated atomically
**And** the updated_at timestamp reflects the update time
**And** the response includes all updated fields

### AC11: Soft Delete Task
**Given** I am authenticated and have a task with id=12
**When** I send a DELETE request to /api/v1/tasks/12
**Then** the task is not removed from the database
**And** the deleted_at field is set to the current timestamp
**And** the task no longer appears in GET /api/v1/tasks list
**And** I receive a 204 No Content response

### AC12: Cannot Update Deleted Task
**Given** I have a task with id=15 that has been soft-deleted (deleted_at is set)
**When** I attempt to update the task with PUT /api/v1/tasks/15
**Then** I receive a 404 Not Found error
**And** the error message states "Task not found"
**And** the task remains deleted (updated_at is not changed)

### AC13: Cannot Delete Other User's Task
**Given** I am authenticated as "user123"
**And** a task with id=25 exists but belongs to "user456"
**When** I send DELETE /api/v1/tasks/25
**Then** I receive a 404 Not Found error
**And** the task remains unchanged in the database
**And** no deletion occurs

### AC14: Unauthenticated Request Rejected
**Given** I do not provide a valid JWT token in the Authorization header
**When** I attempt any task operation (GET, POST, PUT, DELETE)
**Then** I receive a 401 Unauthorized error
**And** the error message states "Invalid or expired token"
**And** no operation is performed

### AC15: Empty Task List
**Given** I am authenticated as a new user with no tasks
**When** I request GET /api/v1/tasks
**Then** I receive a successful 200 OK response
**And** the response is an empty array []
**And** no error occurs

## Edge Cases

### Edge Case 1: Title with Special Characters
**Scenario:** User creates task with title containing special characters, emoji, or Unicode
**Expected Behavior:** Task created successfully, special characters stored and retrieved correctly
**Validation:** POST task with title "Fix bug 🐛 in <script>", verify exact title returned

### Edge Case 2: Very Long Description
**Scenario:** User creates task with description containing 10,000 characters (within TEXT field limits)
**Expected Behavior:** Task created successfully, full description stored
**Validation:** POST task with 10k char description, GET task returns complete description

### Edge Case 3: Null Description
**Scenario:** User creates task without providing description field
**Expected Behavior:** Task created with description = null
**Validation:** POST with only title, GET returns description: null

### Edge Case 4: Empty String Description
**Scenario:** User creates task with description = "" (empty string)
**Expected Behavior:** Task created with description = "" (stored as empty string, not null)
**Validation:** POST with description: "", GET returns description: ""

### Edge Case 5: Title Exactly 200 Characters
**Scenario:** User creates task with title at maximum boundary (200 chars)
**Expected Behavior:** Task created successfully, no validation error
**Validation:** POST with 200-char title, verify success and full title returned

### Edge Case 6: Title 201 Characters
**Scenario:** User creates task with title exceeding limit (201 chars)
**Expected Behavior:** Validation error 400 "Title must not exceed 200 characters"
**Validation:** POST with 201-char title, verify 400 error and no task created

### Edge Case 7: Whitespace-Only Title
**Scenario:** User submits task with title containing only spaces "   "
**Expected Behavior:** Validation error 400 "Title is required" (whitespace trimmed)
**Validation:** POST with whitespace title, verify error and no task created

### Edge Case 8: Concurrent Updates
**Scenario:** Two browser tabs update the same task simultaneously
**Expected Behavior:** Last write wins, both updates succeed, final state shows last update
**Validation:** Send two PUT requests concurrently, verify both return 200, last update persists

### Edge Case 9: Update Non-Existent Task
**Scenario:** User attempts to update task with id=99999 that doesn't exist
**Expected Behavior:** 404 Not Found error "Task not found"
**Validation:** PUT /api/v1/tasks/99999, verify 404 response

### Edge Case 10: Delete Already Deleted Task
**Scenario:** User deletes task id=30, then deletes it again
**Expected Behavior:** Second delete returns 404 Not Found (task already soft-deleted)
**Validation:** DELETE task twice, first returns 204, second returns 404

### Edge Case 11: Invalid Task ID Format
**Scenario:** User requests task with non-numeric ID like /api/v1/tasks/abc
**Expected Behavior:** 422 Unprocessable Entity error "Invalid task ID format"
**Validation:** GET /api/v1/tasks/abc, verify 422 error

### Edge Case 12: Task ID Zero or Negative
**Scenario:** User requests /api/v1/tasks/0 or /api/v1/tasks/-5
**Expected Behavior:** 404 Not Found (IDs start at 1, invalid IDs treated as not found)
**Validation:** GET with id=0 or negative, verify 404 response

### Edge Case 13: JWT Token Missing user_id Claim
**Scenario:** Request has valid JWT signature but missing user_id claim
**Expected Behavior:** 401 Unauthorized error "Invalid token: missing user_id claim"
**Validation:** Send request with malformed JWT, verify 401 and helpful error message

### Edge Case 14: JWT Token Expired
**Scenario:** User's JWT token has expired (exp claim in past)
**Expected Behavior:** 401 Unauthorized error "Invalid or expired token"
**Validation:** Send request with expired JWT, verify 401 and user prompted to re-login

### Edge Case 15: Update with No Changes
**Scenario:** User submits PUT request with same title and description (no actual changes)
**Expected Behavior:** Update succeeds, updated_at timestamp is refreshed despite no content changes
**Validation:** PUT with identical data, verify 200 response and new updated_at

## Error Handling

### Error 1: Missing Title
**Scenario:** User creates task without title field or with null/empty title
**HTTP Status:** 400 Bad Request
**Error Response:**
```json
{
  "detail": "Title is required"
}
```
**User-Facing Message:** "Please enter a task title"
**Recovery:** User enters a valid title and resubmits

### Error 2: Title Too Long
**Scenario:** User provides title longer than 200 characters
**HTTP Status:** 400 Bad Request
**Error Response:**
```json
{
  "detail": "Title must not exceed 200 characters"
}
```
**User-Facing Message:** "Task title is too long (maximum 200 characters)"
**Recovery:** User shortens title and resubmits

### Error 3: Invalid Request Body
**Scenario:** API receives malformed JSON or wrong data types
**HTTP Status:** 422 Unprocessable Entity
**Error Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "completed"],
      "msg": "value is not a valid boolean",
      "type": "type_error.boolean"
    }
  ]
}
```
**User-Facing Message:** "Invalid data format. Please try again."
**Recovery:** Frontend validation prevents this, user retries

### Error 4: Unauthenticated Request
**Scenario:** Request missing Authorization header or invalid JWT token
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid or expired token"
}
```
**User-Facing Message:** "Your session has expired. Please log in again."
**Recovery:** User is redirected to login page, authenticates, and retries

### Error 5: Task Not Found
**Scenario:** User attempts to GET, PUT, or DELETE task that doesn't exist or belongs to another user
**HTTP Status:** 404 Not Found
**Error Response:**
```json
{
  "detail": "Task not found"
}
```
**User-Facing Message:** "This task no longer exists or has been deleted."
**Recovery:** User refreshes task list, removed task disappears from UI

### Error 6: Invalid Task ID
**Scenario:** User provides non-numeric or invalid task ID in URL path
**HTTP Status:** 422 Unprocessable Entity
**Error Response:**
```json
{
  "detail": [
    {
      "loc": ["path", "id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```
**User-Facing Message:** "Invalid task reference. Please try again."
**Recovery:** User navigates back to task list, clicks valid task

### Error 7: Database Connection Failure
**Scenario:** Database is unavailable or connection pool exhausted
**HTTP Status:** 500 Internal Server Error
**Error Response:**
```json
{
  "detail": "An error occurred while processing your request"
}
```
**User-Facing Message:** "Something went wrong. Please try again in a moment."
**Recovery:** User retries after a few seconds, error logged for ops team

### Error 8: Database Constraint Violation
**Scenario:** Unexpected database constraint violation (e.g., duplicate ID due to race condition)
**HTTP Status:** 500 Internal Server Error
**Error Response:**
```json
{
  "detail": "An error occurred while processing your request"
}
```
**User-Facing Message:** "Something went wrong. Please try again."
**Recovery:** User retries, ops team investigates logged error

### Error 9: JWT Missing user_id Claim
**Scenario:** JWT token is valid but missing required user_id claim
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid token: missing user_id claim"
}
```
**User-Facing Message:** "Authentication error. Please log in again."
**Recovery:** User logs out and logs back in to get fresh token

### Error 10: Network Timeout
**Scenario:** Request takes longer than configured timeout (e.g., 30 seconds)
**HTTP Status:** 504 Gateway Timeout
**Error Response:**
```json
{
  "detail": "Request timeout"
}
```
**User-Facing Message:** "Request timed out. Please try again."
**Recovery:** User retries operation, check network connection

## Non-Goals

This feature specifically does NOT include:

- **Task completion toggling:** While the completed field exists in the database, toggling completion status is a separate feature (Feature 03: Task Completion). This feature only handles basic CRUD operations.

- **Task priority management:** Priority field and priority-based operations are handled in a separate feature (Feature 04: Task Priority). The priority field is not part of basic CRUD operations.

- **Task tagging:** Tags field (JSONB array) is managed in a separate feature (Feature 05: Task Tags). Basic CRUD does not include tag operations.

- **Task due dates and recurrence:** Due date and recurrence fields are handled separately (Feature 06: Task Due Dates). Not included in basic CRUD scope.

- **Bulk operations:** Creating, updating, or deleting multiple tasks in a single request is deferred to Phase 3. Each operation handles one task at a time.

- **Task search and filtering:** Basic filtering (by priority, tags, status) and simple search by title/description are handled in separate Phase 2 features (Features 04-05). Advanced queries (full-text search, complex boolean queries, saved searches) are deferred to Phase 3. This feature (Task CRUD) returns all user tasks without any filtering.

- **Task archiving:** Soft deletes (deleted_at) provide a deletion mechanism, but archive/restore functionality is deferred to Phase 4.

- **Task history/audit log:** Tracking changes to tasks over time is handled by the audit system in Phase 5. Only created_at and updated_at timestamps are stored.

- **Task sharing or collaboration:** Multi-user access to the same task is Phase 4 (collaborative features). Phase 2 enforces strict user isolation.

- **Real-time updates:** WebSocket or SSE for live task updates across multiple clients is Phase 3. Current implementation requires manual refresh.

- **Optimistic UI updates:** Frontend immediately updating UI before server confirmation is a frontend enhancement, not part of API specification.

- **Pagination:** The task list endpoint returns all user tasks without pagination. Pagination is deferred until needed (Phase 3 if user task volume justifies it).

## API Contract

### Endpoint: POST /api/v1/tasks

**Description:** Create a new task for the authenticated user

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)
  - Content-Type: application/json

- **Request Body:**
  ```json
  {
    "title": "string (required, 1-200 chars)",
    "description": "string (optional, null allowed)"
  }
  ```

**Response:**
- **Success (201 Created):**
  ```json
  {
    "id": "integer (unique task ID)",
    "user_id": "string (from JWT token)",
    "title": "string",
    "description": "string | null",
    "completed": "boolean (default: false)",
    "priority": "string | null (not set in basic CRUD)",
    "tags": "array (default: [])",
    "due_date": "string (ISO 8601) | null (not set in basic CRUD)",
    "recurrence": "string | null (not set in basic CRUD)",
    "deleted_at": "string (ISO 8601) | null (always null on creation)",
    "created_at": "string (ISO 8601 timestamp)",
    "updated_at": "string (ISO 8601 timestamp)"
  }
  ```

- **Errors:**
  - 400 Bad Request: Missing or invalid title
  - 401 Unauthorized: Missing or invalid JWT token
  - 422 Unprocessable Entity: Invalid data types in request body
  - 500 Internal Server Error: Database or server error

---

### Endpoint: GET /api/v1/tasks

**Description:** List all non-deleted tasks for the authenticated user

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)

- **Query Parameters:** None (filtering/sorting not included in basic CRUD)

**Response:**
- **Success (200 OK):**
  ```json
  [
    {
      "id": "integer",
      "user_id": "string",
      "title": "string",
      "description": "string | null",
      "completed": "boolean",
      "priority": "string | null",
      "tags": "array of strings",
      "due_date": "string (ISO 8601) | null",
      "recurrence": "string | null",
      "deleted_at": "string (ISO 8601) | null (always null in list)",
      "created_at": "string (ISO 8601)",
      "updated_at": "string (ISO 8601)"
    }
  ]
  ```
  - Returns empty array [] if user has no tasks

- **Errors:**
  - 401 Unauthorized: Missing or invalid JWT token
  - 500 Internal Server Error: Database or server error

---

### Endpoint: GET /api/v1/tasks/{id}

**Description:** Get a single task by ID (only if owned by authenticated user)

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)

- **Path Parameters:**
  - `id`: integer (required) - Task ID to retrieve

**Response:**
- **Success (200 OK):**
  ```json
  {
    "id": "integer",
    "user_id": "string",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "priority": "string | null",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "recurrence": "string | null",
    "deleted_at": "string (ISO 8601) | null",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  }
  ```

- **Errors:**
  - 401 Unauthorized: Missing or invalid JWT token
  - 404 Not Found: Task doesn't exist, is deleted, or belongs to another user
  - 422 Unprocessable Entity: Invalid task ID format (non-numeric)
  - 500 Internal Server Error: Database or server error

---

### Endpoint: PUT /api/v1/tasks/{id}

**Description:** Update an existing task (only if owned by authenticated user)

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)
  - Content-Type: application/json

- **Path Parameters:**
  - `id`: integer (required) - Task ID to update

- **Request Body:**
  ```json
  {
    "title": "string (optional, 1-200 chars)",
    "description": "string (optional, null allowed)"
  }
  ```
  - All fields are optional, but at least one should be provided
  - Only title and description can be updated in basic CRUD
  - Other fields (completed, priority, tags, etc.) updated by separate features

**Response:**
- **Success (200 OK):**
  ```json
  {
    "id": "integer",
    "user_id": "string",
    "title": "string (updated if provided)",
    "description": "string | null (updated if provided)",
    "completed": "boolean (unchanged)",
    "priority": "string | null (unchanged)",
    "tags": "array (unchanged)",
    "due_date": "string (ISO 8601) | null (unchanged)",
    "recurrence": "string | null (unchanged)",
    "deleted_at": "string (ISO 8601) | null (unchanged)",
    "created_at": "string (ISO 8601, unchanged)",
    "updated_at": "string (ISO 8601, refreshed to current time)"
  }
  ```

- **Errors:**
  - 400 Bad Request: Invalid title (empty or too long)
  - 401 Unauthorized: Missing or invalid JWT token
  - 404 Not Found: Task doesn't exist, is deleted, or belongs to another user
  - 422 Unprocessable Entity: Invalid data types in request body
  - 500 Internal Server Error: Database or server error

---

### Endpoint: DELETE /api/v1/tasks/{id}

**Description:** Soft delete a task (set deleted_at timestamp, don't remove from database)

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)

- **Path Parameters:**
  - `id`: integer (required) - Task ID to delete

**Response:**
- **Success (204 No Content):**
  - No response body
  - Task's deleted_at field set to current timestamp
  - Task no longer appears in GET /api/v1/tasks list

- **Errors:**
  - 401 Unauthorized: Missing or invalid JWT token
  - 404 Not Found: Task doesn't exist, already deleted, or belongs to another user
  - 422 Unprocessable Entity: Invalid task ID format (non-numeric)
  - 500 Internal Server Error: Database or server error

---

### Common Response Headers (All Endpoints)

```
Content-Type: application/json
X-Request-ID: <unique-request-id>
```

### Common Error Response Format

All error responses follow this structure:
```json
{
  "detail": "string (error message)"
}
```

Or for validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body" | "path" | "query", "field_name"],
      "msg": "string (error description)",
      "type": "string (error type)"
    }
  ]
}
```

## Data Model

### Task

**Fields:**
- `id`: integer (auto-increment, primary key) - Unique task identifier
- `user_id`: string (required, indexed, not null) - Owner's user ID from JWT token claim
- `title`: string (required, not null, max 200 chars) - Task title
- `description`: text (optional, nullable) - Detailed task description
- `completed`: boolean (required, not null, default: false) - Task completion status
- `priority`: string (optional, nullable, max 20 chars) - Task priority level (managed by separate feature)
- `tags`: JSONB (required, not null, default: '[]') - Array of tag strings (managed by separate feature)
- `due_date`: timestamp with time zone (optional, nullable) - Task deadline (managed by separate feature)
- `recurrence`: string (optional, nullable, max 20 chars) - Recurrence pattern (managed by separate feature)
- `deleted_at`: timestamp with time zone (optional, nullable) - Soft delete timestamp
- `created_at`: timestamp with time zone (required, not null, auto-set on insert) - Creation timestamp
- `updated_at`: timestamp with time zone (required, not null, auto-update on change) - Last modification timestamp

**Indexes:**
- `PRIMARY KEY (id)` - Primary key index on id
- `idx_tasks_user_id` on user_id - Frequent queries filtering by user
- `idx_tasks_deleted_at` on deleted_at WHERE deleted_at IS NULL - Optimize soft delete filtering
- `idx_tasks_user_deleted` composite on (user_id, deleted_at) - Optimize combined user + soft delete queries

**Constraints:**
- `user_id` cannot be null (every task must have an owner)
- `title` cannot be null and must be 1-200 characters
- `title` cannot be empty after trimming whitespace
- `completed` cannot be null (must be true or false)
- `tags` cannot be null (use empty array [] if no tags)
- `created_at` cannot be null (auto-set by database)
- `updated_at` cannot be null (auto-set and auto-updated by database)

**Validation Rules:**
- **Title:** Required, must be 1-200 characters after trimming, cannot be whitespace-only
- **Description:** Optional, can be null or any text length supported by TEXT column
- **user_id:** Automatically extracted from JWT token, never accepted from request body
- **User isolation:** ALL queries MUST filter by `user_id = <authenticated_user_id>` AND `deleted_at IS NULL`
- **Soft deletes:** DELETE operations set `deleted_at = NOW()` instead of removing row
- **Timestamps:** `created_at` set once on insert, `updated_at` refreshed on every update

**Database Migration Notes:**
- Create tasks table with all fields including Phase 2 required patterns (user_id, deleted_at, created_at, updated_at)
- Create indexes for performance (user_id, deleted_at, composite)
- Set up auto-update trigger for updated_at timestamp (or use SQLModel hooks)
- Ensure PostgreSQL JSONB extension available for tags field

## UI/UX Requirements

### UI Element 1: Task Creation Form
**Purpose:** Allow user to create a new task
**Location:** Main page or modal dialog, accessible from task list view
**Behavior:**
- Form with two input fields: Title (required) and Description (optional)
- Title field has character counter showing "X/200 characters"
- Submit button labeled "Add Task" or "Create Task"
- Cancel button to close form without saving
- On submit, send POST /api/v1/tasks request via centralized API client
- On success, show brief success message "Task created" and add task to list
- On error, display error message inline in form

**States:**
- Empty state: Both fields empty, submit button disabled until title entered
- Editing: User typing in fields, submit button enabled when title valid
- Submitting: Loading spinner on submit button, form inputs disabled
- Success: Brief success indicator (green checkmark, 2 seconds), form clears
- Error: Error message displayed below form, form remains editable

### UI Element 2: Task List View
**Purpose:** Display all user's tasks in a list
**Location:** Main page, primary view when user logs in
**Behavior:**
- Fetch tasks on component mount via GET /api/v1/tasks
- Display each task as a list item or card showing title
- Click on task item to view full details (navigate to detail view or expand inline)
- Show task count "X tasks" at top of list
- If no tasks, show empty state message "No tasks yet. Create your first task!"

**States:**
- Loading: Skeleton loaders or spinner while fetching tasks
- Loaded with tasks: List of task items displayed
- Empty: Empty state message and illustration
- Error: Error message "Unable to load tasks. Try again." with retry button
- Refreshing: Pull-to-refresh or manual refresh button

### UI Element 3: Task List Item
**Purpose:** Show task summary in the list
**Location:** Each row/card in the task list
**Behavior:**
- Display task title prominently
- Show created date/time in relative format ("2 hours ago", "Yesterday")
- Clickable area to view full task details
- Edit and Delete action buttons (icon buttons or dropdown menu)
- Hover effect to indicate clickable/interactive

**States:**
- Default: Title and metadata visible, actions hidden or subtle
- Hover: Highlight item, show action buttons
- Selected: If in detail view, corresponding list item highlighted
- Deleting: Fade out animation when delete succeeds

### UI Element 4: Task Detail View
**Purpose:** Show complete task information
**Location:** Separate page, modal, or expanded section in task list
**Behavior:**
- Display task title as heading
- Show full description (if present) or "No description" placeholder
- Display all metadata: Created date, Last updated date
- Edit button to enter edit mode
- Delete button to remove task
- Back/Close button to return to list view

**States:**
- Viewing: All fields read-only, displayed as formatted text
- Loading: Skeleton or spinner while fetching task
- Error: "Task not found" message if task deleted or invalid ID
- Not found: 404 state with message and link back to task list

### UI Element 5: Task Edit Form
**Purpose:** Allow user to update task title and description
**Location:** Inline edit in list item, or separate edit page/modal
**Behavior:**
- Pre-populate form fields with current task title and description
- Same validation as create form (title required, max 200 chars)
- Save button to submit changes via PUT /api/v1/tasks/{id}
- Cancel button to discard changes and revert to view mode
- On success, update task in list without full page refresh

**States:**
- Editing: Fields editable, save/cancel buttons visible
- Saving: Loading spinner on save button, fields disabled
- Success: Brief success message "Task updated", return to view mode
- Error: Error message inline, form remains editable for corrections

### UI Element 6: Task Delete Confirmation
**Purpose:** Confirm user intent before deleting task
**Location:** Modal dialog or inline confirmation prompt
**Behavior:**
- Trigger when user clicks delete button on task
- Show confirmation message "Are you sure you want to delete '[Task Title]'?"
- Two buttons: "Delete" (destructive action, red/danger color) and "Cancel"
- On confirm, send DELETE /api/v1/tasks/{id} request
- On success, remove task from list with animation
- On cancel, close dialog without action

**States:**
- Confirmation: Dialog visible, awaiting user choice
- Deleting: Loading spinner on delete button
- Success: Task fades out from list, confirmation closes
- Error: Error message in dialog, user can retry or cancel

### UI Element 7: Error Messages
**Purpose:** Communicate errors to user clearly
**Location:** Inline in forms, toast notifications, or modal dialogs
**Behavior:**
- Display user-friendly error messages from API error responses
- Map technical errors to understandable messages (see Error Handling section)
- Provide actionable recovery steps where applicable
- Auto-dismiss non-critical errors after 5 seconds
- Critical errors (401 auth) trigger redirect to login

**States:**
- Info: Blue/neutral color, informational messages
- Warning: Yellow/orange, non-blocking issues
- Error: Red, operation failed but recoverable
- Critical: Red with icon, requires immediate action (session expired)

### UI Element 8: Loading States
**Purpose:** Indicate operations in progress
**Location:** Throughout task CRUD UI components
**Behavior:**
- Show loading indicator during API requests
- Disable interactive elements during loading to prevent duplicate requests
- Provide meaningful loading messages ("Creating task...", "Loading tasks...")
- Timeout after 30 seconds with error message

**States:**
- Initial load: Full-page or section spinner
- Action loading: Button spinner (inline with button text)
- Background refresh: Subtle indicator, doesn't block interaction
- Timeout: Error message "Request is taking longer than expected"

### UI Element 9: Empty States
**Purpose:** Guide user when no content available
**Location:** Task list when user has no tasks
**Behavior:**
- Display friendly empty state message
- Include illustration or icon
- Provide clear call-to-action button "Create your first task"
- Explain what user can do next

**States:**
- First-time user: Welcoming message, onboarding tone
- After deletion: Neutral message "All tasks completed!"
- After filter (future): "No tasks match your filters"

### UI Element 10: Success Feedback
**Purpose:** Confirm successful operations
**Location:** Toast notification, inline message, or animation
**Behavior:**
- Brief success message after create, update, or delete
- Auto-dismiss after 2-3 seconds
- Optional checkmark icon for visual confirmation
- Don't interrupt user workflow

**States:**
- Created: "Task created successfully"
- Updated: "Task updated"
- Deleted: "Task deleted"

### Accessibility Requirements
- All form inputs have associated labels
- Error messages announced to screen readers
- Keyboard navigation supported (Tab, Enter, Escape)
- Focus management in modals and forms
- ARIA attributes for dynamic content updates
- Sufficient color contrast for text and buttons

### Responsive Design
- Mobile: Single column layout, full-width task items
- Tablet: Optional two-column task grid
- Desktop: Sidebar + main content, wider forms
- Touch targets minimum 44x44px on mobile
- Swipe gestures on mobile for task actions (optional enhancement)
