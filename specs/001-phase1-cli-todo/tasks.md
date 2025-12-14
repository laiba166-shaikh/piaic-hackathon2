# Implementation Tasks: Phase 1 CLI Todo App

**Feature Branch**: `001-phase1-cli-todo`
**Date**: 2025-12-10
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Approach**: Test-First (TDD) - Red → Green → Refactor

---

## Task Organization

Tasks are organized by **User Story** to ensure each feature is independently implementable and testable. Each story follows the TDD workflow:
1. **RED**: Write failing tests first
2. **GREEN**: Implement minimal code to pass tests
3. **REFACTOR**: Clean up code while keeping tests green

**Execution Order**:
- Phase 0: Setup (prerequisites for all user stories)
- Phase 1: Foundational (blocking dependencies)
- Phase 2-12: User Stories P1-P11 (in priority order)
- Phase 13: Polish and Cross-Cutting Concerns

**Parallel Execution**:
- Tasks marked **[P]** can run in parallel with other [P] tasks in the same phase
- Tasks marked **[Story]** map to specific user stories
- Tasks WITHOUT [P] must run sequentially

**Dependency Graph**:
```
Setup → Foundational → [US1, US2, US3, US4, US5] → [US6, US7, US8, US9] → [US10, US11] → Polish
                            ↓
                        [Can run in parallel after foundational]
```

---

## Phase 0: Setup and Project Initialization

**Objective**: Establish project structure, dependencies, and development environment.

- [X] [SETUP-001] [P] Initialize project structure with src/, tests/, specs/, history/ directories (plan.md:208-294)
- [X] [SETUP-002] [P] Create pyproject.toml with project metadata, dependencies (rich, click, python-dateutil), and dev dependencies (pytest, mypy, pytest-cov)
- [X] [SETUP-003] [P] Create .gitignore with Python, IDE, and OS ignores
- [X] [SETUP-004] [P] Create README.md with project overview and setup instructions
- [X] [SETUP-005] [P] Create .env.example with LOG_LEVEL configuration template
- [ ] [SETUP-006] Install UV package manager and verify installation (plan.md:39)
- [ ] [SETUP-007] Install project dependencies using `uv pip install -e .`
- [X] [SETUP-008] Create GitHub Actions CI workflow (.github/workflows/test.yml) for pytest, mypy, coverage (plan.md:105-121)
- [X] [SETUP-009] Create tests/conftest.py with shared pytest fixtures (sample tasks, mock storage)

**Acceptance**: Project structure matches plan.md structure, all dependencies install cleanly, CI workflow runs successfully.

---

## Phase 1: Foundational Layer (Blocking Dependencies)

**Objective**: Build core models, storage abstraction, and base CLI structure that all user stories depend on.

### Core Models and Enums

- [X] [FOUND-001] [RED] [P] Write unit tests for Priority enum (HIGH, MEDIUM, LOW) in tests/unit/test_models.py
- [X] [FOUND-002] [GREEN] [P] Implement Priority enum in src/core/models.py (data-model.md:35-38)
- [X] [FOUND-003] [RED] [P] Write unit tests for Recurrence enum (NONE, DAILY, WEEKLY, MONTHLY) in tests/unit/test_models.py
- [X] [FOUND-004] [GREEN] [P] Implement Recurrence enum in src/core/models.py (data-model.md:40-44)
- [X] [FOUND-005] [RED] Write unit tests for Task dataclass validation in tests/unit/test_models.py
  - Test title required, 1-200 chars (FR-001, FR-007)
  - Test description max 500 chars (FR-001 clarified)
  - Test reminder must be positive integer (FR-028)
  - Test default values (completed=False, priority=MEDIUM, recurrence=NONE)
- [X] [FOUND-006] [GREEN] Implement Task dataclass with __post_init__ validation in src/core/models.py (data-model.md:47-78)
- [X] [FOUND-007] [RED] [P] Write unit tests for Task.is_overdue() method in tests/unit/test_models.py
- [X] [FOUND-008] [GREEN] [P] Implement Task.is_overdue() method in src/core/models.py (data-model.md:70-73)
- [X] [FOUND-009] [RED] [P] Write unit tests for Task.is_due_today() method in tests/unit/test_models.py
- [X] [FOUND-010] [GREEN] [P] Implement Task.is_due_today() method in src/core/models.py (data-model.md:75-78)
- [X] [FOUND-011] [REFACTOR] Run mypy on src/core/models.py, fix type hint issues

**Acceptance**: All Task model tests pass, mypy validation passes, 100% code coverage for models.py.

### Custom Exceptions

- [X] [FOUND-012] [GREEN] [P] Create src/core/exceptions.py with TaskNotFoundError, ValidationError, InvalidIDError

### Storage Abstraction Layer

- [X] [FOUND-013] [RED] Write contract tests for ITaskStorage interface in tests/contract/test_storage_interface.py
  - Test create assigns unique sequential ID (never reused) (contracts/storage.py:25-26)
  - Test create sets created_at and updated_at timestamps (contracts/storage.py:27-28)
  - Test get returns None if not found (contracts/storage.py:29)
  - Test list_all returns newest first (created_at descending) (contracts/storage.py:30)
  - Test update sets updated_at timestamp (contracts/storage.py:28)
  - Test delete does not reuse ID (contracts/storage.py:26)
  - Test delete nonexistent returns False (contracts/storage.py:29)
  - Test update nonexistent raises TaskNotFoundError
- [X] [FOUND-014] [GREEN] Create ITaskStorage ABC interface in src/core/storage/base.py (contracts/storage.py:22-141)
- [X] [FOUND-015] [RED] Write unit tests for MemoryStorage implementation in tests/unit/test_storage.py
  - Test all contract requirements from FOUND-013
  - Test thread-safety for sequential counter (optional for Phase 1)
