---
name: spec-architect
description: Write and structure feature specifications with enforced completeness, clarity, and required sections. Use when (1) creating new feature specifications, (2) documenting design decisions, (3) defining API contracts, or (4) validating existing specs for completeness. Does NOT make implementation decisions or generate code.
license: Complete terms in LICENSE.txt
---

# Spec Architect

Design and write complete, clear, and well-structured feature specifications that serve as the authoritative source of truth for implementation.

## Workflow

Follow these steps when writing specifications:

1. **Gather requirements**
   - Understand user needs and business goals
   - Identify stakeholders
   - Define success criteria
   - Note constraints and dependencies

2. **Structure the specification**
   - Use required sections template
   - Ensure all mandatory sections present
   - Organize information logically
   - Maintain clarity without implementation details

3. **Define user stories and acceptance criteria**
   - Write user stories in standard format
   - Define testable acceptance criteria
   - Use Given-When-Then format
   - Cover all user flows

4. **Document edge cases and error handling**
   - Identify boundary conditions
   - Define error scenarios
   - Specify error messages
   - Note validation rules

5. **Validate completeness**
   - Check all required sections present
   - Verify clarity and unambiguity
   - Ensure testability
   - Confirm no implementation decisions

## Output Format

Present specification using this structure:

```
📋 Specification: [Feature Name]

Location: specs/phase2/features/[feature-name].md

Status: ✅ Complete
Required Sections: 12/12 present

Validation:
✅ Name and description clear
✅ Priority and dependencies defined
✅ User stories complete (As-Want-So format)
✅ Acceptance criteria testable (Given-When-Then)
✅ Edge cases identified
✅ Error handling specified
✅ Non-goals explicitly stated
✅ No implementation details included
```

## Required Specification Structure

Every feature specification MUST include these sections:

### 1. Feature Name (Required)

**Purpose:** Clear, concise identifier for the feature

**Format:**
```markdown
# Feature: [Clear Feature Name]
```

**Requirements:**
- ✅ Clear and descriptive (5-10 words)
- ✅ Action-oriented (verb + noun)
- ✅ No implementation details
- ❌ Not vague or ambiguous

**Examples:**
```markdown
✅ GOOD:
# Feature: Task Priority Management
# Feature: Multi-User Task Filtering
# Feature: Tag-Based Task Organization

❌ BAD:
# Feature: Tasks (too vague)
# Feature: Implement FastAPI Route for Task CRUD (implementation detail)
# Feature: The Feature (not descriptive)
```

### 2. Overview (Required)

**Purpose:** Brief description of what the feature does and why it exists

**Format:**
```markdown
## Overview

Brief 2-3 sentence description of the feature, its purpose, and the problem it solves.
```

**Requirements:**
- ✅ What the feature does
- ✅ Why it's needed (business value)
- ✅ Who benefits (target users)
- ❌ No technical implementation details

**Example:**
```markdown
## Overview

Task priority management allows users to assign importance levels (1-5) to their tasks,
helping them organize work by urgency. This feature addresses the common user need to
focus on high-priority items first and improves task workflow efficiency.
```

### 3. Priority (Required)

**Purpose:** Indicate feature importance and implementation order

**Format:**
```markdown
## Priority

**Level:** [Critical | High | Medium | Low]

**Rationale:** Brief explanation of why this priority level
```

**Requirements:**
- ✅ One of: Critical, High, Medium, Low
- ✅ Rationale explaining priority
- ✅ Consider: User impact, business value, dependencies

**Example:**
```markdown
## Priority

**Level:** High

**Rationale:** Task priority is a core feature requested by 80% of users in surveys.
Without it, users cannot effectively organize their workload. Blocks advanced features
like smart task suggestions and deadline management.
```

### 4. Dependencies (Required - Explicit if None)

**Purpose:** Identify features or systems this depends on

**Format:**
```markdown
## Dependencies

**Required Before Implementation:**
- [Feature/System Name]: Brief description of dependency
- [Another Dependency]: Why it's needed

**Optional/Nice-to-Have:**
- [Feature Name]: Enhancement if available

**None:** Explicitly state if no dependencies
```

**Requirements:**
- ✅ List all blocking dependencies
- ✅ Distinguish required vs optional
- ✅ State "None" explicitly if independent
- ✅ Include both technical and feature dependencies

