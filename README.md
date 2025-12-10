# Phase 1 CLI Todo App (Enhanced)

A professional command-line todo application with Basic, Intermediate, and Advanced features. Built with Python 3.12+, featuring excellent table-based visualization, priorities, tags, search, filtering, recurring tasks, and due date management.

## Features

### Basic Level
- ✅ Add, view, update, and delete tasks
- ✅ Mark tasks complete/incomplete
- ✅ Professional table-based visualization with unicode support

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
├── core/               # Business logic
│   ├── models.py       # Task, Priority, Recurrence
│   ├── services.py     # TaskService
│   ├── exceptions.py   # Custom exceptions
│   ├── validators.py   # Input validation
│   └── storage/        # Storage abstraction
│       ├── base.py     # ITaskStorage interface
│       └── memory.py   # MemoryStorage implementation
├── cli/                # CLI interface
│   ├── main.py         # CLI entry point
│   ├── commands/       # Click commands
│   └── rendering/      # Table rendering
└── config.py           # Configuration

tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
└── contract/           # Storage contract tests
```

## Architecture

This project demonstrates **clean architecture** principles with separation of concerns:

- **Core Layer**: Business logic independent of CLI
- **Storage Layer**: Abstract interface with strategy pattern for Phase 2 database migration
- **CLI Layer**: Click-based commands with Rich table rendering

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

⚠️ **Important**: Phase 1 uses **in-memory storage**. All tasks are lost when you exit the CLI. This is intentional for Phase 1. Database persistence will be added in Phase 2.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

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