- [X] [FOUND-016] [GREEN] Implement MemoryStorage with dict-based storage in src/core/storage/memory.py (plan.md:344-520)
  - Implement _counter for sequential ID generation
  - Implement _tasks dict for in-memory storage
  - Implement create, get, list_all, update, delete methods
- [X] [FOUND-017] [REFACTOR] Run contract tests against MemoryStorage, ensure 100% pass rate

**Acceptance**: All contract tests pass for MemoryStorage, storage interface is future-proof for Phase 2 DatabaseStorage.

### Configuration and Logging

- [X] [FOUND-018] [GREEN] [P] Create src/config.py with logging setup, constants (plan.md:139-148)
- [X] [FOUND-019] [GREEN] [P] Configure structured logging format: `[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE`

### CLI Foundation

- [X] [FOUND-020] [GREEN] [P] Create src/cli/main.py with Click app entry point (plan.md:242)
- [X] [FOUND-021] [GREEN] [P] Create src/cli/commands/__init__.py for command registration
- [X] [FOUND-022] [RED] Write integration test for CLI startup message (FR-013) in tests/integration/test_cli_commands.py
- [X] [FOUND-023] [GREEN] Implement --help command and welcome message in src/cli/main.py

**Acceptance**: CLI starts, displays welcome message, responds to --help, exits cleanly.

---

## Phase 2: User Story 1 - Capture New Tasks (Priority: P1)

**User Story**: As a user, I want to quickly add tasks to my todo list so I can capture things I need to remember without losing focus on my current work.

**Acceptance Scenarios**: spec.md:32-37

### RED Phase (Tests First)

- [X] [US1-001] [RED] Write integration test for `add` command with title only in tests/integration/test_cli_commands.py
  - Test: `todo add "Buy groceries"` creates task with ID 1, incomplete status
  - Verify task appears in storage with auto-generated ID
- [X] [US1-002] [RED] Write integration test for `add` command with title and description
  - Test: `todo add "Call dentist" -d "Schedule annual checkup"`
  - Verify both title and description are stored
- [X] [US1-003] [RED] Write integration test for `add` command with empty title (FR-007)
  - Test: `todo add ""`
  - Verify ValidationError is raised with clear message
- [X] [US1-004] [RED] Write integration test for unique ID assignment (FR-002)
  - Test: Add 3 tasks, verify IDs are 1, 2, 3 (sequential)
- [X] [US1-005] [RED] Write unit test for TaskService.create_task() in tests/unit/test_services.py
  - Mock ITaskStorage, verify create() is called with correct Task object

### GREEN Phase (Implementation)

- [X] [US1-006] [GREEN] Create TaskService class in src/core/services.py with __init__(storage: ITaskStorage)
- [X] [US1-007] [GREEN] Implement TaskService.create_task(title, description=None) method
  - Create Task object with title, description
  - Call storage.create(task)
  - Return created task with assigned ID
- [X] [US1-008] [GREEN] Create src/cli/commands/basic.py with `add` command using Click
  - Define @click.command() for `add`
  - Accept title as argument, description as --description/-d option
  - Call TaskService.create_task()
  - Display success message with task ID (FR-009)
- [X] [US1-009] [GREEN] Register `add` command in src/cli/main.py

### REFACTOR Phase

- [X] [US1-010] [REFACTOR] Add input validation in `add` command (FR-007)
  - Check title is not empty/whitespace
  - Display error message if validation fails (FR-010)
- [X] [US1-011] [REFACTOR] Add logging for task creation in src/core/services.py
- [X] [US1-012] [REFACTOR] Run all US1 tests, ensure 100% pass rate
- [X] [US1-013] [REFACTOR] Run mypy on src/core/services.py and src/cli/commands/basic.py

**Acceptance**: SC-001 (partial), all US1 acceptance scenarios pass, user can add tasks with title and optional description.

---

## Phase 3: User Story 2 - View Task List (Priority: P2)

**User Story**: As a user, I want to see all my tasks at a glance so I can plan what to work on next and track my progress.

**Acceptance Scenarios**: spec.md:49-53

### RED Phase (Tests First)

- [X] [US2-001] [RED] Write integration test for `list` command with tasks in tests/integration/test_cli_commands.py
  - Add 3 tasks, run `todo list`
  - Verify all 3 tasks are displayed with ID, title, status
- [X] [US2-002] [RED] Write integration test for `list` command with empty task list
  - Run `todo list` with no tasks
  - Verify "no tasks" message is displayed
- [X] [US2-003] [RED] Write integration test for task list showing descriptions
  - Add task with description, run `todo list`
  - Verify description is visible or accessible
- [X] [US2-004] [RED] Write integration test for distinguishing complete vs incomplete tasks
  - Add 2 tasks, mark one complete
  - Verify visual distinction (✓ vs ☐) in output
- [X] [US2-005] [RED] Write unit test for TaskService.list_all() in tests/unit/test_services.py
  - Mock storage.list_all(), verify correct return value

### GREEN Phase (Implementation)

- [X] [US2-006] [GREEN] Implement TaskService.list_all() method in src/core/services.py
  - Call storage.list_all()
  - Return list of tasks (sorted by created_at descending per FR-020a)
- [X] [US2-007] [GREEN] Create src/cli/rendering/table.py with render_task_table() function
  - Use Rich Table with columns: ID, Status, Priority, Title, Tags, Due Date (FR-032)
  - Add rows for each task
  - Return formatted table
- [X] [US2-008] [GREEN] Create src/cli/rendering/colors.py with PRIORITY_INDICATORS dict (data-model.md:108-114)
  - Map Priority.HIGH to ("[!]", "red") - text-based for Windows compatibility
  - Map Priority.MEDIUM to ("[-]", "yellow")
  - Map Priority.LOW to ("[v]", "blue")
