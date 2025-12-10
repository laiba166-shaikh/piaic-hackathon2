# Data Model: Phase 1 CLI Todo App

**Date**: 2025-12-10
**Branch**: 001-phase1-cli-todo
**Reference**: Extracted from spec.md requirements

## Core Entity: Task

Represents a single todo item with all Phase 1 attributes.

### Attributes

| Field | Type | Required | Default | Validation | Reference |
|-------|------|----------|---------|------------|-----------|
| `id` | `int` | Auto | - | Unique, sequential, never reused | FR-002, clarification |
| `title` | `str` | Yes | - | 1-200 chars, non-empty | FR-001 |
| `description` | `Optional[str]` | No | `None` | Max 500 chars | FR-001, clarified |
| `completed` | `bool` | No | `False` | - | FR-004 |
| `priority` | `Priority` | No | `MEDIUM` | Enum: HIGH/MEDIUM/LOW | FR-015 |
| `tags` | `List[str]` | No | `[]` | Comma-separated input | FR-016, clarified |
| `due_date` | `Optional[datetime]` | No | `None` | YYYY-MM-DD HH:MM | FR-025 |
| `recurrence` | `Recurrence` | No | `NONE` | NONE/DAILY/WEEKLY/MONTHLY | FR-023 |
| `reminder_minutes` | `Optional[int]` | No | `None` | >0, minutes before due | FR-028 |
| `created_at` | `datetime` | Auto | `now()` | - | Spec requirement |
| `updated_at` | `datetime` | Auto | `now()` | - | Spec requirement |

### Python Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class Task:
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Recurrence = Recurrence.NONE
    reminder_minutes: Optional[int] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title max 200 characters")
        if self.description and len(self.description) > 500:
            raise ValueError("Description max 500 characters")
        if self.reminder_minutes and self.reminder_minutes <= 0:
            raise ValueError("Reminder must be positive minutes")

    def is_overdue(self) -> bool:
        if not self.due_date or self.completed:
            return False
        return datetime.now() > self.due_date

    def is_due_today(self) -> bool:
        if not self.due_date or self.completed:
            return False
        return self.due_date.date() == datetime.now().date()
```

## State Machines

### Task Lifecycle

```
CREATED (incomplete) → mark_complete() → COMPLETED
                    ← mark_incomplete() ←
```

**Recurring Task Behavior** (FR-024, clarified):
- On `mark_complete()` for recurring task:
  1. Set current task `completed=True`
  2. Create NEW task with original attributes + next due date
  3. New task gets new ID (sequential counter continues)

### Due Date States

- **No Due Date**: `due_date=None` → Display `--:--`
- **Upcoming**: `due_date > now` and not today → Normal display
- **Due Today**: `due_date.date() == today` → Yellow highlight (FR-027)
- **Overdue**: `due_date < now` and not completed → Red + ⚠️ (FR-026)
- **Completed**: `completed=True` → No overdue check

## Visual Indicators (CLI Rendering)

### Priority Indicators (FR-021, FR-038-040)

```python
PRIORITY_INDICATORS = {
    Priority.HIGH: ("❗", "red"),      # [!] H in ASCII fallback
    Priority.MEDIUM: ("➖", "yellow"),  # [-] M in ASCII fallback
    Priority.LOW: ("⬇", "blue"),       # [v] L in ASCII fallback
}
```

### Status Indicators (FR-036-037)

- Completed: `✓` or `[✓]` (green)
- Incomplete: `☐` or `[ ]`

### Tags Display (FR-022, FR-043)

- Format: `[work] [urgent] [high priority]`
- Space-separated with brackets

## Validation Rules

| Rule | Requirement | Implementation |
|------|-------------|----------------|
| Title required | FR-007 | `__post_init__` raises ValueError |
| Title 1-200 chars | FR-001 | `__post_init__` validates |
| Description max 500 | FR-001 (clarified) | `__post_init__` validates |
| Priority enum | FR-015 | Type hint enforces |
| Tags list | FR-016 | Parsed by CLI (`parse_tags()`) |
| Recurrence enum | FR-023 | Type hint enforces |
| Reminder positive | FR-028 | `__post_init__` validates |

## Recurring Task Algorithm

```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

def calculate_next_occurrence(due_date: datetime, recurrence: Recurrence) -> datetime:
    if recurrence == Recurrence.DAILY:
        return rrule(DAILY, dtstart=due_date, count=2)[1]
    elif recurrence == Recurrence.WEEKLY:
        return rrule(WEEKLY, dtstart=due_date, count=2)[1]
    elif recurrence == Recurrence.MONTHLY:
        return rrule(MONTHLY, dtstart=due_date, count=2)[1]
    else:
        raise ValueError("Cannot calculate for NONE recurrence")
```

**Edge Cases** (handled by dateutil):
- Jan 31 → Feb 28 (or 29)
- DST transitions
- Leap years

## Phase Evolution

**Phase 1**: No relationships (single-user)
**Phase 2**: Add `user_id: int` foreign key for multi-user support

---

**Data Model Status**: ✅ COMPLETE
**Testing**: See `tests/unit/test_models.py` for validation tests
