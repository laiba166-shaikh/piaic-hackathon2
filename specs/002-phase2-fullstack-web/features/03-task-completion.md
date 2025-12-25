# Feature: Task Completion Toggle

## Overview

Task Completion Toggle provides users with the ability to mark tasks as complete or incomplete through a simple, intuitive interface. This feature implements a single-field toggle operation that updates the task's completion status via a dedicated PATCH endpoint. Users can quickly manage their task workflow by toggling completion status with a checkbox, seeing visual indicators for completed tasks (strike-through text), and filtering their task list by completion status. All completion operations enforce strict user isolation and follow Phase 2 architectural patterns including user_id filtering from JWT tokens and soft delete exclusions.

## Priority

**Level:** Critical

**Rationale:** Task completion is a fundamental feature required for the Basic Level (5 core features) of the hackathon submission. Without the ability to mark tasks as complete, users cannot track their progress or manage their workflow effectively. This feature directly follows Task CRUD (Feature 02) and is a blocking dependency for task filtering and dashboard analytics in subsequent features. It is part of the minimum viable product for Phase 2.

## Dependencies

**Required Before Implementation:**
- Feature 01: User Authentication - JWT tokens with user_id claims required for all operations
- Feature 02: Task CRUD Operations - Tasks table with completed boolean field must exist
- Backend: FastAPI application with JWT validation middleware
- Frontend: Next.js application with centralized API client

**Optional/Nice-to-Have:**
- None - this is a core Basic Level feature

**External Dependencies:**
- PostgreSQL database with tasks table containing completed field
- Better Auth library for JWT token management
- SQLModel for type-safe database operations

## User Stories

### Story 1: Mark Task as Complete
**As a** logged-in user
**I want** to mark a task as complete with a single click
**So that** I can track which tasks I have finished

### Story 2: Mark Task as Incomplete
**As a** logged-in user
**I want** to unmark a completed task to make it active again
**So that** I can correct mistakes or reopen tasks that need more work

### Story 3: Visual Completion Indicator
**As a** logged-in user
**I want** to see a clear visual difference between complete and incomplete tasks
**So that** I can quickly scan my task list and understand my progress

### Story 4: Filter Tasks by Completion Status
**As a** logged-in user
**I want** to filter my tasks to show only active or only completed tasks
**So that** I can focus on what needs to be done or review what I've accomplished

## Acceptance Criteria

### AC1: Toggle Task to Complete
**Given** I am authenticated and have a task with id=5 and completed=false
**When** I send a PATCH request to /api/v1/tasks/5/toggle
**Then** the task's completed field is updated to true
**And** the updated_at timestamp is refreshed to the current time
**And** the response returns the updated task with completed=true

### AC2: Toggle Task to Incomplete
**Given** I am authenticated and have a task with id=10 and completed=true
**When** I send a PATCH request to /api/v1/tasks/10/toggle
**Then** the task's completed field is updated to false
**And** the updated_at timestamp is refreshed
**And** the response returns the updated task with completed=false

### AC3: Explicit Completion Setting (Optional Body)
**Given** I am authenticated and have a task with id=7
**When** I send a PATCH request to /api/v1/tasks/7/complete with body {"completed": true}
**Then** the task's completed field is set to true (regardless of previous state)
**And** the updated_at timestamp is refreshed
**And** the response returns the updated task

### AC4: Updated Timestamp Refreshes on Toggle
**Given** I have a task with updated_at="2025-12-20T10:00:00Z"
**When** I toggle the task's completion status
**Then** the updated_at field is updated to the current timestamp
**And** the created_at field remains unchanged
**And** all other fields (title, description, etc.) remain unchanged

### AC5: User Isolation on Toggle
**Given** I am authenticated as user "user123"
**And** a task with id=15 exists but belongs to "user456"
**When** I attempt to toggle task 15
**Then** I receive a 404 Not Found error
**And** the error message states "Task not found"
**And** the task's completion status remains unchanged