- [X] [US2-009] [GREEN] Add STATUS_INDICATORS to src/cli/rendering/colors.py
  - Map completed=True to ("[X]", "green") (FR-036)
  - Map completed=False to ("[ ]", "white") (FR-037)
- [X] [US2-010] [GREEN] Implement `list` command in src/cli/commands/basic.py
  - Call TaskService.list_all()
  - If empty, display "No tasks found" message
  - Otherwise, call render_task_table() and print
- [X] [US2-011] [GREEN] Register `list` command in src/cli/main.py

### REFACTOR Phase

- [ ] [US2-012] [REFACTOR] Add table formatting tests in tests/integration/test_table_rendering.py
  - Test table has proper borders (FR-031)
  - Test columns are aligned (FR-033)
  - Test long titles are truncated with "..." (FR-034)
- [ ] [US2-013] [REFACTOR] Implement responsive column widths in render_task_table() (FR-035)
  - Use Rich's expand=True, ratio for dynamic widths (ADR-002)
- [ ] [US2-014] [REFACTOR] Add unicode detection and ASCII fallback in src/cli/rendering/table.py
  - Use Rich Console to detect terminal capabilities (FR-007, SC-017)
  - Fallback to ASCII box chars (+---+) if unicode unsupported
- [X] [US2-015] [REFACTOR] Run all US2 tests, ensure 100% pass rate
- [ ] [US2-016] [REFACTOR] Verify table displays correctly with 10+ tasks

**Acceptance**: SC-001 (partial), SC-014, SC-017, all US2 acceptance scenarios pass, users can view tasks in formatted table.

---

## Phase 4: User Story 3 - Mark Tasks Complete (Priority: P3)

**User Story**: As a user, I want to mark tasks as complete when I finish them so I can track my progress and feel accomplished.

**Acceptance Scenarios**: spec.md:66-70

### RED Phase (Tests First)

- [X] [US3-001] [RED] Write integration test for `done` command in tests/integration/test_cli_commands.py
  - Add task, run `todo done 1`
  - Verify task status changes to completed=True
- [X] [US3-002] [RED] Write integration test for marking task incomplete (`undone` command)
  - Mark task complete, then run `todo undone 1`
  - Verify status changes back to completed=False
- [X] [US3-003] [RED] Write integration test for `done` with invalid ID
  - Run `todo done 999`
  - Verify error message is displayed (FR-010)
- [X] [US3-004] [RED] Write integration test for `done` affecting only target task
  - Add 5 tasks, mark task 3 complete
  - Verify tasks 1, 2, 4, 5 remain incomplete
- [X] [US3-005] [RED] Write unit test for TaskService.mark_complete(task_id) in tests/unit/test_services.py
  - Mock storage, verify update() is called
  - Test raises TaskNotFoundError if ID not found

### GREEN Phase (Implementation)

- [X] [US3-006] [GREEN] Implement TaskService.mark_complete(task_id: int) in src/core/services.py
  - Call storage.get(task_id)
  - If None, raise TaskNotFoundError
  - Set task.completed = True
  - Call storage.update(task)
  - Return updated task
- [X] [US3-007] [GREEN] Implement TaskService.mark_incomplete(task_id: int) in src/core/services.py
  - Similar to mark_complete, but set completed = False
- [X] [US3-008] [GREEN] Implement `done` command in src/cli/commands/basic.py
  - Accept task_id as argument
  - Call TaskService.mark_complete(task_id)
  - Display success message (FR-009)
  - Handle TaskNotFoundError, display error (FR-010)
- [X] [US3-009] [GREEN] Implement `undone` command in src/cli/commands/basic.py
  - Accept task_id as argument
  - Call TaskService.mark_incomplete(task_id)
  - Display success message
- [X] [US3-010] [GREEN] Register `done` and `undone` commands in src/cli/main.py

### REFACTOR Phase

- [X] [US3-011] [REFACTOR] Add visual distinction test in tests/integration/test_table_rendering.py
  - Verify completed tasks show ✓ (green) (FR-036, SC-015)
  - Verify incomplete tasks show ☐ (FR-037)
- [X] [US3-012] [REFACTOR] Update render_task_table() to use STATUS_INDICATORS
- [X] [US3-013] [REFACTOR] Run all US3 tests, ensure 100% pass rate

**Acceptance**: SC-001 (partial), SC-015, all US3 acceptance scenarios pass, users can mark tasks complete/incomplete.

---

## Phase 5: User Story 4 - Update Task Details (Priority: P4)

**User Story**: As a user, I want to edit task titles and descriptions so I can fix typos or add more details as I learn more about the task.

**Acceptance Scenarios**: spec.md:84-87

### RED Phase (Tests First)

- [X] [US4-001] [RED] Write integration test for `update` command with title in tests/integration/test_cli_commands.py
  - Add task "Buy milk", update to "Buy milk and eggs"
  - Verify title changes
- [X] [US4-002] [RED] Write integration test for `update` command adding description
  - Add task without description, update with -d "From the organic store"
  - Verify description is added
- [X] [US4-003] [RED] Write integration test for `update` with invalid task ID
  - Run `todo update 999 --title "New title"`
  - Verify error message is displayed
- [X] [US4-004] [RED] Write integration test for `update` with empty title
  - Run `todo update 1 --title ""`
  - Verify error message, task remains unchanged
- [X] [US4-005] [RED] Write unit test for TaskService.update_task() in tests/unit/test_services.py

### GREEN Phase (Implementation)

- [X] [US4-006] [GREEN] Implement TaskService.update_task(task_id, title=None, description=None, **kwargs) in src/core/services.py
  - Get task by ID (raise TaskNotFoundError if not found)
  - Update provided fields
  - Validate title if provided (not empty)
  - Call storage.update(task)
  - Return updated task
