---
name: type-contract-enforcer
description: Generate and synchronize TypeScript/Python types from API specifications. Use when (1) creating or updating API specs, (2) implementing frontend/backend code, (3) user asks to "generate types" or "sync types", or (4) validating type consistency across layers.
license: Complete terms in LICENSE.txt
---

# Type Contract Enforcer

Generate TypeScript interfaces and Pydantic models from API specifications to ensure type consistency across frontend and backend.

## Workflow

Follow these steps when generating or syncing types:

1. **Read API specification** from `specs/phase2/api/[endpoint].md`
   - Identify request/response schemas
   - Note field names, types, and constraints
   - Capture validation rules and optional fields

2. **Generate TypeScript interfaces** for frontend (`shared/types/*.ts`)
   - Use interfaces, not type aliases
   - Include JSDoc comments from spec
   - Add validation constraints as comments
   - Export from shared types directory

3. **Generate Pydantic models** for backend (`shared/types/*.py`)
   - Use Pydantic BaseModel with Field validators
   - Include docstrings from spec
   - Add validation rules (min/max, regex, etc.)
   - Match TypeScript interface structure

4. **Validate consistency**
   - Compare generated types with existing types
   - Check for field name mismatches
   - Verify type mappings (string ↔ str, number ↔ int/float)
   - Alert on drift between spec and implementation

5. **Detect type drift**
   - Frontend types not matching spec
   - Backend types not matching spec
   - TypeScript/Python type misalignment
   - Missing fields or extra fields

## Output Format

Present type generation results using this structure:

```
🔧 Type Generation: [endpoint-name]

Source: specs/phase2/api/[endpoint].md

Generated Files:
- shared/types/[entity].ts (TypeScript interface)
- shared/types/[entity].py (Pydantic model)

Type Mappings:
- title: string → str
- priority: number → int
- tags: string[] → list[str]
- created_at: string (ISO 8601) → datetime

✅ Types match specification
✅ TypeScript/Python types aligned

OR

⚠️ Type Drift Detected:
- Field 'priority' missing in TypeScript interface
- Field 'status' type mismatch: spec says string, backend uses int
```

## Generation Rules

**TypeScript Interface Pattern:**
```typescript
/**
 * Task creation request
 * From: specs/phase2/api/tasks-endpoints.md
 */
export interface TaskCreate {
  /** Task title (required, 1-200 chars) */
  title: string;

  /** Task description (optional) */
  description?: string;

  /** Priority level (1-5) */
  priority?: number;

  /** Task tags */
  tags?: string[];
}
```

**Pydantic Model Pattern:**
```python
from pydantic import BaseModel, Field
from datetime import datetime

class TaskCreate(BaseModel):
    """Task creation request

    From: specs/phase2/api/tasks-endpoints.md
    """
    title: str = Field(..., min_length=1, max_length=200,
                       description="Task title (required)")
    description: str | None = Field(None,
                                    description="Task description (optional)")
    priority: int | None = Field(None, ge=1, le=5,
                                  description="Priority level (1-5)")
    tags: list[str] | None = Field(default_factory=list,
                                    description="Task tags")
```

## Type Mapping Reference

**Spec Type → TypeScript → Python:**
- string → `string` → `str`
- number (integer) → `number` → `int`
- number (float) → `number` → `float`
- boolean → `boolean` → `bool`
- array[T] → `T[]` → `list[T]`
- object → `Record<string, T>` → `dict[str, T]`
- ISO 8601 date → `string` → `datetime`
- enum → `type Union` → `Literal` or `Enum`
- optional → `T | undefined` or `T?` → `T | None`

## File Organization

```
shared/types/
├── task.ts          # Task-related TypeScript interfaces
├── task.py          # Task-related Pydantic models
├── user.ts          # User-related TypeScript interfaces
├── user.py          # User-related Pydantic models
└── common.ts/py     # Shared types (Priority, Status, etc.)
```

## Key Rules

- **Spec is single source of truth** - Never manually edit generated types without updating spec first
- **One file per entity** - Keep task types in task.ts/task.py, user types in user.ts/user.py
- **Include documentation** - Add JSDoc/docstrings with field descriptions from spec
- **Validation rules** - Include constraints (min/max length, regex, range) in Pydantic models
- **Alert on drift** - If frontend/backend types diverge from spec, flag immediately
- **Suggest spec updates** - If implementation needs differ from spec, propose spec changes
- **Version with spec** - When API version changes, update types in lockstep
- **Export properly** - Ensure types are exported and importable by frontend/backend code