### AC6: Cannot Toggle Deleted Task
**Given** I have a task with id=20 that has been soft-deleted (deleted_at is set)
**When** I attempt to toggle task 20
**Then** I receive a 404 Not Found error
**And** the error message states "Task not found"
**And** the task's deleted_at timestamp remains unchanged

### AC7: UI Checkbox Updates Completion
**Given** I am viewing my task list
**When** I click the checkbox next to a task with completed=false
**Then** the frontend sends PATCH /api/v1/tasks/{id}/toggle
**And** the checkbox becomes checked
**And** the task title shows strike-through text
**And** the task remains in the list (no removal)

### AC8: UI Checkbox Updates to Incomplete
**Given** I am viewing my task list with a completed task (checkbox checked, strike-through text)
**When** I click the checkbox to uncheck it
**Then** the frontend sends PATCH /api/v1/tasks/{id}/toggle
**And** the checkbox becomes unchecked
**And** the strike-through text is removed
**And** the task appears as active again

### AC9: Filter Tasks by Completion Status
**Given** I have 10 tasks: 6 incomplete and 4 completed
**When** I select the "Active" filter in the UI
**Then** only the 6 incomplete tasks are displayed
**And** completed tasks are hidden from view

### AC10: Filter to Show Completed Tasks
**Given** I have 10 tasks: 6 incomplete and 4 completed
**When** I select the "Completed" filter in the UI
**Then** only the 4 completed tasks are displayed
**And** incomplete tasks are hidden from view

### AC11: Show All Tasks Regardless of Status
**Given** I have tasks in both complete and incomplete states
**When** I select the "All" filter in the UI
**Then** all tasks are displayed
**And** completed tasks show strike-through text
**And** incomplete tasks show normal text

### AC12: Optimistic UI Update with Rollback
**Given** I am viewing my task list
**When** I click a task checkbox to toggle completion
**Then** the UI immediately updates (checkbox state and strike-through)
**And** the PATCH request is sent to the backend
**And** if the request fails, the UI reverts to the previous state
**And** an error message is displayed

## Edge Cases

### Edge Case 1: Rapid Consecutive Toggles
**Scenario:** User clicks the checkbox multiple times quickly (double-click or rapid clicking)
**Expected Behavior:** Each request is processed in order, final state reflects the last successful toggle
**Validation:** If user clicks 5 times rapidly, task ends in opposite state (odd number of toggles)

### Edge Case 2: Concurrent Toggles from Multiple Devices
**Scenario:** User toggles the same task from two browser tabs simultaneously
**Expected Behavior:** Last write wins, both requests succeed, final state shows last toggle
**Validation:** Both requests return 200 OK, final database state reflects last timestamp

### Edge Case 3: Toggle Non-Existent Task
**Scenario:** User attempts to toggle task with id=99999 that doesn't exist
**Expected Behavior:** 404 Not Found error "Task not found"
**Validation:** Request rejected, no database changes, clear error message

### Edge Case 4: Toggle Task ID Zero or Negative
**Scenario:** User sends PATCH /api/v1/tasks/0/toggle or /api/v1/tasks/-5/toggle
**Expected Behavior:** 404 Not Found (invalid IDs treated as not found)
**Validation:** Request rejected, error response returned

### Edge Case 5: Invalid Task ID Format
**Scenario:** User sends PATCH /api/v1/tasks/abc/toggle (non-numeric ID)
**Expected Behavior:** 422 Unprocessable Entity error "Invalid task ID format"
**Validation:** Request rejected before database query, validation error returned

### Edge Case 6: Missing JWT Token
**Scenario:** User sends toggle request without Authorization header
**Expected Behavior:** 401 Unauthorized error "Authorization required"
**Validation:** Request rejected at authentication middleware, no database access

### Edge Case 7: Expired JWT Token
**Scenario:** User's JWT token has expired (exp claim in past)
**Expected Behavior:** 401 Unauthorized error "Token has expired"
**Validation:** Token validation fails, user redirected to login page

### Edge Case 8: Explicit Body with Invalid Boolean
**Scenario:** User sends PATCH with body {"completed": "yes"} (string instead of boolean)
**Expected Behavior:** 422 Unprocessable Entity validation error
**Validation:** Pydantic validation rejects non-boolean value

