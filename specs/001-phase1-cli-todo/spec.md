# Feature Specification: Phase 1 CLI Todo App (Enhanced)

**Feature Branch**: `001-phase1-cli-todo`
**Created**: 2025-12-09
**Updated**: 2025-12-09
**Status**: Enhanced with Intermediate & Advanced Features
**Input**: "Phase 1: In-Memory Python Console Todo App - Implement Basic, Intermediate, and Advanced level features with excellent CLI visualization using table format. Features include: Add, Delete, Update, View, Mark Complete (Basic); Priorities, Tags, Search, Filter, Sort (Intermediate); Recurring Tasks, Due Dates & Reminders (Advanced). Uses in-memory storage with clean code principles and proper Python project structure. Pure Python with UV package manager."

## Clarifications

### Session 2025-12-10

- Q: Task ID Generation Strategy → A: Sequential counter that never reuses IDs (e.g., delete task 3, next task gets ID 4, ID 3 never reused)
- Q: Recurring Task Update Behavior → A: Update only current instance - when a recurring task is edited, only that task changes; the next auto-created instance will have original attributes
- Q: Description Field Length Limit → A: 500 characters maximum for task descriptions
- Q: Default Sort Order for Task List → A: Created date (newest first) - recently added tasks appear at top when no explicit sort is specified
- Q: Tag Input Format → A: Comma-separated with quotes for multi-word tags (e.g., `--tags work,urgent,"high priority"` or `--tags "work,urgent,personal finance"`)
- Q: Search with Empty Input → A: Show error message requiring at least one search keyword

## User Scenarios & Testing *(mandatory)*

### **BASIC LEVEL FEATURES** (Foundation - Phase 1 MVP)

### User Story 1 - Capture New Tasks (Priority: P1)

As a user, I want to quickly add tasks to my todo list so I can capture things I need to remember without losing focus on my current work.

**Why this priority**: This is the foundation of the app - users can't use any other features without tasks to manage. It's the minimum viable functionality.

**Independent Test**: Can be fully tested by running the CLI, adding a task with a title, and verifying it appears in the list. Delivers immediate value by allowing task capture.

**Acceptance Scenarios**:

1. **Given** the CLI is running, **When** I add a task with title "Buy groceries", **Then** the task is created with a unique ID and marked as incomplete
2. **Given** the CLI is running, **When** I add a task with title "Call dentist" and description "Schedule annual checkup", **Then** the task is created with both title and description
3. **Given** the CLI is running, **When** I add a task with an empty title, **Then** I receive an error message and the task is not created
4. **Given** I have added several tasks, **When** I add a new task, **Then** it receives a unique ID that doesn't conflict with existing tasks

---

### User Story 2 - View Task List (Priority: P2)

As a user, I want to see all my tasks at a glance so I can plan what to work on next and track my progress.

**Why this priority**: Once users can add tasks, they immediately need to see what they've captured. This provides essential feedback and makes the app useful.

**Independent Test**: Can be tested by adding 2-3 tasks and viewing the list, which should display all tasks with their status, ID, title, and completion state.

**Acceptance Scenarios**:

1. **Given** I have added 3 tasks, **When** I view the task list, **Then** I see all 3 tasks with their ID, title, and completion status
2. **Given** I have no tasks, **When** I view the task list, **Then** I see a message indicating the list is empty
3. **Given** I have tasks with descriptions, **When** I view the task list, **Then** I can see or access the description for each task
4. **Given** I have both complete and incomplete tasks, **When** I view the task list, **Then** I can clearly distinguish between completed and incomplete tasks

---

### User Story 3 - Mark Tasks Complete (Priority: P3)

As a user, I want to mark tasks as complete when I finish them so I can track my progress and feel accomplished.

**Why this priority**: This adds essential value by letting users track progress. It's the core benefit of a todo list - seeing things get done.

