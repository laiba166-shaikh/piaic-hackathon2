# Quick Start: Phase 1 CLI Todo App

**Date**: 2025-12-10
**Branch**: 001-phase1-cli-todo
**Important**: Phase 1 uses in-memory storage - data is lost on exit

## Installation

### Prerequisites
- Python 3.12 or higher
- UV package manager (recommended)

### Install UV
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup
```bash
git clone https://github.com/your-username/hackathon2.git
cd hackathon2
git checkout 001-phase1-cli-todo
uv pip install -e .
python -m src.cli.main --help
```

## Basic Commands

### Add Tasks
```bash
# Simple task
todo add "Buy groceries"

# With description
todo add "Call dentist" -d "Schedule annual checkup"

# With priority and tags
todo add "Complete project proposal" -p high --tags "work,urgent"

# With due date (YYYY-MM-DD HH:MM)
todo add "Submit report" --due "2025-12-15 17:00"

# Recurring task
todo add "Team standup" --due "2025-12-11 09:00" --recurrence daily
```

### View Tasks
```bash
todo list                      # All tasks (newest first)
todo list --status incomplete  # Only incomplete
todo list --priority high      # High priority only
todo list --tag work           # Tagged "work"
```

### Update Tasks
```bash
todo update 1 --title "Buy groceries and milk"
todo update 1 -p high
todo update 1 --tags "personal,shopping"
```

### Mark Complete/Incomplete
```bash
todo done 1      # Mark complete (recurring → creates next)
todo undone 1    # Mark incomplete
```

### Delete Tasks
```bash
todo delete 1    # ID 1 is never reused (per spec)
```

### Search & Filter
```bash
todo search "meeting"                                    # Case-insensitive
todo filter --status incomplete --priority high --tag urgent  # Multi-filter
```

### Sort
```bash
todo sort --by due_date   # Soonest first (overdue at top)
todo sort --by priority   # High → Medium → Low
todo sort --by created    # Newest first (default)
todo sort --by title      # Alphabetical
```

## Features

### Priorities
- **HIGH**: ❗ (red) - `[!] H` in ASCII
- **MEDIUM**: ➖ (yellow) - `[-] M` in ASCII
- **LOW**: ⬇ (blue) - `[v] L` in ASCII

### Tags
Multi-word tags use quotes:
```bash
todo add "Review PR" --tags 'work,"code review","high priority"'
```

### Recurring Tasks
When marked complete, automatically creates next instance:
- **daily**: Tomorrow
- **weekly**: Next week (same day)
- **monthly**: Next month (same date, handles month-end)

### Due Dates & Reminders
```bash
todo add "Client call" --due "2025-12-15 14:00" --reminder 60
# Reminder 60 min before (while app runs)
```

**Visual Indicators**:
- ⚠️ **OVERDUE** (red) - past due
- **DUE TODAY** (yellow) - today
- Normal - upcoming or no due date

## Example Session

```bash
python -m src.cli.main

todo add "Buy groceries" -p medium --tags "personal,shopping"
todo add "Complete project proposal" -p high --tags "work,urgent"
todo add "Call dentist" -d "Schedule checkup" -p low

todo list
# ╔════╦════════╦══════════╦═══════════════════════════╦═════════════════╗
# ║ ID ║ Status ║ Priority ║ Title                     ║ Tags            ║
# ╠════╬════════╬══════════╬═══════════════════════════╬═════════════════╣
# ║  3 ║   ☐    ║  ⬇ LOW   ║ Call dentist              ║                 ║
# ║  2 ║   ☐    ║  ❗ HIGH  ║ Complete project proposal ║ [work] [urgent] ║
# ║  1 ║   ☐    ║  ➖ MED   ║ Buy groceries             ║ [personal] [...] ║
# ╚════╩════════╩══════════╩═══════════════════════════╩═════════════════╝

todo done 2
todo search "groceries"
todo delete 3
```

## Troubleshooting

### "Command not found: todo"
Use full path or create alias:
```bash
python -m src.cli.main add "Task"

# Or add to ~/.bashrc
alias todo="python -m src.cli.main"
```

### Unicode not displaying
Rich auto-detects and falls back to ASCII. Force UTF-8:
```bash
export PYTHONIOENCODING=utf-8
```

### Colors not working
Rich auto-detects. Force colors:
```bash
export FORCE_COLOR=1
```

## Testing

```bash
pytest                                    # Run all tests
pytest --cov=src --cov-report=term-missing  # With coverage
pytest tests/unit/test_models.py          # Specific test
mypy src/                                 # Type checking
```

## Important Notes

**Data Persistence**: Phase 1 is **in-memory only**. All tasks lost on exit (intentional).

**Next Phases**:
- Phase 2: Web app + PostgreSQL persistence
- Phase 3: AI chatbot
- Phase 4: Kubernetes
- Phase 5: Cloud deployment

See `ARCHITECTURE.md` for multi-phase evolution strategy.

---

**Quick Start Status**: ✅ READY FOR USE
**Support**: See plan.md for architecture details