**Example:**
```markdown
## Dependencies

**Required Before Implementation:**
- User Authentication: Need user_id from JWT for task ownership
- Task CRUD Operations: Must have basic task creation before adding priority

**Optional/Nice-to-Have:**
- Task Filtering: Priority filtering would enhance task filtering feature

**External Dependencies:**
- PostgreSQL with JSONB support (for tags)
```

### 5. User Stories (Required)

**Purpose:** Define who wants what and why from user perspective

**Format:**
```markdown
## User Stories

### Story 1: [Brief Title]
**As a** [user type]
**I want** [goal/desire]
**So that** [benefit/value]

### Story 2: [Brief Title]
**As a** [user type]
**I want** [goal/desire]
**So that** [benefit/value]
```

**Requirements:**
- ✅ Use "As-Want-So" format consistently
- ✅ Focus on user goals, not implementation
- ✅ Each story is independent and testable
- ✅ Cover all major user flows
- ❌ No technical jargon in user stories

**Example:**
```markdown
## User Stories

### Story 1: Set Task Priority
**As a** task manager user
**I want** to assign a priority level (1-5) to my tasks
**So that** I can organize my work by importance and focus on critical items first

### Story 2: View Tasks by Priority
**As a** task manager user
**I want** to see my tasks sorted by priority
**So that** I can quickly identify which tasks need immediate attention

### Story 3: Update Task Priority
**As a** task manager user
**I want** to change a task's priority as circumstances evolve
**So that** my task list reflects current urgency levels
```

### 6. Acceptance Criteria (Required)

**Purpose:** Define testable conditions for feature completion

**Format:**
```markdown
## Acceptance Criteria

### AC1: [Brief Criterion Title]
**Given** [initial context/state]
**When** [action/event occurs]
**Then** [expected outcome]

**And:** [additional conditions if needed]

### AC2: [Another Criterion]
**Given** [context]
**When** [action]
**Then** [outcome]
```

**Requirements:**
- ✅ Use Given-When-Then format
- ✅ Each criterion is testable
- ✅ Cover all user stories
- ✅ Include success AND failure cases
- ✅ Specific, measurable outcomes
- ❌ No vague acceptance criteria

**Example:**
```markdown
## Acceptance Criteria

### AC1: Create Task with Priority
**Given** I am authenticated and on the task creation form
**When** I enter a task title "Review PR" and select priority level 3
**Then** the task is created with priority 3 stored in the database
**And** the task appears in my task list showing priority level 3

### AC2: Priority Validation
**Given** I am creating a new task
**When** I attempt to set priority to 0 or 6 (out of range 1-5)
**Then** I receive a validation error "Priority must be between 1 and 5"
**And** the task is not created until a valid priority is provided

### AC3: Default Priority
**Given** I am creating a new task
**When** I submit the form without specifying a priority
**Then** the task is created with no priority set (null/None)
**And** it appears in the "No Priority" section of my task list

### AC4: Update Task Priority
**Given** I have an existing task with priority 2
**When** I edit the task and change priority to 5
**Then** the task priority is updated to 5
**And** the task moves to the appropriate priority section in the list

### AC5: User Isolation
**Given** I am authenticated as User A
**When** I view my tasks filtered by priority
**Then** I only see tasks I created, not tasks from User B
**And** all displayed tasks respect the priority filter
```

### 7. Edge Cases (Required)

**Purpose:** Identify boundary conditions and unusual scenarios

**Format:**
```markdown
## Edge Cases

### Edge Case 1: [Scenario Name]
**Scenario:** Description of edge case
**Expected Behavior:** How system should handle it
**Validation:** How to verify correct handling

### Edge Case 2: [Another Scenario]
**Scenario:** [...]
**Expected Behavior:** [...]
**Validation:** [...]
```

**Requirements:**
- ✅ Identify boundary values (min, max, zero, empty)
- ✅ Consider special characters and formats
- ✅ Handle null/undefined/missing values
- ✅ Address concurrent operations if applicable
- ✅ Define expected behavior for each