**Independent Test**: Can be tested by adding a task, marking it complete, and viewing the list to verify the status changed. Provides motivational value.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with ID 1, **When** I mark it as complete, **Then** its status changes to complete and I see confirmation
2. **Given** I have a complete task with ID 2, **When** I mark it as incomplete, **Then** its status changes back to incomplete
3. **Given** I try to mark a non-existent task ID as complete, **When** I execute the command, **Then** I receive an error message
4. **Given** I have 5 tasks, **When** I mark task 3 as complete, **Then** only task 3's status changes, others remain unchanged

---

### User Story 4 - Update Task Details (Priority: P4)

As a user, I want to edit task titles and descriptions so I can fix typos or add more details as I learn more about the task.

**Why this priority**: Mistakes happen and requirements change. This prevents users from having to delete and re-create tasks.

**Independent Test**: Can be tested by adding a task, updating its title or description, and verifying the changes persist.

**Acceptance Scenarios**:

1. **Given** I have a task with title "Buy milk", **When** I update it to "Buy milk and eggs", **Then** the title changes and I see confirmation
2. **Given** I have a task without a description, **When** I add a description "From the organic store", **Then** the description is added to the task
3. **Given** I try to update a non-existent task ID, **When** I execute the command, **Then** I receive an error message
4. **Given** I try to update a task with an empty title, **When** I execute the command, **Then** I receive an error and the task remains unchanged

---

### User Story 5 - Delete Unwanted Tasks (Priority: P5)

As a user, I want to delete tasks I no longer need so I can keep my list focused and uncluttered.

**Why this priority**: While useful, deletion is less critical than other operations. Users can work around this by ignoring tasks or marking them complete.

**Independent Test**: Can be tested by adding a task, deleting it, and verifying it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 1, **When** I delete it, **Then** it is removed from the list and I see confirmation
2. **Given** I try to delete a non-existent task ID, **When** I execute the command, **Then** I receive an error message
3. **Given** I have 3 tasks, **When** I delete task 2, **Then** only task 2 is removed, tasks 1 and 3 remain
4. **Given** I delete all my tasks, **When** I view the list, **Then** I see an empty list message

---

### **INTERMEDIATE LEVEL FEATURES** (Organization & Usability)

### User Story 6 - Assign Priorities and Tags (Priority: P6)

As a user, I want to assign priority levels (high/medium/low) and tags/categories (work/home/personal) to my tasks so I can organize and focus on what matters most.

**Why this priority**: Priority and categorization make the app practical for real-world use, allowing users to organize tasks by urgency and context.

**Independent Test**: Can be tested by adding tasks with different priorities and tags, then viewing the list to verify they display clearly with visual indicators.

**Acceptance Scenarios**:

1. **Given** I add a task, **When** I set priority to "high", **Then** the task displays with high priority indicator (e.g., ❗ HIGH or red color)
2. **Given** I have a task, **When** I assign tags "work" and "urgent", **Then** the task shows both tags in the list view
3. **Given** I have tasks with different priorities, **When** I view the list, **Then** I can clearly distinguish between high/medium/low priority tasks
4. **Given** I update a task's priority from "low" to "high", **When** I view the list, **Then** the priority indicator updates accordingly

---

### User Story 7 - Search Tasks (Priority: P7)

As a user, I want to search for tasks by keyword so I can quickly find specific tasks in a large list.

**Why this priority**: Search is essential when the task list grows beyond a few items, making the app scalable for real usage.

**Independent Test**: Can be tested by adding 10+ tasks with varied titles and descriptions, then searching for specific keywords to verify accurate results.

**Acceptance Scenarios**:

1. **Given** I have tasks with titles containing "meeting", **When** I search for "meeting", **Then** I see only tasks matching that keyword
2. **Given** I search for a keyword that exists in descriptions, **When** I execute search, **Then** tasks with matching descriptions are included
3. **Given** I search for a non-existent keyword, **When** I execute search, **Then** I see a "no results found" message
4. **Given** I search with empty input, **When** I execute search, **Then** I receive an error message requiring at least one search keyword

---

### User Story 8 - Filter Tasks (Priority: P8)

As a user, I want to filter tasks by status (complete/incomplete), priority, tags, or due date so I can focus on specific subsets of my tasks.