- [X] [US4-007] [GREEN] Implement `update` command in src/cli/commands/basic.py
  - Accept task_id as argument
  - Accept --title, --description options
  - Call TaskService.update_task()
  - Display success message
  - Handle errors (FR-010)
- [X] [US4-008] [GREEN] Register `update` command in src/cli/main.py

### REFACTOR Phase

- [X] [US4-009] [REFACTOR] Add validation for title length (1-200 chars) in TaskService.update_task()
- [X] [US4-010] [REFACTOR] Add validation for description length (max 500 chars)
- [X] [US4-011] [REFACTOR] Run all US4 tests, ensure 100% pass rate

**Acceptance**: SC-001 (partial), all US4 acceptance scenarios pass, users can update task titles and descriptions.

---

## Phase 6: User Story 5 - Delete Unwanted Tasks (Priority: P5)

**User Story**: As a user, I want to delete tasks I no longer need so I can keep my list focused and uncluttered.

**Acceptance Scenarios**: spec.md:101-104

### RED Phase (Tests First)

- [X] [US5-001] [RED] Write integration test for `delete` command in tests/integration/test_cli_commands.py
  - Add task, run `todo delete 1`
  - Verify task is removed from list
- [X] [US5-002] [RED] Write integration test for `delete` with invalid ID
  - Run `todo delete 999`
  - Verify error message is displayed
- [X] [US5-003] [RED] Write integration test for `delete` affecting only target task
  - Add 3 tasks, delete task 2
  - Verify tasks 1 and 3 remain
- [X] [US5-004] [RED] Write integration test for empty list after deleting all tasks
  - Add and delete all tasks
  - Verify "no tasks" message when listing
- [X] [US5-005] [RED] Write unit test for TaskService.delete_task(task_id) in tests/unit/test_services.py

### GREEN Phase (Implementation)

- [X] [US5-006] [GREEN] Implement TaskService.delete_task(task_id: int) in src/core/services.py
  - Call storage.delete(task_id)
  - Return True if deleted, False if not found
- [X] [US5-007] [GREEN] Implement `delete` command in src/cli/commands/basic.py
  - Accept task_id as argument
  - Call TaskService.delete_task(task_id)
  - Display success message if deleted
  - Display error if task not found
- [X] [US5-008] [GREEN] Register `delete` command in src/cli/main.py

### REFACTOR Phase

- [ ] [US5-009] [REFACTOR] Add confirmation prompt to `delete` command (optional UX improvement)
  - Use Click.confirm() to ask "Are you sure?"
- [X] [US5-010] [REFACTOR] Verify ID is never reused after deletion (FR-002, clarification)
  - Add test: delete task 3, next created task gets ID 4 (not 3)
- [X] [US5-011] [REFACTOR] Run all US5 tests, ensure 100% pass rate

**Acceptance**: SC-001 (complete - all basic operations work), all US5 acceptance scenarios pass, users can delete tasks.

---

## Phase 7: User Story 6 - Assign Priorities and Tags (Priority: P6)

**User Story**: As a user, I want to assign priority levels (high/medium/low) and tags/categories (work/home/personal) to my tasks so I can organize and focus on what matters most.

**Acceptance Scenarios**: spec.md:120-123

### RED Phase (Tests First)

- [X] [US6-001] [RED] Write integration test for `add` command with priority in tests/integration/test_cli_commands.py
  - Test: `todo add "Complete proposal" -p high`
  - Verify task has priority=Priority.HIGH
- [X] [US6-002] [RED] Write integration test for `add` command with tags
  - Test: `todo add "Review code" --tags "work,urgent"`
  - Verify task.tags = ["work", "urgent"]
- [X] [US6-003] [RED] Write integration test for visual priority indicators in table
  - Add tasks with different priorities
  - Verify [!] HIGH (red), [-] MEDIUM (yellow), [v] LOW (blue) appear correctly (FR-038-040, SC-006)
- [X] [US6-004] [RED] Write integration test for tag display with multi-word tags
  - Test: `todo add "Meeting" --tags 'work,high priority'`
  - Verify tags = ["work", "high priority"]
- [X] [US6-005] [RED] Write unit test for parse_tags() function in tests/unit/test_validators.py
  - Test comma-separated parsing
  - Test quote handling for multi-word tags (FR-016 clarified)

### GREEN Phase (Implementation)

- [X] [US6-006] [GREEN] Create src/core/validators.py with parse_tags(tags_input: str) function
  - Use simple split() for comma-separated parsing
  - Return List[str]
- [X] [US6-007] [GREEN] Update TaskService.create_task() to accept priority and tags parameters
- [X] [US6-008] [GREEN] Update `add` command in src/cli/commands/basic.py
  - Add --priority/-p option with Click.Choice(['high', 'medium', 'low'])
  - Add --tags option
  - Parse tags using parse_tags()
  - Convert priority string to Priority enum
  - Pass to TaskService.create_task()
- [X] [US6-009] [GREEN] Update render_task_table() in src/cli/rendering/table.py
  - Priority and Tags columns already implemented
  - PRIORITY_INDICATORS already defined in colors.py
- [X] [US6-010] [GREEN] Update `update` command to support --priority and --tags options
  - Updated TaskService.update_task() to accept priority and tags parameters
  - Updated update CLI command with --priority/-p and --tags options
  - Updated success message to show priority and tags

### REFACTOR Phase

- [X] [US6-011] [REFACTOR] Add color rendering for priority indicators
  - HIGH: red text (FR-038)
  - MEDIUM: yellow text (FR-039)
  - LOW: blue text (FR-040)
  - Already implemented in colors.py
- [ ] [US6-012] [REFACTOR] Add tag display tests in tests/integration/test_table_rendering.py
  - Test tags show with brackets and space separation (SC-006, FR-022)