### Edge Case 9: Explicit Body with Null Completed
**Scenario:** User sends PATCH with body {"completed": null}
**Expected Behavior:** 400 Bad Request "Completed field cannot be null"
**Validation:** Validation rejects null value, task unchanged

### Edge Case 10: Network Timeout During Toggle
**Scenario:** Network request times out while toggling task
**Expected Behavior:** Frontend shows error "Request timed out. Please try again.", UI reverts to previous state
**Validation:** Optimistic update rolled back, user can retry

### Edge Case 11: Database Constraint Violation
**Scenario:** Unexpected database error during toggle (e.g., connection lost)
**Expected Behavior:** 500 Internal Server Error "An error occurred. Please try again."
**Validation:** Error logged for ops team, user sees generic error message

### Edge Case 12: Toggle Filter Edge Case - All Tasks Completed
**Scenario:** User completes all tasks and has "Active" filter selected
**Expected Behavior:** Empty state shown "No active tasks. Great job!" with option to view completed
**Validation:** List becomes empty, empty state message displayed

## Error Handling

### Error 1: Task Not Found
**Scenario:** User attempts to toggle task that doesn't exist, is deleted, or belongs to another user
**HTTP Status:** 404 Not Found
**Error Response:**
```json
{
  "detail": "Task not found"
}
```
**User-Facing Message:** "This task no longer exists or has been deleted."
**Recovery:** User refreshes task list, task is removed from view

### Error 2: Unauthenticated Request
**Scenario:** Request missing Authorization header or invalid JWT token
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid or expired token"
}
```
**User-Facing Message:** "Your session has expired. Please log in again."
**Recovery:** User is redirected to login page, re-authenticates, and retries

### Error 3: Invalid Task ID Format
**Scenario:** User provides non-numeric task ID in URL path
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

### Error 4: Invalid Completed Value (Explicit Body)
**Scenario:** User sends body with completed as non-boolean (e.g., string, number, null)
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
**User-Facing Message:** "Invalid completion status. Please try again."
**Recovery:** Frontend validation prevents this, user retries

### Error 5: Database Connection Failure
**Scenario:** Database is unavailable or connection pool exhausted during toggle
**HTTP Status:** 500 Internal Server Error
**Error Response:**
```json
{
  "detail": "An error occurred while processing your request"
}
```
**User-Facing Message:** "Something went wrong. Please try again in a moment."
**Recovery:** User retries after a few seconds, error logged for ops team

### Error 6: Network Timeout
**Scenario:** Request takes longer than configured timeout (e.g., 30 seconds)
**HTTP Status:** 504 Gateway Timeout
**Error Response:**
```json
{
  "detail": "Request timeout"
}
```
**User-Facing Message:** "Request timed out. Please check your connection and try again."
**Recovery:** User retries operation, check network connection

### Error 7: Missing user_id in JWT
**Scenario:** JWT token is valid but missing user_id claim (configuration error)
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid token: missing user_id claim"
}
```
**User-Facing Message:** "Authentication error. Please log in again."
**Recovery:** User logs out and logs back in to get fresh token

### Error 8: Concurrent Toggle Conflict (Rare)
**Scenario:** Two rapid toggles create race condition (extremely unlikely)
**HTTP Status:** 200 OK (succeeds but may show unexpected state)
**Error Response:** N/A (success)
**User-Facing Message:** None (last write wins)
**Recovery:** User can toggle again if state is unexpected

## Non-Goals

This feature specifically does NOT include:

- **Bulk Completion Operations:** Marking multiple tasks as complete in a single request is deferred to Phase 3. Each task must be toggled individually.
  (Reason: Adds complexity with transaction management and partial failure handling)

- **Completion History/Audit Log:** Tracking when tasks were completed, by whom, or how many times toggled is deferred to Phase 5 audit system. Only current completed status and updated_at timestamp are stored.
  (Reason: Requires audit table, event logging, and historical data management)

- **Undo Completion:** Dedicated undo mechanism or completion history rollback is deferred to Phase 4.
  (Reason: Current toggle behavior already supports unmarking as complete; dedicated undo adds complexity)