**Why this priority**: Filtering reduces cognitive load by showing only relevant tasks, making the app more practical for daily use.

**Independent Test**: Can be tested by creating tasks with various combinations of status, priority, and tags, then applying different filters to verify correct results.

**Acceptance Scenarios**:

1. **Given** I have 10 tasks (5 complete, 5 incomplete), **When** I filter by "incomplete", **Then** I see only the 5 incomplete tasks
2. **Given** I have tasks with different priorities, **When** I filter by "high priority", **Then** I see only high-priority tasks
3. **Given** I have tasks with various tags, **When** I filter by tag "work", **Then** I see only tasks tagged with "work"
4. **Given** I apply multiple filters (e.g., incomplete + high priority), **When** I view results, **Then** I see tasks matching all filter criteria

---

### User Story 9 - Sort Tasks (Priority: P9)

As a user, I want to sort tasks by due date, priority, created date, or alphabetically so I can view my tasks in the most useful order for my current context.

**Why this priority**: Sorting helps users organize their mental model of work, whether by urgency (due date), importance (priority), or recency.

**Independent Test**: Can be tested by creating tasks with various dates and priorities, then applying different sort options to verify correct ordering.

**Acceptance Scenarios**:

1. **Given** I have tasks with different due dates, **When** I sort by "due date", **Then** tasks appear with soonest due dates first
2. **Given** I have tasks with different priorities, **When** I sort by "priority", **Then** tasks appear as high → medium → low
3. **Given** I have tasks, **When** I sort by "title alphabetically", **Then** tasks appear in A-Z order
4. **Given** I have tasks, **When** I sort by "created date", **Then** newest or oldest tasks appear first (based on direction)

---

### **ADVANCED LEVEL FEATURES** (Intelligent Features)

### User Story 10 - Recurring Tasks (Priority: P10)

As a user, I want to create recurring tasks (daily, weekly, monthly) that automatically reschedule after completion so I don't have to manually recreate repetitive tasks.

**Why this priority**: Recurring tasks save significant time for repetitive work (e.g., "weekly team meeting", "daily standup", "monthly report").

**Independent Test**: Can be tested by creating a recurring task, completing it, and verifying a new instance is automatically created with the next due date.

**Acceptance Scenarios**:

1. **Given** I create a task with recurrence "weekly", **When** I mark it complete, **Then** a new identical task is created with due date 7 days from now
2. **Given** I have a daily recurring task, **When** I complete it, **Then** a new task appears with tomorrow's date
3. **Given** I create a monthly recurring task, **When** I complete it, **Then** a new task appears with due date 1 month from now
4. **Given** I edit a recurring task, **When** I update it, **Then** only the current instance is updated; the next auto-created instance will have the original (pre-edit) attributes

---

### User Story 11 - Due Dates and Time Reminders (Priority: P11)

As a user, I want to set due dates and receive reminders so I don't miss important deadlines.

**Why this priority**: Due dates and reminders transform the app from a passive list into an active productivity tool that helps users stay on track.

**Independent Test**: Can be tested by creating tasks with various due dates, checking that overdue tasks are highlighted, and that upcoming tasks trigger reminders.

**Acceptance Scenarios**:

1. **Given** I add a task with due date "2025-12-15 14:00", **When** I view the list, **Then** the due date displays clearly with the task
2. **Given** I have a task due today, **When** I view the list, **Then** it is highlighted or marked as "due today"
3. **Given** I have an overdue task, **When** I view the list, **Then** it is clearly marked as overdue with visual indicator (e.g., ⚠️ OVERDUE in red)
4. **Given** I set a reminder for a task, **When** the reminder time arrives (while app is running), **Then** I see a notification or alert
5. **Given** I have tasks with various due dates, **When** I sort by due date, **Then** overdue tasks appear first, followed by upcoming deadlines

---

### Edge Cases

**Basic Features:**
- What happens when a user enters a very long task title (e.g., 500 characters)?
- What happens when a user tries to add a task with only whitespace as the title?
- What happens when a user provides an invalid task ID (e.g., negative number, letter, or extremely large number)?
- What happens when the user exits the application - is the data loss clearly communicated?
- What happens when a user enters special characters or unicode in task titles/descriptions?
- What happens if the user attempts multiple operations in rapid succession?

