# Phase 2: Full-Stack Web Application - Overview

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-12-21
**Phase:** 2 of 5

---

## Table of Contents

1. [Overview](#overview)
2. [Goals and Scope](#goals-and-scope)
3. [Architecture Summary](#architecture-summary)
4. [Technology Stack](#technology-stack)
5. [Monorepo Structure](#monorepo-structure)
6. [Phase 2 Required Patterns](#phase-2-required-patterns)
7. [Feature Specifications](#feature-specifications)
8. [Development Workflow](#development-workflow)
9. [Agent-Driven Implementation](#agent-driven-implementation)
10. [Getting Started](#getting-started)
11. [References](#references)

---

## Overview

Phase 2 transforms the Phase 1 CLI todo application into a **multi-user, full-stack web application** with persistent storage, authentication, and a modern web interface. This phase demonstrates the transition from a single-user command-line tool to a scalable web application while preserving the working CLI from Phase 1.

**Key Transformation:**
- **Phase 1:** Single-user CLI with in-memory storage
- **Phase 2:** Multi-user web app with PostgreSQL, JWT authentication, and Next.js UI

**Independence:** Phase 1 CLI remains fully functional and runnable alongside Phase 2 web application.

---

## Goals and Scope

### Primary Goals

1. **Multi-User Support**
   - Each user has isolated task data
   - JWT-based authentication with Better Auth
   - User data completely separated (user A cannot see user B's tasks)

2. **Persistent Storage**
   - PostgreSQL database (Neon serverless)
   - Task data survives application restarts
   - Soft deletes for data safety

3. **Modern Web Interface**
   - Next.js 16+ with App Router
   - Responsive design (mobile + desktop)
   - Real-time feedback and error handling

4. **RESTful API**
   - FastAPI backend with automatic OpenAPI docs
   - Versioned endpoints (/api/v1/)
   - Type-safe request/response with Pydantic

5. **Spec-Driven Development**
   - All features specified before implementation
   - Agent-driven workflow for consistent quality
   - Complete acceptance criteria for all features

### Out of Scope (Deferred to Later Phases)

- Real-time updates (WebSockets) → Phase 3
- Task collaboration/sharing → Phase 4
- Advanced search (full-text search, complex queries, saved searches) → Phase 3
  - **Note:** Basic filtering (by status, priority, tags) IS included in Phase 2
  - **Note:** Simple search by title/description IS included in Phase 2
- Pagination for large datasets → Phase 3
- Audit log and task history → Phase 5
- Recurring tasks automation → Phase 5
- Notifications and reminders → Phase 5

---

## Architecture Summary

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Phase 2 Web Application                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │   Frontend      │  HTTP   │    Backend      │            │
│  │   (Next.js)     │ ──────> │   (FastAPI)     │            │
│  │                 │ <────── │                 │            │
│  │  - App Router   │  JSON   │  - REST API     │            │
│  │  - React        │         │  - JWT Auth     │            │
│  │  - Tailwind     │         │  - Pydantic     │            │
│  │  - Better Auth  │         │  - SQLModel     │            │
│  └─────────────────┘         └─────────────────┘            │
│         │                            │                       │
│         │                            │                       │
│         │                            ▼                       │
│         │                   ┌─────────────────┐             │
│         │                   │   PostgreSQL    │             │
│         │                   │   (Neon)        │             │
│         │                   │                 │             │
│         │                   │  - User tasks   │             │
│         │                   │  - Soft deletes │             │
│         │                   │  - Indexes      │             │
│         │                   └─────────────────┘             │
│         │                                                    │
│         └─────> Better Auth (JWT tokens, user_id)           │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Phase 1 CLI (Still Works!)                  │
├─────────────────────────────────────────────────────────────┤
│  python -m cli.main add "Buy groceries"                      │
│  Uses: In-memory storage (independent from web app)          │
└─────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
1. User visits frontend → Redirected to login
2. Better Auth (frontend) → User enters credentials
3. Better Auth → Issues JWT token with user_id claim
4. Frontend → Stores JWT in secure HTTP-only cookie
5. Frontend → Sends requests with Authorization: Bearer {JWT}
6. Backend → Validates JWT, extracts user_id
7. Backend → Filters all DB queries by user_id
8. Backend → Returns only user's own data
```

**Key Rules:**
- Frontend manages authentication (Better Auth)
- Backend validates JWT and extracts user_id
- Backend has NO users table (trusts frontend JWT)
- user_id NEVER in URL paths (always from JWT token)

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15+ | React framework, App Router, server components |
| **React** | 18+ | UI library |
| **TypeScript** | 5+ | Type safety |
| **Tailwind CSS** | 3+ | Utility-first styling |
| **Better Auth** | Latest | JWT authentication, token management |
| **Vitest** | Latest | Unit testing |
| **React Testing Library** | Latest | Component testing |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | Latest | Python async web framework |
| **Python** | 3.11+ | Backend language |
| **SQLModel** | Latest | ORM with Pydantic integration |
| **Pydantic** | 2+ | Data validation, serialization |
| **PostgreSQL** | 15+ | Relational database |
| **Alembic** | Latest | Database migrations |
| **Pytest** | Latest | Testing framework |
| **Uvicorn** | Latest | ASGI server |

### Database

| Technology | Purpose |
|------------|---------|
| **Neon PostgreSQL** | Serverless PostgreSQL hosting, auto-scaling |
| **JSONB** | Store tags as array without junction table |
| **Partial Indexes** | Optimize soft delete queries |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Claude Code** | AI-assisted development with agent workflow |
| **UV** | Python package manager |
| **npm** | Node.js package manager |
| **Git** | Version control |

---

## Monorepo Structure

```
hackathon2/
├── .claude/
│   ├── agents/                      # Agent definitions (ADR-005)
│   │   ├── spec-writer-agent.md
│   │   ├── spec-coordinator-agent.md
│   │   ├── schema-architect-agent.md
│   │   ├── api-developer-agent.md
│   │   ├── ui-developer-agent.md
│   │   ├── test-engineer-agent.md
│   │   └── quality-guardian-agent.md
│   └── skills/                      # Claude Code skills
│       ├── spec-architect/
│       ├── spec-interpreter/
│       ├── type-contract-enforcer/
│       ├── database-designer/
│       └── ... (16 total skills)
│
├── specs/
│   ├── 001-phase1-cli/             # Phase 1 specs (preserved)
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
│   └── 002-phase2-fullstack-web/   # Phase 2 specs (feature-oriented)
│       ├── 00-phase2-overview.md   # This file
│       ├── 00-backend-architecture.md  # Backend patterns
│       ├── 08-frontend-design-flow.md  # Frontend patterns
│       ├── 01-user-authentication.md
│       ├── 02-task-crud.md
│       ├── 03-task-completion.md
│       ├── 04-task-priority.md
│       ├── 05-task-tags.md
│       ├── 06-task-due-dates.md
│       └── 07-dashboard-overview.md
│
├── shared/                          # Shared types (Phase 2)
│   └── types/
│       ├── task.ts                 # TypeScript types for frontend
│       └── task.py                 # Pydantic types for backend
│
├── cli/                            # Phase 1 CLI (still works!)
│   ├── main.py
│   ├── commands.py
│   └── storage/
│       ├── base.py
│       ├── memory.py              # In-memory storage
│       └── database.py            # Optional DB storage
│
├── src/
│   └── core/
│       ├── backend/                        # Phase 2 Backend
│       │   ├── main.py                    # FastAPI app entry point
│       │   ├── models/                    # SQLModel database models
│       │   │   └── task.py
│       │   ├── schemas/                   # Pydantic request/response schemas
│       │   │   └── task.py
│       │   ├── routers/                   # API route handlers
│       │   │   └── tasks.py
│       │   ├── dependencies.py            # FastAPI dependencies (auth, db)
│       │   ├── auth.py                    # JWT validation
│       │   ├── database.py                # Database connection
│       │   ├── migrations/                # Alembic migrations
│       │   └── tests/
│       │       ├── unit/
│       │       └── integration/
│       │
│       └── frontend/                      # Phase 2 Frontend
│           ├── app/                       # Next.js App Router
│           │   ├── layout.tsx
│           │   ├── page.tsx               # Dashboard
│           │   ├── login/
│           │   └── tasks/
│           │       └── page.tsx
│           ├── components/                # React components
│           │   └── tasks/
│           │       ├── TaskList.tsx
│           │       ├── TaskForm.tsx
│           │       └── TaskCard.tsx
│           ├── lib/
│           │   └── api.ts                 # Centralized API client
│           ├── tests/
│           │   └── unit/
│           ├── package.json
│           ├── tailwind.config.js
│           └── CLAUDE.md                  # Frontend-specific guidance
│
├── history/
│   ├── prompts/                   # Prompt History Records (PHRs)
│   │   ├── constitution/
│   │   ├── 002-phase2-fullstack-web/
│   │   └── general/
│   └── adr/                       # Architecture Decision Records
│       ├── 001-storage-abstraction-layer.md
│       ├── 002-cli-technology-stack.md
│       ├── 003-date-time-handling-for-recurrence.md
│       ├── 004-phase2-fullstack-architecture.md
│       └── 005-agent-architecture-for-phase2-development.md
│
├── .env                           # Environment variables
├── .gitignore
├── ARCHITECTURE.md                # Multi-phase architecture
├── CLAUDE.md                      # Root Claude Code instructions
└── README.md
```

---

## Phase 2 Required Patterns

All Phase 2 features MUST follow these architectural patterns:

### 1. User Isolation

**Pattern:** All database queries filtered by user_id from JWT token

```python
# ✅ CORRECT - user_id from JWT dependency
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    statement = select(Task).where(
        Task.user_id == user_id,  # Filter by authenticated user
        Task.deleted_at == None
    )
    return session.exec(statement).all()

# ❌ WRONG - user_id in URL path
@router.get("/api/v1/users/{user_id}/tasks")  # NEVER DO THIS
```

### 2. Soft Deletes

**Pattern:** Set deleted_at timestamp instead of hard delete

```python
# ✅ CORRECT - Soft delete
@router.delete("/api/v1/tasks/{id}")
async def delete_task(task_id: int, user_id: str = Depends(get_current_user)):
    task.deleted_at = datetime.utcnow()
    session.commit()
    return Response(status_code=204)

# ❌ WRONG - Hard delete
session.delete(task)  # NEVER DO THIS
```

### 3. Auto Timestamps

**Pattern:** created_at and updated_at managed automatically

```python
class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Auto-update hook for updated_at on every change
```

### 4. JSONB for Arrays

**Pattern:** Use PostgreSQL JSONB for simple arrays (tags)

```python
from sqlalchemy.dialects.postgresql import JSONB

class Task(SQLModel, table=True):
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    # No separate tags table in Phase 2
```

### 5. Centralized API Client

**Pattern:** All frontend API calls through centralized client

```typescript
// ✅ CORRECT - Use centralized API client
import { api } from '@/lib/api';
const tasks = await api.getTasks();

// ❌ WRONG - Direct fetch in component
const res = await fetch('/api/v1/tasks');  // NEVER DO THIS
```

### 6. JWT Authentication

**Pattern:** All endpoints require valid JWT with user_id claim

```python
# Every route handler
async def endpoint(
    user_id: str = Depends(get_current_user),  # Required
    ...
):
```

---

## Feature Specifications

Phase 2 consists of **10 specification files** organized as follows:

### Foundation Specs (Architecture)

1. **00-phase2-overview.md** (This File)
   - Phase 2 architecture overview
   - Monorepo structure and tech stack
   - Required patterns and workflows

2. **00-backend-architecture.md**
   - API contract standards
   - Data ownership rules
   - Validation rules
   - Error behavior
   - Phase 2 backend patterns

3. **08-frontend-design-flow.md**
   - Centralized API client patterns
   - Reusable UI components
   - Navigation and routing
   - Design system (Tailwind)
   - Error/loading states

### Feature Specs (12-Section Template)

4. **01-user-authentication.md**
   - Better Auth setup
   - Login/logout flows
   - JWT token management
   - Protected routes

5. **02-task-crud.md** ✅
   - Create, read, update, delete tasks
   - User isolation
   - Soft deletes

6. **03-task-completion.md**
   - Toggle task completion status
   - PATCH /api/v1/tasks/{id}/toggle

7. **04-task-priority.md**
   - Set priority (1-5)
   - Filter by priority
   - Priority validation

8. **05-task-tags.md**
   - Add/remove tags (JSONB)
   - Filter by tags
   - Tag management

9. **06-task-due-dates.md**
   - Set due dates
   - Overdue detection
   - Date validation

10. **07-dashboard-overview.md**
    - Task statistics
    - Summary view
    - Aggregation queries

---

## Development Workflow

### Spec-Driven Development

Phase 2 follows a strict **spec → implementation → validation** workflow:

```
1. SPEC PHASE
   ├─> Spec Writer Agent creates feature spec (12 sections)
   ├─> Spec includes: User Stories, Acceptance Criteria, API Contract,
   │   Data Model, UI/UX Requirements
   └─> Output: specs/002-phase2-fullstack-web/features/{name}.md

2. COORDINATION PHASE
   ├─> Spec Coordinator Agent reads spec
   ├─> Generates shared types (TypeScript + Pydantic)
   ├─> Creates implementation plan
   └─> Output: shared/types/{entity}.ts and {entity}.py

3. DATABASE PHASE
   ├─> Schema Architect Agent creates SQLModel
   ├─> Applies Phase 2 patterns (user_id, deleted_at, etc.)
   ├─> Generates Alembic migration
   └─> Output: src/core/backend/models/{entity}.py, migrations/

4. BACKEND PHASE
   ├─> API Developer Agent implements FastAPI routes
   ├─> Enforces auth boundaries (JWT, user_id filtering)
   ├─> Creates Pydantic schemas
   └─> Output: src/core/backend/routers/{entity}.py, src/core/backend/schemas/

5. FRONTEND PHASE
   ├─> UI Developer Agent builds Next.js components
   ├─> Uses centralized API client
   ├─> Implements UI/UX from spec
   └─> Output: src/core/frontend/app/, src/core/frontend/components/

6. TESTING PHASE
   ├─> Test Engineer Agent generates test suites
   ├─> Backend: Pytest (unit + integration)
   ├─> Frontend: Vitest + RTL (unit tests)
   └─> Output: src/core/backend/tests/, src/core/frontend/tests/

7. VALIDATION PHASE
   ├─> Quality Guardian Agent validates implementation
   ├─> Checks: API contracts, test coverage, auth boundaries,
   │   monorepo boundaries
   ├─> Output: Quality report (APPROVED or NEEDS FIXES)
   └─> If approved: Ready for deployment
       If fixes needed: Return to implementation phase
```

---

## Agent-Driven Implementation

Phase 2 uses **7 specialized agents** (documented in ADR-005):

### Planning Phase
1. **Spec Writer Agent**
   - Creates complete 12-section feature specs
   - Enforces clarity and testability
   - Escalates ambiguities to user

### Implementation Phase
2. **Spec Coordinator Agent**
   - Reads specs, generates shared types
   - Coordinates changes across monorepo
   - Validates spec authority

3. **Schema Architect Agent**
   - Designs SQLModel database schemas
   - Enforces Phase 2 patterns
   - Creates migrations

4. **API Developer Agent**
   - Implements FastAPI routes
   - Enforces auth boundaries
   - Creates Pydantic schemas

5. **UI Developer Agent**
   - Builds Next.js components
   - Uses centralized API client
   - Implements UI/UX requirements

6. **Test Engineer Agent**
   - Generates comprehensive test suites
   - Backend: Pytest (unit + integration)
   - Frontend: Vitest + RTL

### Validation Phase
7. **Quality Guardian Agent**
   - Validates API contracts (3-way)
   - Audits test coverage
   - Enforces auth/monorepo boundaries
   - Approves or requests fixes

**Time Estimates (per feature):**
- Spec Writing: ~2 hours
- Implementation: ~3 hours 15 minutes
- Total: ~5 hours per feature

---

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **PostgreSQL** 15+ (Neon account recommended)
- **Git** (version control)
- **UV** (Python package manager)

### Environment Setup

1. **Clone and Install Dependencies**

   ```bash
   # Clone repository
   cd hackathon2

   # Backend setup
   cd src/core/backend
   uv sync  # Install Python dependencies

   # Frontend setup
   cd ../../frontend
   npm install
   ```

2. **Configure Environment Variables**

   Create `.env` in root:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:password@host:5432/dbname

   # JWT
   JWT_SECRET=your-secret-key-here

   # Frontend
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run Database Migrations**

   ```bash
   cd src/core/backend
   alembic upgrade head
   ```

4. **Start Development Servers**

   ```bash
   # Terminal 1: Backend
   cd src/core/backend
   uvicorn main:app --reload --port 8000

   # Terminal 2: Frontend
   cd src/core/frontend
   npm run dev

   # Terminal 3: CLI (optional, still works!)
   python -m cli.main list
   ```

5. **Access Application**

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Implementation Order

Follow this order for Phase 2 implementation:

1. ✅ Create foundation specs (overview, backend arch, frontend design, auth)
2. ✅ Implement authentication (Feature 01)
3. ✅ Implement Task CRUD (Feature 02) - Core feature
4. Implement remaining features (03-07) in any order
5. Final QA and deployment

---

## References

### Architecture Decision Records (ADRs)

- **ADR-004:** [Phase 2 Full-Stack Architecture](../../history/adr/004-phase2-fullstack-architecture.md)
  - Complete architectural decisions for Phase 2
  - Technology stack rationale
  - Authentication architecture
  - Database design decisions

- **ADR-005:** [Agent Architecture for Phase 2 Development](../../history/adr/005-agent-architecture-for-phase2-development.md)
  - 7-agent workflow design
  - Agent roles and decision authority
  - Implementation time estimates

### Related Documentation

- **Phase 1 Specs:** [specs/001-phase1-cli/](../001-phase1-cli/)
- **Constitution:** [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- **Multi-Phase Architecture:** [ARCHITECTURE.md](../../ARCHITECTURE.md)
- **Claude Code Guide:** [CLAUDE.md](../../CLAUDE.md)

### External Documentation

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Better Auth Documentation](https://www.better-auth.com/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs/)

---

**Document Status:** Active
**Next Review:** After Feature 01 (Authentication) implementation
**Maintained By:** Development Team