- [X] [US6-013] [REFACTOR] Run all US6 tests, ensure 100% pass rate

**Acceptance**: SC-006, SC-015, all US6 acceptance scenarios pass, users can assign priorities and tags.

---

## Phase 8: User Story 7 - Search Tasks (Priority: P7)

**User Story**: As a user, I want to search for tasks by keyword so I can quickly find specific tasks in a large list.

**Acceptance Scenarios**: spec.md:137-140

### RED Phase (Tests First)

- [X] [US7-001] [RED] Write integration test for `search` command in tests/integration/test_cli_commands.py
  - Add 10 tasks with varied titles
  - Search for "meeting"
  - Verify only matching tasks are displayed
- [X] [US7-002] [RED] Write integration test for search matching descriptions
  - Add task with keyword in description
  - Search for keyword
  - Verify task is found (FR-017)
- [X] [US7-003] [RED] Write integration test for search with no results
  - Search for non-existent keyword
  - Verify "no results found" message
- [X] [US7-004] [RED] Write integration test for search with empty input
  - Run `todo search ""`
  - Verify error message requiring keyword (FR-017 clarified)
- [X] [US7-005] [RED] Write unit tests for TaskService.search_tasks(query) in tests/unit/test_search_filter.py
  - Test case-insensitive matching (FR-017)
  - Test substring matching in title and description
  - Added 6 comprehensive unit tests (TestSearchTasks class)

### GREEN Phase (Implementation)

- [X] [US7-006] [GREEN] Implement TaskService.search_tasks(query: str) in src/core/services.py
  - Validate query is not empty, raise ValueError if empty
  - Get all tasks from storage
  - Filter: query.lower() in title.lower() or query.lower() in description.lower()
  - Return matching tasks (research.md:636-644)
- [X] [US7-007] [GREEN] Create src/cli/commands/intermediate.py with `search` command
  - Accept query as argument
  - Call TaskService.search_tasks(query)
  - Display results using render_task_table()
  - Display "no results" if empty
  - Handle ValueError for empty query
- [X] [US7-008] [GREEN] Register `search` command in src/cli/main.py
- [X] [US7-009] [GREEN] Update tests/conftest.py fixture to share storage between basic and intermediate modules

### REFACTOR Phase

- [ ] [US7-010] [REFACTOR] Add performance test in tests/unit/test_search_filter.py
  - Create 1000 tasks, search
  - Verify completes in <2 seconds (SC-007, NFR-002)
- [X] [US7-011] [REFACTOR] Run all US7 tests, ensure 100% pass rate
  - All 11 tests passing (6 unit + 5 integration)
  - Added to full test suite: 157 total tests passing

**Acceptance**: SC-007, all US7 acceptance scenarios pass, search is fast and accurate.

---

## Phase 9: User Story 8 - Filter Tasks (Priority: P8)

**User Story**: As a user, I want to filter tasks by status (complete/incomplete), priority, tags, or due date so I can focus on specific subsets of my tasks.

**Acceptance Scenarios**: spec.md:153-157

### RED Phase (Tests First)

- [X] [US8-001] [RED] Write integration test for `filter` command by priority in tests/integration/test_cli_commands.py
  - Add tasks with varied priorities
  - Run `todo filter --priority high`
  - Verify only high-priority tasks shown
- [X] [US8-002] [RED] Write integration test for `filter` by status (completed)
  - Add tasks and mark some complete
  - Run `todo filter --status completed`
  - Verify only completed tasks shown
- [X] [US8-003] [RED] Write integration test for `filter` by status (incomplete)
  - Add tasks and mark some complete
  - Run `todo filter --status incomplete`
  - Verify only incomplete tasks shown
- [X] [US8-004] [RED] Write integration test for `filter` by tag
  - Add tasks with various tags
  - Run `todo filter --tag work`
  - Verify only tasks with "work" tag shown
- [X] [US8-005] [RED] Write integration test for multiple filters (FR-019, SC-008)
  - Run `todo filter --priority high --status incomplete`
  - Verify only tasks matching ALL criteria shown (AND logic)
- [X] [US8-006] [RED] Write integration test for filter with no results (FR-020)
  - Apply filter with no matches
  - Verify friendly "no tasks match filters" message
- [X] [US8-007] [RED] Write unit tests for TaskService.filter_tasks() in tests/unit/test_search_filter.py
  - Added 7 comprehensive unit tests (TestFilterTasks class)
  - Test filter by priority, status (completed/incomplete), tag
  - Test combined criteria (AND logic)
  - Test empty results, no criteria error

### GREEN Phase (Implementation)

- [X] [US8-008] [GREEN] Implement TaskService.filter_tasks(priority=None, completed=None, tag=None) in src/core/services.py
  - Validate at least one filter criterion provided
  - Get all tasks from storage
  - Apply priority filter if provided (task.priority == priority)
  - Apply completed filter if provided (task.completed == completed)
  - Apply tag filter if provided (tag in task.tags)
  - Return filtered tasks using AND logic (FR-019)
- [X] [US8-009] [GREEN] Implement `filter` command in src/cli/commands/intermediate.py
  - Add --status/-s option with Click.Choice(['completed', 'incomplete', 'all'])
  - Add --priority/-p option with Click.Choice(['high', 'medium', 'low'])
  - Add --tag/-t option
  - Call TaskService.filter_tasks()
  - Display results using render_task_table()
  - Display friendly "no results" message with active filters shown
- [X] [US8-010] [GREEN] Register `filter` command in src/cli/main.py

### REFACTOR Phase

- [X] [US8-011] [REFACTOR] Run all US8 tests, ensure 100% pass rate
  - All 13 tests passing (7 unit + 6 integration)
  - Full test suite: 157 total tests passing
  - Code coverage: 83%
  - mypy: 0 errors in US8 implementation