**Intermediate Features:**
- What happens when a user assigns an invalid priority level?
- What happens when a user tries to filter/sort with no matching tasks?
- What happens when a user assigns multiple tags with special characters or spaces?
- What happens when search query contains regex special characters?
- What happens when sorting by a field that has null values (e.g., due date)?

**Advanced Features:**
- What happens when a recurring task's next occurrence conflicts with an existing task?
- What happens when a user sets a due date in the past?
- What happens when a reminder is due but the app is not running (reminder missed)?
- What happens when a user creates a recurring task with invalid recurrence pattern?
- What happens when system time changes (timezone, DST)?

## Requirements *(mandatory)*

### Functional Requirements

**Basic Level (Essential):**
- **FR-001**: System MUST allow users to add a new task with a required title (1-200 characters) and optional description (max 500 characters)
- **FR-002**: System MUST assign a unique integer ID to each task automatically upon creation using a sequential counter that never reuses IDs (e.g., if task 3 is deleted, the next task gets ID 4, not ID 3)
- **FR-003**: System MUST allow users to view all tasks in a well-formatted table displaying: ID, title,description, status, priority, tags, due date
- **FR-004**: System MUST allow users to mark a task as complete or incomplete using its ID
- **FR-005**: System MUST allow users to update the title and/or description of an existing task using its ID
- **FR-006**: System MUST allow users to delete a task using its ID
- **FR-007**: System MUST validate that task titles are not empty (excluding whitespace)
- **FR-008**: System MUST store all tasks in memory during program execution
- **FR-009**: System MUST provide clear success messages for all successful operations
- **FR-010**: System MUST provide clear error messages for invalid operations (e.g., invalid ID, empty title)
- **FR-011**: System MUST NOT persist data between application sessions (in-memory only)
- **FR-012**: System MUST provide a command to exit the application cleanly
- **FR-013**: System MUST display a welcome message on startup explaining available commands
- **FR-014**: System MUST handle graceful shutdown when user exits

**Intermediate Level (Organization & Usability):**
- **FR-015**: System MUST allow users to assign priority levels (high, medium, low) to tasks
- **FR-016**: System MUST allow users to assign one or more tags/categories to tasks (e.g., "work", "home", "personal") using comma-separated format with quotes for multi-word tags (e.g., `work,urgent,"high priority"`)
- **FR-017**: System MUST provide search functionality that matches keywords in task titles and descriptions (case-insensitive), and MUST return an error if search input is empty
- **FR-018**: System MUST provide filtering by status (complete/incomplete), priority (high/medium/low), and tags
- **FR-019**: System MUST support multiple simultaneous filters (e.g., incomplete + high priority + work tag)
- **FR-020**: System MUST allow users to sort tasks by: due date (ascending/descending), priority, created date, title (alphabetical)
- **FR-020a**: System MUST display tasks sorted by created date (newest first) when no explicit sort order is specified by the user
- **FR-021**: System MUST display visual indicators for priorities in list view (e.g., ❗HIGH, ➖MEDIUM, ⬇LOW)
- **FR-022**: System MUST display tags clearly in list view with visual separation

**Advanced Level (Intelligent Features):**
- **FR-023**: System MUST support recurring tasks with patterns: daily, weekly, monthly
- **FR-024**: System MUST automatically create next instance of recurring task when marked complete, using the original task attributes (not any edits made to the current instance)
- **FR-025**: System MUST allow users to set due dates with date and time (format: YYYY-MM-DD HH:MM)
- **FR-026**: System MUST highlight overdue tasks with visual indicator (e.g., ⚠️ OVERDUE in red text)
- **FR-027**: System MUST highlight tasks due today with visual indicator
- **FR-028**: System MUST support reminder times for tasks (e.g., "remind me 1 hour before due")
- **FR-029**: System MUST display notification/alert when reminder time is reached (if app is running)
- **FR-030**: System MUST sort by due date with overdue tasks appearing first, then by proximity to deadline