- **Completion Percentage/Progress Tracking:** Calculating percentage of completed tasks or displaying progress bars is deferred to Phase 3.
  (Reason: Belongs to dashboard analytics feature, not basic completion toggle)

- **Completion Notifications:** Email or push notifications when tasks are completed is deferred to Phase 4+.
  (Reason: Requires notification service integration and user preference management)

- **Completion Date Tracking:** Storing a dedicated completed_at timestamp separate from updated_at is deferred to Phase 3+.
  (Reason: Adds database field and migration; updated_at serves as proxy for now)

- **Recurring Task Completion:** Automatic creation of next instance when recurring task is completed is handled by separate recurring task feature (Phase 3+).
  (Reason: Recurrence logic is a separate feature with its own complexity)

- **Subtask Completion Logic:** Automatic parent task completion when all subtasks are complete is deferred to Phase 4+ (subtasks feature).
  (Reason: Subtasks are not part of Phase 2; no hierarchical task structure exists)

- **Completion Confirmation Dialog:** No confirmation prompt when marking task complete (unlike delete which has confirmation).
  (Reason: Completion is easily reversible via toggle; confirmation adds friction)

- **Completion Sound/Animation:** Audio feedback or elaborate animations on completion are deferred to Phase 3+ UX enhancements.
  (Reason: Keep UI simple in Phase 2; focus on functionality over polish)

- **Completion Rewards/Gamification:** Points, badges, streaks, or other gamification elements are deferred to Phase 5+.
  (Reason: Out of scope for basic task management; requires separate gamification system)

## API Contract

### Endpoint: PATCH /api/v1/tasks/{id}/toggle

**Description:** Toggle task completion status (complete ↔ incomplete)

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)
  - Content-Type: application/json (Optional - no body needed for toggle)

- **Path Parameters:**
  - `id`: integer (required) - Task ID to toggle

- **Request Body (Optional):**
  ```json
  {}
  ```
  - No body needed for toggle operation (simple state flip)
  - Backend automatically toggles completed: true ↔ false

**Alternative: Explicit Completion Setting**

If you want to support explicit setting instead of toggle:

**Endpoint:** PATCH /api/v1/tasks/{id}/complete

**Request Body (Optional):**
```json
{
  "completed": "boolean (optional - true or false)"
}
```
- If body provided, sets completed to specified value
- If body empty, toggles current state

**Response:**
- **Success (200 OK):**
  ```json
  {
    "id": "integer",
    "user_id": "string",
    "title": "string",
    "description": "string | null",
    "completed": "boolean (toggled value)",
    "priority": "string | null",
    "tags": "array of strings",
    "due_date": "string (ISO 8601) | null",
    "recurrence": "string | null",
    "deleted_at": "string (ISO 8601) | null",
    "created_at": "string (ISO 8601, unchanged)",
    "updated_at": "string (ISO 8601, refreshed to current time)"
  }
  ```

- **Errors:**
  - 401 Unauthorized: Missing or invalid JWT token
  - 404 Not Found: Task doesn't exist, is deleted, or belongs to another user
  - 422 Unprocessable Entity: Invalid task ID format or invalid completed value
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

### Task (No New Fields)

**The completed field already exists in the tasks table from Feature 02 (Task CRUD).**

**Field Details:**
- `completed`: boolean (required, not null, default: false) - Task completion status
  - **Type:** Boolean
  - **Default:** false (tasks start as incomplete)
  - **Nullable:** No (must be true or false)
  - **Indexed:** Yes (add index for filtering by completion status)

**Database Schema (Existing):**
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE NOT NULL,  -- Used by this feature
  priority VARCHAR(20),
  tags JSONB DEFAULT '[]' NOT NULL,
  due_date TIMESTAMP WITH TIME ZONE,
  recurrence VARCHAR(20),
  deleted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Existing indexes (from Feature 02)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_tasks_user_deleted ON tasks(user_id, deleted_at);