**Acceptance**: SC-008, all US8 acceptance scenarios pass, filtering works with multiple criteria.

---

## Phase 10: User Story 9 - Sort Tasks (Priority: P9)

**User Story**: As a user, I want to sort tasks by due date, priority, created date, or alphabetically so I can view my tasks in the most useful order for my current context.

**Acceptance Scenarios**: spec.md:170-174

### RED Phase (Tests First)

- [X] [US9-001] [RED] Write integration test for `sort` by priority in tests/integration/test_cli_commands.py
  - Add tasks with varied priorities
  - Run `todo sort --by priority`
  - Verify order: high → medium → low (descending default)
- [X] [US9-002] [RED] Write integration test for `sort` by title alphabetically
  - Add tasks with varied titles
  - Run `todo sort --by title --order asc`
  - Verify A-Z order
- [X] [US9-003] [RED] Write integration test for `sort` by created date
  - Add tasks over time
  - Run `todo sort --by created --order asc`
  - Verify oldest first (ascending)
- [X] [US9-004] [RED] Write integration test for `sort` with ascending order
  - Add tasks with different priorities
  - Run `todo sort --by priority --order asc`
  - Verify order: low → medium → high
- [X] [US9-005] [RED] Write integration test for `sort` with descending order
  - Add tasks with different priorities
  - Run `todo sort --by priority --order desc`
  - Verify order: high → medium → low
- [X] [US9-006] [RED] Write integration test for `sort` with empty task list
  - Run `todo sort --by priority` with no tasks
  - Verify friendly "no tasks" message
- [X] [US9-007] [RED] Write unit tests for TaskService.sort_tasks(by) in tests/unit/test_search_filter.py
  - Added 7 comprehensive unit tests (TestSortTasks class)
  - Test sort by priority (ascending/descending)
  - Test sort by title (alphabetical)
  - Test sort by created date (both directions)
  - Test empty list and invalid field error

### GREEN Phase (Implementation)

- [X] [US9-008] [GREEN] Implement TaskService.sort_tasks(by: str, ascending=True) in src/core/services.py
  - Validate sort field (priority, title, created, due_date)
  - Get all tasks from storage
  - Sort by specified field with correct ordering
  - Handle None values for due_date (place at end)
  - Return sorted tasks
- [X] [US9-009] [GREEN] Implement `sort` command in src/cli/commands/intermediate.py
  - Add --by/-b option with Click.Choice(['priority', 'title', 'created', 'due_date'])
  - Add --order/-o option with Click.Choice(['asc', 'desc']) default='desc'
  - Call TaskService.sort_tasks()
  - Display results using render_task_table()
  - Display friendly "no tasks" message when empty
- [X] [US9-010] [GREEN] Register `sort` command in src/cli/main.py

### REFACTOR Phase

- [ ] [US9-011] [REFACTOR] Add test for sorting with null due dates
  - Tasks without due dates should appear at end when sorting by due_date
- [X] [US9-012] [REFACTOR] Run all US9 tests, ensure 100% pass rate
  - All 13 tests passing (7 unit + 6 integration)
  - Full test suite: 170 total tests passing
  - Code coverage: 82%
  - mypy: 0 errors

**Acceptance**: SC-009, all US9 acceptance scenarios pass, sorting works for all criteria.

---

## Phase 11: User Story 10 - Recurring Tasks (Priority: P10)

**User Story**: As a user, I want to create recurring tasks (daily, weekly, monthly) that automatically reschedule after completion so I don't have to manually recreate repetitive tasks.

**Acceptance Scenarios**: spec.md:190-194

### RED Phase (Tests First)

- [X] [US10-001] [RED] Write integration test for daily recurring task in tests/integration/test_cli_commands.py
  - Create task with `--recurrence daily`
  - Verify task has recurrence=DAILY
- [X] [US10-002] [RED] Write integration test for weekly recurring task
  - Create task with `--recurrence weekly`
  - Verify task has recurrence=WEEKLY
- [X] [US10-003] [RED] Write integration test for monthly recurring task
  - Create task with `--recurrence monthly`
  - Verify task has recurrence=MONTHLY
- [X] [US10-004] [RED] Write integration test for completing recurring task creates new instance
  - Create recurring task with due date
  - Mark complete
  - Verify new task is created with next due date
- [X] [US10-005] [RED] Write unit tests for calculate_next_occurrence() in tests/unit/test_recurring.py
  - Test DAILY: Jan 1 → Jan 2 (preserves time)
  - Test WEEKLY: Jan 1 → Jan 8
  - Test MONTHLY: Jan 15 → Feb 15
  - Test edge case: Jan 31 → Feb 28 (non-leap year)
  - Test edge case: Jan 31, 2024 → Feb 29, 2024 (leap year)
  - Test NONE recurrence raises ValueError
  - Test None due_date raises ValueError
  - Test year boundary: Dec 15 → Jan 15 (monthly)
  - Test year boundary: Dec 29 → Jan 5 (weekly)
  - Added 10 comprehensive unit tests (TestCalculateNextOccurrence class)

### GREEN Phase (Implementation)

- [X] [US10-006] [GREEN] Create src/core/recurring.py with calculate_next_occurrence() function
  - Implemented without dateutil (pure Python for simplicity)
  - Uses datetime.timedelta for DAILY and WEEKLY
  - Custom _add_months() for MONTHLY handling month-end edge cases
  - Returns next occurrence datetime preserving time component
- [X] [US10-007] [GREEN] Update TaskService.mark_complete() to handle recurring tasks
  - After setting completed=True
  - If task.recurrence != Recurrence.NONE and task.due_date is set:
    - Calculate next_due_date = calculate_next_occurrence(task.due_date, task.recurrence)
    - Create new task with same attributes and new due_date
    - Call storage.create(new_task)