### Key Entities

- **Task**: Represents a single todo item with the following attributes:
  - ID (unique integer identifier, auto-generated using sequential counter starting from 1, never reused after deletion)
  - Title (required string, 1-200 characters)
  - Description (optional string, max 500 characters)
  - Completed (boolean status, defaults to false)
  - Priority (enum: HIGH, MEDIUM, LOW, defaults to MEDIUM)
  - Tags (list of strings parsed from comma-separated input, e.g., ["work", "urgent", "high priority"])
  - Due Date (optional datetime, format: YYYY-MM-DD HH:MM)
  - Recurrence (optional enum: NONE, DAILY, WEEKLY, MONTHLY, defaults to NONE)
  - Reminder (optional integer: minutes before due date, e.g., 60 for 1 hour)
  - Created At (timestamp for when task was created)
  - Updated At (timestamp for when task was last modified)

### CLI Visualization Requirements *(NEW - High Priority)*

The CLI interface MUST provide excellent visualization using table format and visual indicators:

**Table Format:**
- **FR-031**: Task list MUST be displayed in a well-formatted ASCII table with clear borders
- **FR-032**: Table MUST include columns: ID,Title, Status, Priority, Tags, Due Date, Recurrence
- **FR-033**: Table rows MUST be properly aligned with consistent spacing
- **FR-034**: Long titles MUST be truncated with "..." if they exceed column width
- **FR-035**: Table MUST adjust column widths based on terminal size (responsive)

**Visual Indicators:**
- **FR-036**: Completed tasks MUST show ✓ or [✓] status indicator
- **FR-037**: Incomplete tasks MUST show ☐ or [ ] status indicator
- **FR-038**: High priority MUST show ❗or [!] in red/bright color
- **FR-039**: Medium priority MUST show ➖ or [-] in yellow/normal color
- **FR-040**: Low priority MUST show ⬇ or [v] in blue/dim color
- **FR-041**: Overdue tasks MUST show ⚠️ and be highlighted in red
- **FR-042**: Tasks due today MUST be highlighted in yellow/amber
- **FR-043**: Tags MUST be displayed with clear separators (e.g., [work] [urgent])

**Table Example:**
```
╔════╦════════╦══════════╦═══════════════════════════╦═════════════════╦══════════════════╗
║ ID ║ Status ║ Priority ║ Title                     ║ Tags            ║ Due Date         ║
╠════╬════════╬══════════╬═══════════════════════════╬═════════════════╬══════════════════╣
║  1 ║   ☐    ║  ❗HIGH   ║ Complete project proposal ║ [work] [urgent] ║ 2025-12-10 17:00 ║
║  2 ║   ✓    ║  ➖MED    ║ Buy groceries             ║ [personal]      ║ 2025-12-09 18:00 ║
║  3 ║   ☐    ║  ⬇LOW    ║ Read book chapter         ║ [personal]      ║ 2025-12-15 --:-- ║
║  4 ║   ☐    ║  ❗HIGH   ║ ⚠️  Call client (OVERDUE) ║ [work]          ║ 2025-12-08 14:00 ║
╚════╩════════╩══════════╩═══════════════════════════╩═════════════════╩══════════════════╝
```

**Color Scheme (if terminal supports colors):**
- Green: Completed tasks
- Red: Overdue tasks, HIGH priority
- Yellow: Due today, MEDIUM priority
- Blue: LOW priority
- Gray/Dim: Descriptions and metadata

**Alternative Plain ASCII (for limited terminals):**
```
+----+--------+----------+---------------------------+-----------------+------------------+
| ID | Status | Priority | Title                     | Tags            | Due Date         |
+----+--------+----------+---------------------------+-----------------+------------------+
|  1 |   [ ]  |  [!] H   | Complete project proposal | [work] [urgent] | 2025-12-10 17:00 |
|  2 |   [X]  |  [-] M   | Buy groceries             | [personal]      | 2025-12-09 18:00 |
|  3 |   [ ]  |  [v] L   | Read book chapter         | [personal]      | 2025-12-15 --:-- |
|  4 |   [ ]  |  [!] H   | [!] Call client (OVERDUE) | [work]          | 2025-12-08 14:00 |
+----+--------+----------+---------------------------+-----------------+------------------+
```