**Example:**
```markdown
## Edge Cases

### Edge Case 1: Empty Priority
**Scenario:** User creates task without setting priority
**Expected Behavior:** Task created with priority = null, appears in "No Priority" section
**Validation:** GET /api/v1/tasks returns task with priority: null

### Edge Case 2: Minimum Priority (Boundary)
**Scenario:** User sets priority to 1 (minimum valid value)
**Expected Behavior:** Task created with priority = 1, no validation error
**Validation:** Task saved with priority 1, appears in "Low Priority" section

### Edge Case 3: Maximum Priority (Boundary)
**Scenario:** User sets priority to 5 (maximum valid value)
**Expected Behavior:** Task created with priority = 5, no validation error
**Validation:** Task saved with priority 5, appears in "Critical Priority" section

### Edge Case 4: Below Minimum (Invalid)
**Scenario:** API receives priority = 0 or negative number
**Expected Behavior:** Validation error 400 "Priority must be between 1 and 5"
**Validation:** Task NOT created, error response returned

### Edge Case 5: Above Maximum (Invalid)
**Scenario:** API receives priority > 5
**Expected Behavior:** Validation error 400 "Priority must be between 1 and 5"
**Validation:** Task NOT created, error response returned

### Edge Case 6: Invalid Type
**Scenario:** API receives priority = "high" (string instead of number)
**Expected Behavior:** Validation error 422 "Priority must be a number"
**Validation:** Pydantic validation rejects non-numeric priority

### Edge Case 7: Null vs Undefined
**Scenario:** Frontend sends priority: null vs omits priority field
**Expected Behavior:** Both treated as "no priority set"
**Validation:** Backend accepts both, stores as null in database

### Edge Case 8: Concurrent Priority Updates
**Scenario:** Two users (or tabs) update same task priority simultaneously
**Expected Behavior:** Last write wins, updated_at timestamp reflects latest change
**Validation:** Database shows most recent priority, both requests succeed (no conflict)

### Edge Case 9: Changing from Set to Unset
**Scenario:** User removes priority from task that had priority = 3
**Expected Behavior:** Priority set to null, task moves to "No Priority" section
**Validation:** Update request with priority: null succeeds

### Edge Case 10: Soft-Deleted Task Priority
**Scenario:** Task with priority is soft-deleted
**Expected Behavior:** Priority remains in database but task not shown in lists
**Validation:** GET /api/v1/tasks excludes task, but database record has both priority and deleted_at
```

### 8. Error Handling (Required)

**Purpose:** Define all error scenarios and responses

**Format:**
```markdown
## Error Handling

### Error 1: [Error Type]
**Scenario:** When/how error occurs
**HTTP Status:** [400/401/403/404/422/500]
**Error Response:**
\`\`\`json
{
  "detail": "Specific error message"
}
\`\`\`
**User-Facing Message:** Friendly message shown to user
**Recovery:** How user can resolve the error

### Error 2: [Another Error Type]
[...]
```

**Requirements:**
- ✅ Cover all failure scenarios
- ✅ Define HTTP status codes
- ✅ Specify error response format
- ✅ Provide user-friendly messages
- ✅ Include recovery steps

**Example:**
```markdown
## Error Handling

### Error 1: Invalid Priority Range
**Scenario:** User provides priority < 1 or > 5
**HTTP Status:** 400 Bad Request
**Error Response:**
\`\`\`json
{
  "detail": "Priority must be between 1 and 5"
}
\`\`\`
**User-Facing Message:** "Please select a priority between 1 (Low) and 5 (Critical)"
**Recovery:** User selects valid priority from dropdown/slider

### Error 2: Invalid Priority Type
**Scenario:** API receives non-numeric priority value
**HTTP Status:** 422 Unprocessable Entity
**Error Response:**
\`\`\`json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
\`\`\`
**User-Facing Message:** "Priority must be a number between 1 and 5"
**Recovery:** Frontend validation prevents this, but backend rejects gracefully

### Error 3: Unauthenticated Request
**Scenario:** User attempts to create/update task without valid JWT
**HTTP Status:** 401 Unauthorized
**Error Response:**
\`\`\`json
{
  "detail": "Invalid or expired token"
}
\`\`\`
**User-Facing Message:** "Your session has expired. Please log in again."
**Recovery:** Redirect to login page, user re-authenticates

### Error 4: Task Not Found
**Scenario:** User attempts to update priority for non-existent or deleted task
**HTTP Status:** 404 Not Found
**Error Response:**
\`\`\`json
{
  "detail": "Task not found"
}
\`\`\`
**User-Facing Message:** "This task no longer exists or has been deleted."
**Recovery:** Refresh task list, task removed from UI

### Error 5: Accessing Other User's Task
**Scenario:** User A attempts to modify task owned by User B
**HTTP Status:** 404 Not Found (user isolation - acts like task doesn't exist)
**Error Response:**
\`\`\`json
{
  "detail": "Task not found"
}
\`\`\`
**User-Facing Message:** "This task no longer exists or has been deleted."
**Recovery:** None - correct behavior, user should not see other users' tasks

### Error 6: Database Connection Error
**Scenario:** Database is unavailable or connection fails
**HTTP Status:** 500 Internal Server Error
**Error Response:**
\`\`\`json
{
  "detail": "An error occurred while processing your request"
}
\`\`\`
**User-Facing Message:** "Something went wrong. Please try again in a moment."
**Recovery:** User retries, error logged for ops team investigation
```