- [X] [US10-008] [GREEN] Update `add` command to accept --recurrence option
  - Added -r/--recurrence option with Click.Choice(['none', 'daily', 'weekly', 'monthly'])
  - Default: 'none'
  - Convert to Recurrence enum and pass to TaskService.create_task()
  - Display recurrence in success message when not NONE
- [X] [US10-009] [GREEN] Update TaskService.create_task() to accept recurrence parameter
  - Added optional recurrence parameter (default: Recurrence.NONE)
  - Pass to Task model constructor

### REFACTOR Phase

- [X] [US10-010] [REFACTOR] Edge case tests included in unit tests
  - Month-end dates (Jan 31 → Feb 28) - PASSED
  - Leap years (Jan 31, 2024 → Feb 29, 2024) - PASSED
  - Year boundaries (Dec → Jan) - PASSED
- [X] [US10-011] [REFACTOR] Run all US10 tests, ensure 100% pass rate
  - All 16 tests passing (10 unit + 6 integration)
  - Full test suite: 187 total tests passing
  - Code coverage: 82%
  - mypy: 0 errors

**Acceptance**: SC-010, SC-013, all US10 acceptance scenarios pass, recurring tasks auto-create correctly.

---

## Phase 12: User Story 11 - Due Dates and Overdue Filtering (Priority: P11)

**User Story**: As a user, I want to set due dates and filter overdue tasks so I don't miss important deadlines.

**Acceptance Scenarios**: spec.md:207-211

### RED Phase (Tests First)

- [X] [US11-001] [RED] Write integration test for `add` with due date in tests/integration/test_cli_commands.py
  - Test: `todo add "Submit report" --due "2025-12-31"`
  - Verify due_date is stored correctly (FR-025)
- [X] [US11-002] [RED] Write integration test for `add` with due date and time
  - Test: `todo add "Meeting" --due "2025-12-31 14:30"`
  - Verify date and time are stored correctly
- [X] [US11-003] [RED] Write integration test for `update` with due date
  - Test: `todo update 1 --due "2025-12-25"`
  - Verify due_date is updated
- [X] [US11-004] [RED] Write integration test for task list showing due date
  - Add task with due date
  - Verify due date appears in list output
- [X] [US11-005] [RED] Write integration test for invalid due date format
  - Test: `todo add "Bad" --due "not-a-date"`
  - Verify error is raised
- [X] [US11-006] [RED] Write integration test for overdue filter
  - Add overdue task and future task
  - Run `todo filter --overdue`
  - Verify only overdue task is shown
- [X] [US11-007] [RED] Write integration test for overdue filter combined with priority
  - Add multiple overdue tasks with different priorities
  - Run `todo filter --overdue --priority high`
  - Verify only high priority overdue task is shown
- [X] [US11-008] [RED] Write unit tests for overdue filtering in tests/unit/test_search_filter.py
  - Test filter_tasks(overdue=True) returns only overdue tasks
  - Test filter_tasks(overdue=False) returns non-overdue tasks
  - Test combined filters (overdue + priority)
  - Added 3 comprehensive unit tests (TestFilterOverdueTasks class)

### GREEN Phase (Implementation)

- [X] [US11-009] [GREEN] Add parse_due_date() function to src/core/validators.py
  - Supports YYYY-MM-DD format (date only)
  - Supports YYYY-MM-DD HH:MM format (date and time)
  - Returns datetime object
  - Raises ValueError for invalid formats
- [X] [US11-010] [GREEN] Update TaskService.create_task() to accept due_date parameter
  - Added optional due_date parameter
  - Pass to Task model constructor
- [X] [US11-011] [GREEN] Update `add` command to accept --due option
  - Parse due date using parse_due_date()
  - Display due date in success message
- [X] [US11-012] [GREEN] Update TaskService.update_task() to accept due_date parameter
  - Added optional due_date parameter
  - Update task.due_date when provided
- [X] [US11-013] [GREEN] Update `update` command to accept --due option
  - Parse due date using parse_due_date()
  - Display due date in success message
- [X] [US11-014] [GREEN] Update TaskService.filter_tasks() to accept overdue parameter
  - Added optional overdue parameter (True/False)
  - Filter by task.is_overdue() method
  - Combine with other filters using AND logic
- [X] [US11-015] [GREEN] Update `filter` command to accept --overdue flag
  - Added --overdue flag (is_flag=True)
  - Pass to filter_tasks() service method
  - Display overdue in filter header and no-results message

### REFACTOR Phase

- [X] [US11-016] [REFACTOR] Overdue highlighting already implemented in render_task_table()
  - Uses task.is_overdue() method
  - Overdue tasks displayed in red (COLORS["overdue"])
  - Due today tasks displayed in yellow bold (COLORS["due_today"])
- [X] [US11-017] [REFACTOR] Run all US11 tests, ensure 100% pass rate
  - All 11 tests passing (3 unit + 8 integration)
  - Full test suite: 206 total tests passing
  - Code coverage: 84%
  - mypy: 0 errors

**Note**: Reminder functionality (--reminder option and ReminderMonitor) deferred to Phase 2 as it requires background threading and is lower priority than core functionality.

**Acceptance**: SC-011 (partial - overdue highlighting), due dates and overdue filtering work correctly.

---

## Phase 13: Polish and Cross-Cutting Concerns

**Objective**: Refine UX, optimize performance, ensure compliance with all NFRs and success criteria.

### Visual and UX Polish

- [ ] [POLISH-001] Run visual tests for table rendering with 50+ tasks (SC-016)
  - Verify table remains readable (NFR-009)
  - Test scrolling behavior
- [ ] [POLISH-002] Test terminal capability detection (NFR-007, SC-017)
  - Test unicode terminals (╔═╗ box chars)
  - Test ASCII-only terminals (+---+ box chars)
  - Test color terminals
  - Test monochrome terminals
