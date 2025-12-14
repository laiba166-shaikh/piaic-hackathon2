# ADR-003: Date/Time Handling for Recurring Tasks

> **Scope**: Date/time library selection for parsing, recurrence calculations, and timezone handling. Critical for implementing recurring tasks (FR-023, FR-024) and due date features (FR-025-030).

- **Status:** Accepted
- **Date:** 2025-12-10
- **Feature:** 001-phase1-cli-todo
- **Context:** Spec requires recurring tasks (daily, weekly, monthly) with automatic next-instance creation (FR-024), due date parsing (YYYY-MM-DD HH:MM format per FR-025), and overdue detection (FR-026). Need library with robust recurrence support to handle edge cases (month-end dates, DST transitions, leap years). Must integrate with storage layer (affects Task.due_date field type).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Affects recurring task implementation (core feature), date parsing across CLI, storage schema for due_date field, Phase 2+ web API date handling
     2) Alternatives: YES - Arrow, stdlib datetime, manual recurrence all viable with different complexity/capability tradeoffs
     3) Scope: YES - Cross-cutting: CLI parsing, TaskService business logic, storage, future web API, edge case handling
-->

## Decision

**Use python-dateutil for all date/time operations, including parsing and recurrence calculations.**

**Components**:
- **Parsing**: `dateutil.parser.parse()` for flexible "YYYY-MM-DD HH:MM" format
- **Recurrence**: `dateutil.rrule` module implementing RFC 5545 (iCalendar) recurrence rules
- **Date Arithmetic**: `dateutil.relativedelta` for month-end edge cases
- **Storage**: `datetime.datetime` objects (stdlib) stored in Task entity

**Pattern**: Use industry-standard RFC 5545 recurrence rules (same as Google Calendar, Outlook)

## Consequences

### Positive

- ✅ **Built-in Recurrence**: `rrule` module implements DAILY, WEEKLY, MONTHLY patterns per RFC 5545 spec
- ✅ **Edge Case Handling**: Automatically handles month-end dates (Jan 31 → Feb 28/29), DST transitions, leap years
- ✅ **Near-Stdlib**: Widely used, de-facto standard for date operations in Python (pip install count: 100M+/month)
- ✅ **Parsing Flexibility**: `parse()` handles multiple formats (defensive if user types "Dec 15, 2025" vs strict "2025-12-15")
- ✅ **Timezone Support**: Excellent timezone handling for Phase 2+ (user timezones, UTC storage)
- ✅ **Phase 2+ Compatible**: FastAPI, SQLModel, Neon all integrate seamlessly with `datetime` + `python-dateutil`

### Negative