-- NEW INDEX for completion filtering
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- OPTIONAL: Composite index for user + completed queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed) WHERE deleted_at IS NULL;
```

**Migration Notes:**
- **No new columns needed** - completed field exists from Feature 02
- **Add index on completed field** for efficient filtering by completion status
- **Optional composite index** on (user_id, completed) for performance optimization
- **No data migration needed** - all existing tasks default to completed=false

### Validation Rules

**Completed Field:**
- Must be boolean (true or false)
- Cannot be null
- Defaults to false on task creation
- Updated via PATCH /api/v1/tasks/{id}/toggle endpoint
- Updates updated_at timestamp when changed
- Never directly set by user in POST or PUT operations (only via PATCH toggle)

**Database Constraints:**
- `completed` NOT NULL
- `completed` DEFAULT FALSE
- All queries MUST filter by `user_id` and `deleted_at IS NULL` (Phase 2 required pattern)

## UI/UX Requirements

### UI Element 1: Task Completion Checkbox
**Purpose:** Allow user to toggle task completion status with a single click
**Location:** Next to task title in task list view, before the title text
**Behavior:**
- Display unchecked checkbox for incomplete tasks (completed=false)
- Display checked checkbox for completed tasks (completed=true)
- On click, send PATCH /api/v1/tasks/{id}/toggle request
- Optimistically update checkbox state and apply strike-through before request completes
- If request fails, revert checkbox state and remove strike-through, show error
- Checkbox accessible via keyboard (Tab to focus, Space/Enter to toggle)

**States:**
- **Unchecked (incomplete):** Empty checkbox, normal task title
- **Checked (completed):** Checked checkbox, strike-through title
- **Loading:** Checkbox disabled, subtle spinner or opacity change during request
- **Error:** Revert to previous state, show inline error message

### UI Element 2: Strike-Through Text for Completed Tasks
**Purpose:** Provide visual indicator that task is complete
**Location:** Task title text in task list
**Behavior:**
- Apply text-decoration: line-through when completed=true
- Remove strike-through when completed=false
- Optionally reduce opacity (e.g., text-gray-500) for completed tasks
- Strike-through updates immediately on checkbox click (optimistic UI)

**States:**
- **Active task:** Normal text, full opacity, no strike-through
- **Completed task:** Strike-through text, reduced opacity (gray)

### UI Element 3: Completion Filter Dropdown
**Purpose:** Allow user to filter tasks by completion status
**Location:** Above task list, in toolbar or filter bar
**Behavior:**
- Dropdown or toggle buttons with three options: "All", "Active", "Completed"
- Default selection: "All" (show all tasks)
- On selection change, filter task list client-side (no API call)
- Persist filter selection in component state (not localStorage in Phase 2)
- Show task count for each filter option (e.g., "Active (6)", "Completed (4)")

**Options:**
- **All:** Show all tasks regardless of completion status
- **Active:** Show only tasks with completed=false
- **Completed:** Show only tasks with completed=true

**States:**
- **All selected:** All tasks visible, default state
- **Active selected:** Only incomplete tasks visible, completed tasks hidden
- **Completed selected:** Only completed tasks visible, incomplete tasks hidden

### UI Element 4: Completion Count Display
**Purpose:** Show user how many tasks are completed vs total
**Location:** Task list header or filter bar
**Behavior:**
- Display count as "X of Y completed" or "X / Y tasks"
- Update count automatically when task completion status changes
- Calculate from current task list in component state
- Example: "4 of 10 completed" or "6 active tasks"

**States:**
- **With tasks:** Show count (e.g., "4 of 10 completed")
- **All completed:** Show "All tasks completed!" message
- **No tasks:** Hide count or show "No tasks yet"

### UI Element 5: Visual Feedback on Toggle
**Purpose:** Provide immediate confirmation that toggle action was registered
**Location:** Task item in list
**Behavior:**
- Checkbox state changes immediately (optimistic update)
- Strike-through applies/removes immediately
- Subtle animation or transition (e.g., 200ms ease-in-out for strike-through)
- If request succeeds, state persists
- If request fails, revert with error message

**States:**
- **Toggling:** Checkbox updates, strike-through animates in/out
- **Success:** State persists, no additional feedback needed
- **Error:** State reverts, error message displayed inline

### UI Element 6: Loading State During Toggle
**Purpose:** Indicate that toggle request is in progress
**Location:** Task item checkbox or task row
**Behavior:**
- Disable checkbox during request to prevent double-clicks
- Optionally show subtle spinner next to checkbox
- Reduce opacity of task row slightly (e.g., opacity-70)
- Duration typically < 500ms for fast backend response
- Re-enable checkbox after request completes (success or error)

**States:**
- **Idle:** Checkbox enabled, normal opacity
- **Loading:** Checkbox disabled, subtle spinner, reduced opacity
- **Complete:** Return to idle state

### UI Element 7: Optimistic UI Update
**Purpose:** Make UI feel responsive by updating before server confirmation
**Location:** Task list component
**Behavior:**
- Immediately update checkbox and strike-through on click
- Send PATCH request to backend
- If request succeeds, no additional action needed
- If request fails, revert checkbox and strike-through, show error
- Error displayed as inline message below task or toast notification

**States:**
- **Optimistic Update:** UI updated, request pending
- **Confirmed:** Request succeeded, optimistic state is correct
- **Rollback:** Request failed, revert to previous state, show error

### UI Element 8: Error Rollback on Toggle Failure
**Purpose:** Revert UI to previous state if toggle request fails
**Location:** Task item in list
**Behavior:**
- If PATCH request fails (network error, 401, 404, 500)
- Revert checkbox to previous state
- Revert strike-through to previous state
- Display error message: "Failed to update task. Please try again."
- Allow user to retry toggle immediately

**States:**
- **Error Occurred:** UI reverted, error message visible
- **Retry:** User clicks checkbox again to retry
- **Dismissed:** Error message auto-dismisses after 5 seconds or user dismisses manually

### UI Element 9: Empty State for Filtered Views
**Purpose:** Show helpful message when filter results in empty list
**Location:** Task list area
**Behavior:**
- When "Active" filter selected and all tasks are completed: "No active tasks. Great job!"
- When "Completed" filter selected and no tasks completed: "No completed tasks yet. Start checking off items!"
- Include option to change filter or view all tasks
- Provide link or button to switch to "All" filter

**States:**
- **Active filter, no results:** "No active tasks" message with "View all tasks" link
- **Completed filter, no results:** "No completed tasks" message with "View all tasks" link

### UI Element 10: Accessibility Features
**Purpose:** Ensure completion toggle is accessible to all users
**Location:** Throughout task completion UI
**Behavior:**
- Checkbox has accessible label (aria-label or associated label element)
- Checkbox focusable via keyboard (Tab navigation)
- Checkbox toggleable via keyboard (Space or Enter key)
- Screen reader announces state: "Mark task complete" or "Mark task incomplete"
- Error messages announced to screen readers (aria-live region)
- Focus management after toggle (focus remains on checkbox)
- Sufficient color contrast for strike-through text

**ARIA Attributes:**
- `aria-label` on checkbox: "Mark task as complete" or "Mark task as incomplete"
- `aria-checked="true"` or `aria-checked="false"` on checkbox
- `role="checkbox"` if using custom checkbox (not native input)
- `aria-live="polite"` on error message container
- `aria-describedby` linking checkbox to task title

**Keyboard Navigation:**
- Tab: Move focus to checkbox
- Space/Enter: Toggle checkbox state
- Tab: Move to next interactive element
- Shift+Tab: Move to previous interactive element

### Responsive Design
- Mobile (< 768px): Larger checkbox touch target (minimum 44x44px)
- Tablet (768px - 1024px): Standard checkbox size
- Desktop (> 1024px): Standard checkbox size with hover effects
- All screen sizes: Clear strike-through visible, adequate spacing between tasks

### Accessibility Notes
- Use semantic HTML (`<input type="checkbox">`) for native accessibility
- Ensure checkbox and label are properly associated
- Provide visible focus indicators for keyboard navigation
- Announce completion state changes to screen readers
- Ensure adequate color contrast for strike-through text and checkbox
- Support both mouse/touch and keyboard interactions