- [ ] [POLISH-003] Add task count display to `list` command
  - Show "X incomplete, Y complete" at bottom (NFR-011)
- [ ] [POLISH-004] Refine error messages for clarity (NFR-005, SC-004)
  - Review all ValidationError, TaskNotFoundError messages
  - Add suggested corrective actions
- [ ] [POLISH-005] Add data loss warning to welcome message (NFR-006)
  - Display "⚠️  Data is not persisted between sessions" on startup

### Performance Optimization

- [ ] [POLISH-006] Run performance benchmarks in tests/unit/test_services.py
  - Test CRUD operations with 100 tasks <1s (SC-002, NFR-001)
  - Test search/filter with 1000 tasks <2s (SC-007, NFR-002)
  - Test table rendering with 100 tasks <500ms (NFR-003)
- [ ] [POLISH-007] Optimize search algorithm if benchmarks fail
  - Consider caching or indexing (deferred to Phase 2 if needed)
- [ ] [POLISH-008] Optimize table rendering for large lists
  - Implement pagination if needed (deferred to Phase 2 if needed)

### Testing and Quality

- [x] [POLISH-009] Run full test suite, ensure >90% code coverage (plan.md:78-96)
  - pytest --cov=src --cov-report=term-missing
  - **COMPLETED**: 289 tests passing, 90% code coverage achieved
  - Added tests/unit/test_interactive.py (22 tests)
  - Added tests/integration/test_cli_errors.py (14 tests)
- [x] [POLISH-010] Run mypy on entire codebase, fix all type errors (plan.md:65)
  - mypy src/ --strict
  - **COMPLETED**: Success with no issues found in 20 source files
- [x] [POLISH-011] Run integration test for primary workflow (SC-003)
  - Add task → view list → mark complete in <30 seconds
  - **COMPLETED**: Added TestPrimaryWorkflow class with 4 tests
  - Primary workflow completes in ~0.03s (well under 30s requirement)
- [x] [POLISH-012] Test edge cases from spec.md Edge Cases section
  - **COMPLETED**: Added tests/unit/test_edge_cases.py (43 tests)
  - Very long titles (200 chars max) - verified truncation/error
  - Whitespace-only titles - verified error
  - Invalid task IDs (negative, letters, large numbers)
  - Special characters in titles/descriptions
  - Tags with spaces and special characters
  - Past due dates
  - Date parsing edge cases

### Documentation

- [x] [POLISH-013] Update README.md with complete installation and usage guide
  - **COMPLETED**: Added comprehensive command reference tables
  - Added visual indicators documentation
  - Added filter/sort command options tables
  - Architecture overview already present
- [~] [POLISH-014] Create CONTRIBUTING.md with development guidelines
  - **SKIPPED**: Individual project, not applicable
- [x] [POLISH-015] Implement --help for all commands (NFR-008)
  - **COMPLETED**: All commands have examples and descriptions
  - Fixed `\b` formatting in docstrings for proper Click help rendering
  - Verified: add, list, done, undone, update, delete, search, filter, sort
- [x] [POLISH-016] Add docstrings to all public functions and classes
  - **COMPLETED**: All public modules have comprehensive docstrings
  - models.py, validators.py, exceptions.py, services.py
  - storage/base.py, storage/memory.py
  - recurring.py, rendering/table.py, rendering/colors.py

### CI/CD and Deployment

- [ ] [POLISH-017] Verify GitHub Actions CI workflow runs successfully
  - Push to branch
  - Verify pytest, mypy, coverage all pass
- [ ] [POLISH-018] Create release checklist for v0.1.0
  - All tests pass
  - Code coverage >90%
  - No mypy errors
  - README complete
  - All success criteria met

### Final Validation

- [ ] [POLISH-019] Manual acceptance testing for all 11 user stories
  - Run through all acceptance scenarios from spec.md
  - Document any failures
- [ ] [POLISH-020] Validate all 17 Success Criteria (SC-001 to SC-017)
  - Create checklist, verify each one
- [ ] [POLISH-021] Validate all Functional Requirements (FR-001 to FR-043)
  - Create checklist, verify each one
- [ ] [POLISH-022] Validate all Non-Functional Requirements (NFR-001 to NFR-012)
  - Performance benchmarks
  - Usability testing
  - UX goals
- [ ] [POLISH-023] Create demo video or screenshots for README
  - Show table rendering
  - Show all features in action
- [ ] [POLISH-024] Final code review and refactoring
  - Remove debug code
  - Remove commented code
  - Ensure consistent naming
  - Ensure DRY principles

**Acceptance**: All success criteria met, all tests pass, code coverage >90%, ready for production use.

---

## Summary

**Total Tasks**: 210+ tasks organized into 13 phases
**User Stories**: 11 independent user stories (P1-P11)
**Test Coverage Target**: >90%
**Development Approach**: TDD (Red-Green-Refactor)

**Estimated Execution**:
- **Setup**: 1 hour
- **Foundational**: 4-6 hours
- **User Stories 1-5 (Basic)**: 8-12 hours
- **User Stories 6-9 (Intermediate)**: 8-12 hours
- **User Stories 10-11 (Advanced)**: 6-8 hours
- **Polish**: 4-6 hours
- **Total**: 30-45 hours for complete Phase 1 implementation

**Next Steps**:
1. Review and approve this task breakdown
2. Begin Phase 0 (Setup)
3. Execute foundational layer (Phase 1)
4. Implement user stories in priority order (P1 → P11)
5. Run final validation and polish

**Success Metrics**:
- ✅ All 11 user stories implemented and tested
- ✅ All 17 Success Criteria met
- ✅ Code coverage >90%
- ✅ No mypy errors
- ✅ CI/CD pipeline green
- ✅ Ready for Phase 2 evolution (web + database)