### 9. Non-Goals (Required)

**Purpose:** Explicitly state what this feature does NOT include

**Format:**
```markdown
## Non-Goals

This feature specifically does NOT include:

- [Feature/behavior explicitly out of scope]
- [Another excluded item]
- [Why it's excluded or deferred]
```

**Requirements:**
- ✅ Explicitly list excluded features
- ✅ Explain why excluded (out of scope, future phase, etc.)
- ✅ Prevent scope creep
- ✅ Set clear expectations

**Example:**
```markdown
## Non-Goals

This feature specifically does NOT include:

- **Priority-based automatic sorting:** While users can assign priorities, automatic
  re-ordering of the task list is not included. Users manually control sort order.
  (Deferred to Phase 3: Smart Task Management)

- **Priority suggestions:** The system will not recommend priority levels based on
  due dates or other factors. Users must manually assign priorities.
  (Future enhancement if user research shows demand)

- **Sub-task priority inheritance:** If a task has sub-tasks (future feature), they
  do not automatically inherit parent priority. Each task has independent priority.
  (Complexity not justified for initial release)

- **Priority-based notifications:** Email/push notifications will not be triggered
  based on priority levels. Notification logic is separate.
  (Different feature: Notification Management)

- **Historical priority tracking:** System does not track priority changes over time
  or show priority change history.
  (Not requested by users, adds storage complexity)

- **Team-wide priority consensus:** In shared workspaces (future feature), priority
  is per-user, not agreed upon by team.
  (Collaborative features are Phase 4)
```

### 10. API Contract (Required for Backend Features)

**Purpose:** Define precise API specification

**Format:**
```markdown
## API Contract

### Endpoint: [HTTP METHOD] [Path]

**Description:** Brief description of what endpoint does

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT}
  - Content-Type: application/json

- **Path Parameters:** (if any)
  - `id`: [type] - Description

- **Query Parameters:** (if any)
  - `filter`: [type] - Description

- **Request Body:** (for POST/PUT)
  \`\`\`json
  {
    "field": "type (description)"
  }
  \`\`\`

**Response:**
- **Success (2xx):**
  - Status: 201 Created
  - Body:
    \`\`\`json
    {
      "field": "type (description)"
    }
    \`\`\`

- **Errors:**
  - 400: Invalid input
  - 401: Unauthorized
  - 404: Not found
```

**Requirements:**
- ✅ Complete endpoint specification
- ✅ All request/response fields documented
- ✅ Field types and constraints specified
- ✅ All status codes listed
- ✅ Authentication requirements clear

**Example:**
```markdown
## API Contract

### Endpoint: POST /api/v1/tasks

**Description:** Create a new task with optional priority for authenticated user

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)
  - Content-Type: application/json

- **Request Body:**
  \`\`\`json
  {
    "title": "string (required, 1-200 chars)",
    "description": "string (optional)",
    "priority": "integer (optional, 1-5, null for no priority)",
    "tags": "string[] (optional, array of strings)"
  }
  \`\`\`

**Response:**
- **Success (201 Created):**
  \`\`\`json
  {
    "id": "integer (unique task ID)",
    "title": "string",
    "description": "string | null",
    "priority": "integer (1-5) | null",
    "tags": "string[]",
    "created_at": "string (ISO 8601 timestamp)",
    "updated_at": "string (ISO 8601 timestamp)"
  }
  \`\`\`

- **Errors:**
  - 400 Bad Request: Missing title or priority out of range
  - 401 Unauthorized: Missing or invalid JWT token
  - 422 Unprocessable Entity: Invalid data types

---

### Endpoint: PUT /api/v1/tasks/{id}

**Description:** Update an existing task including its priority

**Request:**
- **Headers:**
  - Authorization: Bearer {JWT} (Required)
  - Content-Type: application/json

- **Path Parameters:**
  - `id`: integer - Task ID to update

- **Request Body:**
  \`\`\`json
  {
    "title": "string (optional, 1-200 chars)",
    "description": "string (optional)",
    "priority": "integer (optional, 1-5, or null to remove priority)",
    "tags": "string[] (optional)"
  }
  \`\`\`

**Response:**
- **Success (200 OK):**
  \`\`\`json
  {
    "id": "integer",
    "title": "string",
    "description": "string | null",
    "priority": "integer (1-5) | null",
    "tags": "string[]",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  }
  \`\`\`

- **Errors:**
  - 400 Bad Request: Invalid priority range
  - 401 Unauthorized: Missing or invalid JWT
  - 404 Not Found: Task doesn't exist or belongs to another user
```