### Non-Functional Requirements

**Performance:**
- **NFR-001**: All task operations (add, view, update, delete, complete) MUST complete in under 1 second on standard hardware
- **NFR-002**: Search and filter operations MUST complete in under 2 seconds for lists up to 1000 tasks
- **NFR-003**: Table rendering MUST be optimized to handle at least 100 tasks without noticeable lag

**Usability:**
- **NFR-004**: The CLI MUST be intuitive enough that users can perform basic operations without reading documentation
- **NFR-005**: Error messages MUST be user-friendly and suggest corrective action
- **NFR-006**: The application MUST warn users that data is not persisted (e.g., in startup message or help text)
- **NFR-007**: The CLI MUST detect terminal capabilities (colors, unicode) and adapt visualization accordingly
- **NFR-008**: Help command MUST provide clear commands and examples for all operations

**User Experience:**
- **NFR-009**: The table format MUST make tasks easy to scan at a glance
- **NFR-010**: Visual indicators MUST be clear and consistent throughout the app
- **NFR-011**: The interface MUST provide a sense of progress and accomplishment (e.g., completed task count)
- **NFR-012**: Commands MUST be short and memorable (e.g., "add", "list", "done", not verbose)

### Assumptions

- Users will interact with the application through command-line interface only
- No authentication is required (single-user application for Phase 1)
- Task IDs will be simple integers starting from 1, incremented sequentially, and never reused (even after deletion)
- Application will be used for short sessions (in-memory storage is acceptable)
- Standard terminal/console character encoding (UTF-8) is available
- Users have basic familiarity with command-line interfaces
- Terminal supports at least 100 characters width for table display
- System clock is accurate for due date and reminder functionality
- Users understand that reminders only work while application is running
- Python 3.12+ environment with modern terminal (supports ANSI colors preferred)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Basic Features:**
- **SC-001**: Users can add, view, update, mark complete, and delete tasks through simple CLI commands without errors
- **SC-002**: All basic task operations complete within 1 second for lists up to 100 tasks
- **SC-003**: Users can successfully complete the primary workflow (add task → view list → mark complete) in under 30 seconds on first use
- **SC-004**: Error messages for common mistakes (invalid ID, empty title) are clear enough that users can correct the error without external help
- **SC-005**: The application starts, accepts commands, and exits cleanly without crashes or unexpected errors

**Intermediate Features:**
- **SC-006**: Users can assign priorities and tags to tasks and see them clearly in the table view
- **SC-007**: Search returns accurate results in under 2 seconds for lists up to 1000 tasks
- **SC-008**: Users can apply multiple filters simultaneously (e.g., incomplete + high priority + work tag) and get expected results
- **SC-009**: Sorting by any criterion (due date, priority, title, created date) works correctly and displays in expected order

**Advanced Features:**
- **SC-010**: Recurring tasks automatically create next instance when completed, with correct due date calculation
- **SC-011**: Overdue tasks are clearly highlighted in red and appear first when sorted by due date
- **SC-012**: Reminders trigger correctly when due time arrives (if app is running)
- **SC-013**: Users can manage tasks with due dates spanning weeks/months without issues

**Visualization:**
- **SC-014**: Task list displays in a clean, well-formatted table with borders and proper alignment
- **SC-015**: Visual indicators (✓, ❗, ⚠️) are clear and consistent across all views
- **SC-016**: Table remains readable with up to 50 tasks displayed without scrolling off-screen
- **SC-017**: The interface adapts gracefully to terminals with and without unicode/color support

### User Experience Goals

- Intuitive command structure that mimics natural language where possible (e.g., "add Buy milk", "done 1", "list work")
- Immediate visual feedback for all actions with success confirmations
- Clear distinction between completed and incomplete tasks in table view
- Minimal keystrokes required for common operations
- Visual hierarchy that makes high-priority and overdue tasks immediately noticeable
- Professional, polished appearance that users would want to use daily