- ⚠️ **External Dependency**: Not stdlib (though near-universal in Python ecosystem)
- ⚠️ **Learning Curve**: `rrule` API moderately complex (requires understanding RFC 5545 concepts)
- ⚠️ **Overkill for Phase 1**: Phase 1 is in-memory, no timezone complexity - simpler solution might suffice
- ⚠️ **Import Size**: ~500KB package (larger than Arrow's ~300KB)

**Mitigation**: Complexity justified by spec requirement for recurring tasks. RFC 5545 is industry standard (same as Google Calendar) - reusable knowledge. Edge case handling (month-end, DST) would require 100+ lines manual code.

## Alternatives Considered

### Alternative A: Arrow (Humanized Dates Library)

**Approach**: Use Arrow for all date operations

```python
import arrow

# Parsing
due_date = arrow.get("2025-12-15 14:00")

# Recurrence (MANUAL - Arrow has no rrule)
if recurrence == "weekly":
    next_date = due_date.shift(weeks=1)
```

**Pros**:
- More intuitive API (`arrow.now()`, `shift(weeks=1)`)
- Smaller package (~300KB)
- Better error messages

**Cons**:
- **No built-in recurrence** - must implement DAILY, WEEKLY, MONTHLY manually
- **Month-end edge cases** - `shift(months=1)` on Jan 31 → ❌ Error vs dateutil → Feb 28/29
- **Manual testing required** - 50+ edge case tests vs dateutil's battle-tested rrule
- **Less adoption** - 10M pip installs/month vs dateutil's 100M

**Why Rejected**: Spec requires recurring tasks (FR-023, FR-024) - manual recurrence implementation violates DRY. Estimated 150+ lines of recurrence logic + edge case handling vs dateutil's single `rrule()` call. Month-end errors would be production bugs.

### Alternative B: Stdlib datetime + Manual Recurrence

**Approach**: Use only stdlib `datetime` module

```python
from datetime import datetime, timedelta

# Parsing (MANUAL - no flexible parser)
due_date = datetime.strptime("2025-12-15 14:00", "%Y-%m-%d %H:%M")

# Recurrence (MANUAL)
if recurrence == "daily":
    next_date = due_date + timedelta(days=1)
elif recurrence == "weekly":
    next_date = due_date + timedelta(weeks=1)
elif recurrence == "monthly":
    # COMPLEX - no timedelta(months=1)
    month = due_date.month + 1
    year = due_date.year
    if month > 12:
        month = 1
        year += 1
    # Handle day overflow (Jan 31 → Feb 31 invalid)
    # ... 20+ lines of edge case logic
```

**Pros**:
- Zero external dependencies
- Maximum control

**Cons**:
- **No flexible parsing** - `strptime` requires exact format, fails on variations
- **Manual recurrence** - 100+ lines for monthly recurrence with edge cases
- **Month-end bugs** - Easy to miss edge cases (Jan 31 → Feb 31 = crash)
- **No DST handling** - Requires manual timezone logic
- **Maintenance burden** - Team maintains date logic vs using battle-tested library

**Why Rejected**: Violates constitution principle of using well-vetted libraries. Estimated 150+ lines of manual date logic vs 10 lines with dateutil. High risk of edge-case bugs in production (month-end, leap year, DST).

### Alternative C: Pendulum (datetime Alternative)

**Approach**: Use Pendulum (modern datetime library)

**Pros**:
- More intuitive API than stdlib
- Built-in timezone support
- Human-readable intervals

**Cons**:
- **No recurrence support** - same problem as Arrow
- **Less adoption** - 5M installs/month vs dateutil's 100M
- **Heavier** - Larger package than dateutil
- **Redundant** - Overlap with dateutil features

**Why Rejected**: Same recurrence gap as Arrow. Lower adoption = higher risk. No compelling advantage over dateutil for recurring task use case.

## Implementation Example

```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from dateutil.parser import parse

# CLI parsing (flexible)
due_date = parse("2025-12-15 14:00")  # or "Dec 15, 2025 2PM"

# Recurring task - calculate next occurrence
def calculate_next_occurrence(due_date: datetime, recurrence: Recurrence) -> datetime:
    if recurrence == Recurrence.DAILY:
        return rrule(DAILY, dtstart=due_date, count=2)[1]
    elif recurrence == Recurrence.WEEKLY:
        return rrule(WEEKLY, dtstart=due_date, count=2)[1]
    elif recurrence == Recurrence.MONTHLY:
        return rrule(MONTHLY, dtstart=due_date, count=2)[1]

# Edge cases handled automatically:
# Jan 31 + MONTHLY → Feb 28 (or 29 in leap year)
# Nov 3 2024 02:00 EDT + DAILY → Nov 3 2024 02:00 EST (DST transition)
```

## References

- Feature Spec: `specs/001-phase1-cli-todo/spec.md` (FR-023 to FR-030: Recurring Tasks, Due Dates, Reminders)
- Implementation Plan: `specs/001-phase1-cli-todo/plan.md` (AD-004)
- Research: `specs/001-phase1-cli-todo/research.md` (Sections 3, 4)
- Data Model: `specs/001-phase1-cli-todo/data-model.md` (Recurring Task Algorithm)
- RFC 5545 (iCalendar): https://tools.ietf.org/html/rfc5545
- python-dateutil Docs: https://dateutil.readthedocs.io/
- Related ADRs: ADR-001 (Storage Abstraction - affects due_date field storage)

---

**Acceptance Criteria Verification**:
- ✅ Decision documents date/time library with recurrence rationale
- ✅ Explicit alternatives (Arrow, stdlib, Pendulum) with rejection reasons (no rrule, manual complexity)
- ✅ Consequences cover positive (RFC 5545, edge cases) and negative (dependency, learning curve)
- ✅ References link to spec FR-023-030, plan.md, research.md, RFC 5545