### 11. Data Model (Required for Data Features)

**Purpose:** Define data structure and constraints

**Format:**
```markdown
## Data Model

### [Entity Name]

**Fields:**
- `field_name`: type (constraints) - Description
- `another_field`: type (constraints) - Description

**Indexes:**
- Index on field_name (reason)

**Constraints:**
- Unique constraint on (field1, field2)
- Foreign key to other_table

**Validation Rules:**
- Field must be [constraint]
```

**Requirements:**
- ✅ All fields with types documented
- ✅ Constraints and validation rules clear
- ✅ Indexes for performance noted
- ✅ Relationships to other entities
- ❌ No database implementation details (which DB, table names)

**Example:**
```markdown
## Data Model

### Task

**Fields:**
- `id`: integer (auto-increment, primary key) - Unique task identifier
- `user_id`: string (required, indexed) - Owner's user ID from JWT
- `title`: string (required, 1-200 chars) - Task title
- `description`: string (optional, nullable) - Detailed task description
- `priority`: integer (optional, nullable, range 1-5) - Priority level
- `tags`: array of strings (JSONB, default empty array) - Task tags
- `deleted_at`: timestamp (nullable) - Soft delete timestamp
- `created_at`: timestamp (auto, not null) - Creation timestamp
- `updated_at`: timestamp (auto-update, not null) - Last modification timestamp

**Indexes:**
- `idx_tasks_user_id` on user_id (frequent queries by user)
- `idx_tasks_deleted_at` on deleted_at WHERE deleted_at IS NULL (soft delete filter)
- `idx_tasks_priority` on priority (optional, if priority filtering is common)

**Constraints:**
- user_id cannot be null (every task has an owner)
- priority must be between 1 and 5 if set, or null
- title minimum length 1 character

**Validation Rules:**
- Title: Required, 1-200 characters
- Priority: If provided, must be integer 1-5
- Tags: Array of strings, each tag max 50 characters
- User isolation: All queries filter by user_id
```

### 12. UI/UX Requirements (Required for Frontend Features)

**Purpose:** Define user interface expectations without dictating implementation

**Format:**
```markdown
## UI/UX Requirements

### UI Element 1: [Component Name]
**Purpose:** What user sees/does
**Location:** Where it appears
**Behavior:** How it works
**States:** Different UI states (loading, error, empty, etc.)

### UI Element 2: [Another Component]
[...]
```

**Requirements:**
- ✅ Define WHAT user sees/does
- ✅ Specify user interactions
- ✅ Describe different UI states
- ❌ NO specific framework/library decisions
- ❌ NO CSS/styling specifications
- ❌ NO component implementation details

**Example:**
```markdown
## UI/UX Requirements

### UI Element 1: Priority Selector
**Purpose:** Allow user to select task priority when creating/editing task
**Location:** Task creation form and task edit form, below description field
**Behavior:**
- Display as dropdown or slider showing levels 1-5
- Labels: 1 (Low), 2 (Medium-Low), 3 (Medium), 4 (High), 5 (Critical)
- Optional: Allow "No Priority" selection (null value)
- Default: No priority selected (null)

**States:**
- Empty state: "Select priority (optional)" placeholder
- Selected state: Shows chosen priority level with label
- Disabled state: Grayed out during form submission

### UI Element 2: Priority Display in Task List
**Purpose:** Show task priority at a glance in task list
**Location:** Each task item in the task list, aligned right or as badge
**Behavior:**
- Display priority number with label (e.g., "P3: Medium")
- Optional: Color-code by level (1=green, 5=red)
- Tasks without priority show "No Priority" or no badge

**States:**
- With priority: Shows level and label
- Without priority: No badge or "—" placeholder
- Hover: Shows full priority label tooltip

### UI Element 3: Priority Filter
**Purpose:** Allow user to filter tasks by priority level
**Location:** Above task list, in filter bar
**Behavior:**
- Multi-select: User can select multiple priority levels
- Checkbox or button group for each level 1-5
- Option to show "No Priority" tasks
- Clear all filters button

**States:**
- No filters: All tasks shown
- Filtered: Only matching priority tasks shown
- Empty result: "No tasks match selected priorities" message
- Loading: Shows loading spinner while fetching filtered tasks

### UI Element 4: Priority Change Indicator
**Purpose:** Provide feedback when priority is updated
**Location:** Task item or edit form
**Behavior:**
- On successful update: Brief success message "Priority updated to [level]"
- On error: Error message explaining issue
- Visual feedback: Highlight or animation on change

**States:**
- Saving: Loading indicator on task
- Success: Brief success indicator (green checkmark, 2 seconds)
- Error: Error message with retry option
```

