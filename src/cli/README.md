# Phase 1 CLI Todo App (Enhanced)

A professional command-line todo application with Basic, Intermediate, and Advanced features. Built with Python 3.12+, featuring excellent table-based visualization, priorities, tags, search, filtering, recurring tasks, and due date management.

## Features

### Basic Level
- ✅ Add, view, update, and delete tasks
- ✅ Mark tasks complete/incomplete
- ✅ Professional table-based visualization with unicode support
- ✅ Interactive shell mode for persistent session

### Intermediate Level
- ✅ Assign priorities (High/Medium/Low) with visual indicators
- ✅ Tag tasks for organization
- ✅ Search tasks by keyword
- ✅ Filter by status, priority, and tags
- ✅ Sort by due date, priority, created date, or title

### Advanced Level
- ✅ Recurring tasks (daily, weekly, monthly)
- ✅ Due dates with time support
- ✅ Overdue task highlighting
- ✅ Reminder notifications

## Quick Start

### Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip

### Installation

```bash
# Clone repository
git clone https://github.com/laiba166-shaikh/piaic-hackathon2.git
cd piaic-hackathon2

# Checkout feature branch
git checkout 001-phase1-cli-todo

# Install UV (if not already installed)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies
uv pip install -e .

# Verify installation
todo --help
```

### Basic Usage

#### Interactive Mode (Recommended)

Interactive mode keeps tasks in memory during your session, making the in-memory storage practical to use:

```bash
# Start interactive mode
todo

# Then execute commands without the "todo" prefix:
todo> add "Buy groceries"
Task created successfully! ID: 1

todo> add "Call dentist" -d "Schedule checkup"
Task created successfully! ID: 2

todo> list
# Shows all tasks from this session

todo> help
# See all available commands

todo> exit
# Exit interactive mode
```

#### One-Shot Commands

You can also run individual commands (each runs in a separate process):

```bash
# Add a task
todo add "Buy groceries"

# Add task with details
todo add "Complete proposal" -p high --tags "work,urgent" --due "2025-12-15 17:00"

# View all tasks
todo list

# Mark task complete
todo done 1

# Search tasks
todo search "meeting"

# Filter tasks
todo filter --status incomplete --priority high

# Delete task
todo delete 1
```

**Note**: With one-shot commands, each command runs in a separate process, so tasks don't persist between commands in Phase 1 (in-memory storage). Use interactive mode for a better experience.

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run type checking
mypy src/

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

### Project Structure

```
src/
├── cli/                    # Phase 1 CLI application
│   ├── main.py             # CLI entry point
│   ├── commands/           # Click commands (basic, intermediate)
│   ├── rendering/          # Table rendering (colors, table)
│   ├── logics/             # Business logic (CLI-local)
│   │   ├── models.py       # Task, Priority, Recurrence
│   │   ├── services.py     # TaskService
│   │   ├── exceptions.py   # Custom exceptions
│   │   ├── validators.py   # Input validation
│   │   ├── recurring.py    # Recurring task utilities
│   │   └── storage/        # Storage abstraction
│   │       ├── base.py     # ITaskStorage interface
│   │       └── memory.py   # MemoryStorage implementation
│   └── tests/              # All CLI tests
│       ├── unit/
│       ├── integration/
│       └── contract/
├── core/                   # Phase 2+ (web)
│   ├── backend/            # FastAPI backend
│   └── frontend/           # Next.js frontend
└── config.py               # Shared configuration
```

## Architecture

This project demonstrates **clean architecture** principles with separation of concerns:

- **Logics Layer** (`cli/logics/`): Business logic, domain models, and storage — fully independent of the CLI interface
- **Storage Layer**: Abstract interface (`ITaskStorage`) with strategy pattern, enabling Phase 2 database migration
- **CLI Layer**: Click-based commands with Rich table rendering, depends only on the logics layer

Built to evolve across 5 phases:
- **Phase 1**: CLI with in-memory storage (this phase)
- **Phase 2**: Web interface with PostgreSQL
- **Phase 3**: AI chatbot integration
- **Phase 4**: Kubernetes deployment
- **Phase 5**: Cloud deployment

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v
```

**Coverage Target**: >90%

## Data Persistence

⚠️ **Important**: Phase 1 uses **in-memory storage**.

- **Interactive Mode**: Tasks persist during your session. When you exit, all tasks are lost.
- **One-Shot Commands**: Each command runs in a separate process, so tasks don't persist between commands.

**Recommendation**: Use interactive mode (`todo` with no arguments) for the best Phase 1 experience.

Database persistence will be added in Phase 2.

## Command Reference

### Task Management

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create a new task | `todo add "Buy milk" -p high --tags "shopping"` |
| `list` | View all tasks | `todo list` |
| `done` | Mark task complete | `todo done 1` |
| `undone` | Mark task incomplete | `todo undone 1` |
| `update` | Modify task details | `todo update 1 --title "New title" -p low` |
| `delete` | Remove a task | `todo delete 1` |

### Search, Filter & Sort

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Find tasks by keyword | `todo search "meeting"` |
| `filter` | Filter by criteria | `todo filter --priority high --status incomplete` |
| `sort` | Sort tasks | `todo sort --by priority --order desc` |

### Add Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `-d, --description` | Task description | `-d "Call about appointment"` |
| `-p, --priority` | Priority level (high/medium/low) | `-p high` |
| `--tags` | Comma-separated tags | `--tags "work,urgent"` |
| `--due` | Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM) | `--due "2025-12-31 14:00"` |
| `-r, --recurrence` | Recurrence pattern (daily/weekly/monthly) | `-r weekly` |

### Filter Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `-p, --priority` | Filter by priority | `--priority high` |
| `-s, --status` | Filter by status (completed/incomplete/all) | `--status incomplete` |
| `-t, --tag` | Filter by tag | `--tag work` |
| `--overdue` | Show only overdue tasks | `--overdue` |

### Sort Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `-b, --by` | Sort field (priority/title/created/due_date) | `--by priority` |
| `-o, --order` | Sort order (asc/desc) | `--order asc` |

## Visual Indicators

### Priority Icons
- **HIGH**: `[!]` (red) - Urgent tasks
- **MEDIUM**: `[-]` (yellow) - Normal priority
- **LOW**: `[v]` (blue) - Low priority

### Status Icons
- `[X]` - Completed task
- `[ ]` - Incomplete task

### Due Date Indicators
- **OVERDUE** (red) - Past due date
- **DUE TODAY** (yellow) - Due today
- Normal date display - Future dates

## License

MIT

## Documentation

- [Feature Specification](specs/001-phase1-cli-todo/spec.md)
- [Implementation Plan](specs/001-phase1-cli-todo/plan.md)
- [Task Breakdown](specs/001-phase1-cli-todo/tasks.md)
- [Quick Start Guide](specs/001-phase1-cli-todo/quickstart.md)
- [Architecture Decisions](history/adr/)

## Phase Evolution

For multi-phase architecture strategy, see [ARCHITECTURE.md](ARCHITECTURE.md).