---

## Out of Scope (For Phase 1)

**Deferred to Phase 2+:**
- Data persistence to disk or database (Phase 2)
- Multi-user support or authentication (Phase 2)
- Web interface (Phase 2)
- RESTful API (Phase 2)
- Cloud synchronization (Phase 2+)

**Deferred to Future Phases:**
- AI-powered natural language task creation (Phase 3)
- Mobile or desktop GUI (Phase 2+)
- Integration with external calendar/task apps (Phase 2+)
- Email/SMS notifications (Phase 2+)
- Team collaboration features (Phase 2+)
- Subtasks and task dependencies (Phase 4+)
- Time tracking and productivity analytics (Phase 5)
- Export/import functionality (CSV, JSON) (Phase 5)
- Task templates or automation rules (Phase 5)
- Custom fields or task types (Phase 5)

**Never in Scope for CLI:**
- Undo/redo capabilities (complex state management not suitable for in-memory CLI)
- Real-time push notifications when app is closed
- Offline-first architecture (not relevant for in-memory storage)

---

## Notes

### Phased Evolution Context

This specification defines **Phase 1** of a 5-phase evolution:
- **Phase 1** (this spec): Enhanced CLI with Basic + Intermediate + Advanced features, in-memory storage
- **Phase 2**: Add web interface (Next.js) and database persistence (Neon PostgreSQL)
- **Phase 3**: Add AI chatbot interface using OpenAI Agents SDK and MCP
- **Phase 4**: Kubernetes deployment (Minikube, Helm, kubectl-ai, Kagent)
- **Phase 5**: Cloud deployment (DOKS/GKE/AKS) with Kafka and Dapr

### Implementation Strategy

**Recommended Development Order:**

1. **Foundation (Basic Features - P1-P5):**
   - Implement core Task entity with all attributes
   - Build in-memory storage layer
   - Create basic CLI commands (add, list, update, delete, done)
   - Implement table visualization framework

2. **Organization (Intermediate Features - P6-P9):**
   - Add priority and tags to Task entity
   - Implement search algorithm (keyword matching)
   - Build filtering engine (by status, priority, tags)
   - Implement sorting functions (by due date, priority, etc.)
   - Enhance table to display priorities and tags with visual indicators

3. **Intelligence (Advanced Features - P10-P11):**
   - Add due date and recurrence fields to Task entity
   - Implement recurring task logic (auto-create next instance)
   - Build due date comparison logic (overdue detection)
   - Implement reminder system (background thread monitoring)
   - Add visual indicators for overdue and due-today tasks

4. **Polish & Testing:**
   - Refine table formatting and responsive column widths
   - Add color support detection and graceful fallback
   - Comprehensive testing of all features
   - Performance optimization for large task lists
   - Documentation and help system

### Architecture Principles

The architecture MUST support evolution to future phases by:
- **Separation of Concerns**: Core business logic independent of CLI interface
- **Modular Design**: Task management, storage, visualization, and CLI as separate modules
- **Type Safety**: Complete Python type hints for all functions and classes
- **Testability**: All business logic unit-testable without CLI dependencies
- **Future-Proof**: Data structures designed to persist in Phase 2 without major changes

### Technology Stack

**Required:**
- Python 3.12+ (for advanced type hints and modern features)
- UV package manager (for dependency management)

**Recommended Libraries:**
- `rich` or `tabulate` - for table formatting and colors
- `click` or `typer` - for CLI command parsing (optional)
- `python-dateutil` - for date/time handling
- `colorama` - for cross-platform color support (Windows compatibility)

### Key Technical Challenges

1. **Table Rendering**: Dynamic column widths, text wrapping, unicode support
2. **Recurring Tasks**: Accurate date calculations for daily/weekly/monthly recurrence
3. **Reminders**: Background thread for monitoring due times while app runs
4. **Color Detection**: Graceful fallback for terminals without ANSI color support
5. **Performance**: Efficient search/filter/sort for large lists (1000+ tasks)