## Validation Checklist

Before finalizing a specification, verify:

**✅ Structure Complete:**
- [ ] All 12 required sections present
- [ ] Sections in logical order
- [ ] Consistent formatting throughout
- [ ] No missing mandatory information

**✅ Clarity Enforced:**
- [ ] No ambiguous language
- [ ] All terms defined
- [ ] Examples provided where helpful
- [ ] Testable acceptance criteria

**✅ Completeness Verified:**
- [ ] All user stories have acceptance criteria
- [ ] All edge cases identified
- [ ] All error scenarios covered
- [ ] Non-goals explicitly stated

**✅ Implementation-Free:**
- [ ] No technology choices (databases, frameworks)
- [ ] No code examples or pseudocode
- [ ] No specific algorithms specified
- [ ] Focus on WHAT, not HOW

**✅ Testability Confirmed:**
- [ ] Every acceptance criterion can be tested
- [ ] Success and failure cases defined
- [ ] Expected outcomes are measurable
- [ ] Edge cases have verification methods

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Implementation Details in Spec

**WRONG:**
```markdown
## Implementation

Use FastAPI with SQLModel. Create a Task model with SQLAlchemy Column for priority.
Use Pydantic Field() validator with ge=1, le=5 for validation.
```

**CORRECT:**
```markdown
## Data Model

### Task
- priority: integer (optional, range 1-5) - Task priority level
```

### ❌ Anti-Pattern 2: Vague Acceptance Criteria

**WRONG:**
```markdown
## Acceptance Criteria

- User can set priority
- System validates priority
- Priority is saved
```

**CORRECT:**
```markdown
## Acceptance Criteria

### AC1: Set Task Priority
**Given** I am on the task creation form
**When** I select priority level 3 from the dropdown
**Then** the task is created with priority = 3
**And** the priority is persisted in the database
```

### ❌ Anti-Pattern 3: Missing Edge Cases

**WRONG:**
```markdown
## Edge Cases

- Handle invalid priority
```

**CORRECT:**
```markdown
## Edge Cases

### Edge Case 1: Priority Below Minimum
**Scenario:** User provides priority = 0
**Expected Behavior:** Validation error "Priority must be between 1 and 5"

### Edge Case 2: Priority Above Maximum
**Scenario:** User provides priority = 10
**Expected Behavior:** Validation error "Priority must be between 1 and 5"

### Edge Case 3: Non-Numeric Priority
**Scenario:** API receives priority = "high"
**Expected Behavior:** Type validation error 422
```

### ❌ Anti-Pattern 4: Inferring Behavior

**WRONG:**
```markdown
Priority will probably need some kind of UI indicator, maybe color-coded.
Users might want to sort by priority, so we should implement that.
```

**CORRECT:**
```markdown
## UI/UX Requirements

Priority must be visible to user in task list.
(Implementation: Decided during design phase)

## Non-Goals

This feature does NOT include automatic sorting by priority.
Manual sorting is handled separately.
```

## Key Rules

- **Enforce structure** - All 12 required sections must be present
- **Enforce clarity** - No ambiguous language, all terms defined
- **Enforce completeness** - All user stories, edge cases, errors covered
- **No implementation** - Describe WHAT, never HOW
- **No code generation** - Specs define requirements, not code
- **No behavior inference** - Everything must be explicitly stated
- **Testable criteria** - Every acceptance criterion can be verified
- **Explicit non-goals** - State what's out of scope clearly
- **User-focused** - User stories from user perspective
- **Error-ready** - All error scenarios documented
- **Edge-case aware** - Boundary conditions identified
- **API-complete** - Full endpoint specifications for backend features
