---
name: monorepo-coordinator
description: Coordinate monorepo structure, maintain code boundaries, and enforce spec authority across frontend, backend, CLI, and shared code. Use when (1) making changes that affect multiple parts of the monorepo, (2) adding new features across layers, (3) modifying specs or types, or (4) validating import patterns and dependencies.
license: Complete terms in LICENSE.txt
---

# Monorepo Coordinator

Manage monorepo structure, enforce code boundaries, maintain spec authority, and coordinate changes across frontend, backend, CLI, and shared code.

## Workflow

Follow these steps when coordinating monorepo changes:

1. **Understand current monorepo structure**
   - Identify which directories exist
   - Understand folder purposes and boundaries
   - Check phase-specific organization
   - Review spec locations

2. **Validate change boundaries**
   - Determine which parts are affected
   - Check if changes cross boundaries
   - Verify spec authority is maintained
   - Ensure proper import patterns

3. **Enforce modification rules**
   - Specs are authoritative (modify specs first)
   - Types generated from specs (don't manually edit)
   - Shared code used by all layers
   - Layer-specific code stays isolated

4. **Coordinate cross-layer changes**
   - Update specs first
   - Regenerate shared types
   - Update backend implementation
   - Update frontend implementation
   - Update tests in both layers

5. **Verify boundaries are respected**
   - No circular dependencies
   - Proper import paths used
   - Shared code is truly shared
   - Phase isolation maintained

## Output Format

Present monorepo coordination using this structure:

```
🗂️ Monorepo Coordination: [change-description]

Affected Areas:
- specs/phase2/api/tasks-endpoints.md (authoritative)
- shared/types/task.ts (generated from spec)
- shared/types/task.py (generated from spec)
- backend/routers/tasks.py (implementation)
- frontend/lib/api.ts (implementation)

Change Flow:
1. ✅ Update spec first (specs/phase2/api/tasks-endpoints.md)
2. ✅ Generate types (shared/types/task.ts, task.py)
3. ✅ Update backend (backend/routers/tasks.py)
4. ✅ Update frontend (frontend/lib/api.ts)
5. ✅ Update tests (backend/tests/, frontend/tests/)

Boundary Validation:
✅ Spec is authoritative source
✅ Types are generated, not manually edited
✅ No frontend → backend imports
✅ No backend → frontend imports
✅ Shared types used by both layers
✅ Phase isolation maintained
```

## Monorepo Structure

### Complete Folder Organization

```
hackathon2/                          # Monorepo root
│
├── specs/                           # AUTHORITATIVE specifications
│   ├── phase1/                      # Phase 1 CLI specs
│   │   └── requirements.md
│   └── phase2/                      # Phase 2 Full-Stack specs
│       ├── features/                # Feature specifications
│       │   ├── tasks.md
│       │   ├── tags.md
│       │   └── search.md
│       ├── api/                     # API endpoint specifications
│       │   ├── tasks-endpoints.md
│       │   └── tags-endpoints.md
│       └── database/                # Database specifications
│           └── schema.md
│
├── shared/                          # SHARED across all layers
│   └── types/                       # Generated from specs (DO NOT EDIT MANUALLY)
│       ├── task.ts                  # TypeScript types (frontend)
│       ├── task.py                  # Pydantic models (backend)
│       ├── tag.ts
│       └── tag.py
│
├── cli/                             # Phase 1: CLI application (ISOLATED)
│   ├── src/
│   │   ├── core/                    # Business logic
│   │   │   ├── models.py
│   │   │   └── storage.py
│   │   └── commands/                # CLI commands
│   └── tests/
│
├── backend/                         # Phase 2: FastAPI backend (ISOLATED from frontend)
│   ├── main.py                      # FastAPI app entry
│   ├── config.py                    # Settings from env
│   ├── dependencies.py              # Shared dependencies (auth, db)
│   │
│   ├── models/                      # SQLModel database models
│   │   ├── task.py                  # Can import from shared/types/task.py
│   │   └── base.py
│   │
│   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── task.py                  # Can import from shared/types/task.py
│   │   └── common.py
│   │
│   ├── routers/                     # API route handlers
│   │   ├── tasks.py
│   │   └── tags.py
│   │
│   ├── services/                    # Business logic
│   │   └── task_service.py
│   │
│   └── tests/                       # Backend tests
│       ├── unit/
│       └── integration/
│
├── frontend/                        # Phase 2: Next.js frontend (ISOLATED from backend)
│   ├── app/                         # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── tasks/
│   │       └── page.tsx
│   │
│   ├── components/                  # React components
│   │   ├── ui/
│   │   └── tasks/
│   │
│   ├── lib/                         # Frontend utilities
│   │   ├── api.ts                   # Centralized API client (can import shared/types/task.ts)
│   │   └── auth.ts
│   │
│   ├── types/                       # Frontend-specific types (or use shared/types/)
│   │
│   └── tests/                       # Frontend tests
│       ├── unit/
│       └── integration/
│
├── history/                         # Project history
│   ├── prompts/                     # Prompt History Records
│   │   ├── constitution/
│   │   ├── general/
│   │   └── [feature-name]/
│   └── adr/                         # Architecture Decision Records
│       ├── 001-cli-architecture.md
│       └── 004-phase2-fullstack-architecture.md
│
├── .specify/                        # SpecKit Plus tooling
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── scripts/
│
└── .claude/                         # Claude Code configuration
    └── skills/
        ├── monorepo-coordinator/
        ├── spec-interpreter/
        └── ... (other skills)
```

## Folder Boundary Rules

### 1. Specs (`specs/`)

**Purpose:** Single source of truth for requirements, API contracts, and data models

**Who Can Modify:**
- ✅ Anyone making feature changes (but spec changes FIRST, code SECOND)
- ✅ Architecture decisions must update specs

**What Lives Here:**
- Feature requirements with acceptance criteria
- API endpoint specifications (request/response schemas)
- Database schema specifications
- Business rules and validation logic

**Boundary Rules:**
- ✅ Specs are READ by all layers
- ❌ Specs DO NOT import code
- ✅ Specs define contracts, code implements contracts
- ❌ NEVER modify code without updating spec first

**Example Files:**
```
specs/phase2/api/tasks-endpoints.md
specs/phase2/features/tasks.md
specs/phase2/database/schema.md
```

**Import Pattern:**
```
Code → Specs ✅ (read and implement)
Specs → Code ❌ (specs don't import code)
```

### 2. Shared (`shared/`)

**Purpose:** Code and types shared across all layers (frontend, backend, CLI)

**Who Can Modify:**
- ⚠️ GENERATED CODE - Do not manually edit!
- ✅ Generated by type-contract-enforcer skill from specs
- ✅ If changes needed, update spec first, then regenerate

**What Lives Here:**
- TypeScript interfaces (for frontend)
- Pydantic models (for backend)
- Shared enums and constants
- Common validation rules

**Boundary Rules:**
- ✅ Backend CAN import from `shared/types/*.py`
- ✅ Frontend CAN import from `shared/types/*.ts`
- ✅ CLI CAN import shared enums/constants
- ❌ Shared CANNOT import from backend, frontend, or CLI
- ❌ NEVER manually edit - always regenerate from spec

**Example Files:**
```typescript
// shared/types/task.ts (GENERATED - DO NOT EDIT)
/**
 * Generated from: specs/phase2/api/tasks-endpoints.md
 * DO NOT EDIT MANUALLY - Run type generation to update
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: number | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}
```

```python
# shared/types/task.py (GENERATED - DO NOT EDIT)
"""
Generated from: specs/phase2/api/tasks-endpoints.md
DO NOT EDIT MANUALLY - Run type generation to update
"""
from pydantic import BaseModel, Field
from datetime import datetime

class Task(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
```

**Import Pattern:**
```
Backend → shared/types/*.py ✅
Frontend → shared/types/*.ts ✅
CLI → shared/types/*.py ✅
shared → Backend/Frontend/CLI ❌
```

### 3. CLI (`cli/`)

**Purpose:** Phase 1 command-line application (isolated, complete)

**Who Can Modify:**
- ✅ Anyone working on Phase 1 features
- ⚠️ Phase 2 should NOT modify (only reference for migration)

**What Lives Here:**
- CLI-specific models and storage
- Command implementations
- Phase 1 business logic
- CLI-specific tests

**Boundary Rules:**
- ✅ CLI is ISOLATED from backend and frontend
- ✅ Phase 2 can READ CLI code for migration
- ❌ Phase 2 should NOT modify CLI code
- ✅ CLI can import from shared (enums, constants)
- ❌ CLI does NOT import from backend or frontend

**Example:**
```python
# cli/src/core/models.py
from shared.types.priority import Priority  # ✅ Can import shared enums

class Task:  # CLI-specific model
    # Phase 1 implementation
```

**Import Pattern:**
```
CLI → shared/types/*.py ✅ (enums, constants only)
Backend/Frontend → CLI ❌ (isolated)
Phase 2 can READ CLI ✅ (for migration reference)
Phase 2 MODIFIES CLI ❌ (keep Phase 1 working)
```

### 4. Backend (`backend/`)

**Purpose:** Phase 2 FastAPI backend (isolated from frontend)

**Who Can Modify:**
- ✅ Anyone implementing backend features
- ✅ Must follow spec authority (specs first, code second)

**What Lives Here:**
- FastAPI route handlers
- SQLModel database models
- Pydantic schemas (request/response)
- Backend business logic
- Backend tests

**Boundary Rules:**
- ✅ Backend imports from `shared/types/*.py`
- ❌ Backend CANNOT import from `frontend/`
- ❌ Backend CANNOT import from `cli/`
- ✅ Backend implements contracts defined in specs
- ✅ Backend validates JWT from frontend

**Example:**
```python
# backend/models/task.py
from sqlmodel import SQLModel, Field
from shared.types.task import Task as TaskBase  # ✅ Import shared type

class Task(SQLModel, table=True):
    """Database model - extends shared type"""
    # Add database-specific fields
    user_id: str = Field(index=True)
    deleted_at: datetime | None = None
```

```python
# backend/schemas/task.py
from pydantic import BaseModel
from shared.types.task import TaskCreate  # ✅ Import shared type

# Use shared types directly or extend them
class TaskCreateRequest(TaskCreate):
    pass  # Or add request-specific fields
```

**Import Pattern:**
```
Backend → shared/types/*.py ✅
Backend → Frontend ❌ (isolated)
Backend → CLI ❌ (can read for migration, don't import)
```

### 5. Frontend (`frontend/`)

**Purpose:** Phase 2 Next.js frontend (isolated from backend)

**Who Can Modify:**
- ✅ Anyone implementing frontend features
- ✅ Must follow spec authority (specs first, code second)

**What Lives Here:**
- Next.js pages and layouts
- React components
- Frontend utilities (API client, auth)
- Frontend-specific types (or use shared)
- Frontend tests

**Boundary Rules:**
- ✅ Frontend imports from `shared/types/*.ts`
- ❌ Frontend CANNOT import from `backend/`
- ❌ Frontend CANNOT import from `cli/`
- ✅ Frontend calls backend via API (not direct imports)
- ✅ Frontend issues JWT tokens (Better Auth)

**Example:**
```typescript
// frontend/lib/api.ts
import type { Task, TaskCreate } from '@shared/types/task';  // ✅ Import shared type

export const api = {
  getTasks: () => fetchWithAuth<Task[]>('/api/v1/tasks'),
  createTask: (data: TaskCreate) =>
    fetchWithAuth<Task>('/api/v1/tasks', { method: 'POST', body: JSON.stringify(data) })
};
```

```typescript
// frontend/components/tasks/TaskList.tsx
import type { Task } from '@shared/types/task';  // ✅ Import shared type

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks }: TaskListProps) {
  // Component implementation
}
```

**Import Pattern:**
```
Frontend → shared/types/*.ts ✅
Frontend → Backend ❌ (use API calls, not imports)
Frontend → CLI ❌ (isolated)
```

### 6. History (`history/`)

**Purpose:** Project history and architectural decisions

**Who Can Modify:**
- ✅ Anyone creating PHRs (automatically after tasks)
- ✅ Anyone documenting architectural decisions (ADRs)

**What Lives Here:**
- Prompt History Records (PHRs)
- Architecture Decision Records (ADRs)
- Implementation notes
- Lessons learned

**Boundary Rules:**
- ✅ History is APPEND-ONLY (add new, don't delete old)
- ✅ PHRs routed by feature/phase
- ✅ ADRs numbered sequentially
- ❌ Code does NOT import from history
- ✅ History references code/specs (for documentation)

**Structure:**
```
history/
├── prompts/
│   ├── constitution/          # Constitution-related PHRs
│   ├── general/               # General PHRs
│   └── [feature-name]/        # Feature-specific PHRs
└── adr/
    ├── 001-decision.md
    └── 004-phase2-architecture.md
```

## Spec Authority Rules

### Rule 1: Specs Are the Single Source of Truth

**Process:**
1. ✅ Spec defines requirement
2. ✅ Types generated from spec
3. ✅ Code implements spec
4. ✅ Tests validate spec compliance

**Anti-Pattern:**
```
❌ WRONG:
1. Write code
2. Update spec to match code (backward!)

✅ CORRECT:
1. Write/update spec
2. Generate types from spec
3. Implement code following spec
4. Write tests validating spec
```

### Rule 2: Types Are Generated, Not Manually Edited

**Process:**
1. ✅ Update spec: `specs/phase2/api/tasks-endpoints.md`
2. ✅ Run type generation: Use type-contract-enforcer skill
3. ✅ Generated files updated:
   - `shared/types/task.ts` (TypeScript)
   - `shared/types/task.py` (Pydantic)
4. ✅ Code uses generated types

**Anti-Pattern:**
```typescript
// ❌ WRONG: Manually editing generated file
// shared/types/task.ts
export interface Task {
  id: number;
  title: string;
  newField: string;  // Added manually - WRONG!
}

// ✅ CORRECT: Update spec first
// 1. Update specs/phase2/api/tasks-endpoints.md
// 2. Regenerate shared/types/task.ts
// 3. File automatically includes newField
```

### Rule 3: Cross-Layer Changes Follow Spec-First Flow

**Complete Flow:**
```
1. Identify Need → "Add priority field to tasks"

2. Update Spec FIRST
   specs/phase2/api/tasks-endpoints.md:
   - priority: number (1-5)

3. Generate Types
   Run: type-contract-enforcer
   Updates:
   - shared/types/task.ts (adds priority: number)
   - shared/types/task.py (adds priority: int)

4. Update Backend
   backend/models/task.py:
   - Add: priority: int | None = Field(None, ge=1, le=5)

   backend/routers/tasks.py:
   - Use updated TaskCreate schema (now has priority)

5. Update Frontend
   frontend/components/tasks/TaskForm.tsx:
   - Add priority input field

   frontend/lib/api.ts:
   - Already type-safe with updated Task interface

6. Update Tests
   backend/tests/unit/test_tasks.py:
   - test_create_task_with_priority()
   - test_create_task_with_invalid_priority()

   frontend/tests/unit/TaskForm.test.tsx:
   - should set priority field
   - should validate priority range

7. Verify Consistency
   Run: api-contract-guardian
   Validates: spec ↔ backend ↔ frontend alignment
```

## Import Rules by Layer

### Backend Import Rules

**✅ ALLOWED:**
```python
# Backend can import from shared
from shared.types.task import Task, TaskCreate

# Backend can import from other backend modules
from backend.models.task import Task as DBTask
from backend.dependencies import get_current_user

# Backend can import standard libraries
from fastapi import APIRouter, Depends
from sqlmodel import Session
```

**❌ FORBIDDEN:**
```python
# Backend CANNOT import from frontend
from frontend.lib.api import api  # ❌ WRONG

# Backend CANNOT import from CLI
from cli.src.core.models import Task  # ❌ WRONG
```

### Frontend Import Rules

**✅ ALLOWED:**
```typescript
// Frontend can import from shared
import type { Task, TaskCreate } from '@shared/types/task';

// Frontend can import from other frontend modules
import { api } from '@/lib/api';
import { TaskForm } from '@/components/tasks/TaskForm';

// Frontend can import standard libraries
import { useState } from 'react';
```

**❌ FORBIDDEN:**
```typescript
// Frontend CANNOT import from backend
import { createTask } from '@backend/routers/tasks';  // ❌ WRONG

// Frontend CANNOT import from CLI
import { Task } from '@cli/src/core/models';  // ❌ WRONG
```

### CLI Import Rules

**✅ ALLOWED:**
```python
# CLI can import shared constants/enums
from shared.types.priority import Priority

# CLI can import from other CLI modules
from cli.src.core.storage import MemoryStorage

# CLI can import standard libraries
import click
```

**❌ FORBIDDEN:**
```python
# CLI CANNOT import from backend
from backend.models.task import Task  # ❌ WRONG

# CLI CANNOT import from frontend
from frontend.lib.api import api  # ❌ WRONG
```

## Validation Checklist

Before committing changes, verify:

**✅ Spec Authority:**
- [ ] Spec updated before code
- [ ] Types regenerated from spec
- [ ] Code implements spec, not the reverse

**✅ Boundary Respect:**
- [ ] No frontend → backend imports
- [ ] No backend → frontend imports
- [ ] No direct CLI modifications (Phase 2)
- [ ] Shared types used correctly

**✅ Import Patterns:**
- [ ] Backend imports only from backend/ and shared/
- [ ] Frontend imports only from frontend/ and shared/
- [ ] No circular dependencies

**✅ Phase Isolation:**
- [ ] Phase 1 (CLI) still functional
- [ ] Phase 2 (Full-Stack) independent
- [ ] No accidental CLI modifications

**✅ Type Safety:**
- [ ] TypeScript types from shared/types/
- [ ] Pydantic models from shared/types/
- [ ] No manual type edits (regenerate instead)

## Common Violations and Fixes

### Violation 1: Manually Edited Generated Types

**Problem:**
```typescript
// shared/types/task.ts (GENERATED)
export interface Task {
  id: number;
  title: string;
  customField: string;  // ❌ Added manually
}
```

**Fix:**
1. Update spec: `specs/phase2/api/tasks-endpoints.md`
2. Add `customField: string` to spec
3. Regenerate types using type-contract-enforcer
4. Commit spec AND generated types

### Violation 2: Code Before Spec

**Problem:**
```python
# backend/models/task.py
class Task(SQLModel, table=True):
    new_feature: str  # ❌ Added without spec update
```

**Fix:**
1. Remove premature code change
2. Update spec first: `specs/phase2/features/tasks.md`
3. Document requirement and acceptance criteria
4. Update API spec: `specs/phase2/api/tasks-endpoints.md`
5. Regenerate types
6. Implement in code

### Violation 3: Cross-Layer Imports

**Problem:**
```typescript
// frontend/lib/tasks.ts
import { Task } from '@backend/models/task';  // ❌ WRONG
```

**Fix:**
```typescript
// frontend/lib/tasks.ts
import type { Task } from '@shared/types/task';  // ✅ CORRECT
```

### Violation 4: Skipped Type Generation

**Problem:**
1. Update spec
2. Update backend code directly
3. Update frontend code directly
4. Skip type generation → Types drift from spec

**Fix:**
1. Update spec
2. **Generate types** ← Don't skip!
3. Update backend (use generated types)
4. Update frontend (use generated types)

## Key Rules

- **Specs are authoritative** - Code implements specs, not the reverse
- **Types are generated** - Never manually edit shared/types/
- **Layers are isolated** - No backend ↔ frontend imports
- **Shared is shared** - Backend and frontend both use shared/types/
- **Phase isolation** - Phase 1 (CLI) stays functional
- **Import rules enforced** - Each layer has allowed import paths
- **Spec-first workflow** - Always update spec before code
- **Regenerate types** - After every spec change
- **Validate boundaries** - Before committing changes
- **Cross-layer changes coordinated** - Follow spec → types → backend → frontend → tests flow
