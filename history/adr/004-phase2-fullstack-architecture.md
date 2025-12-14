# ADR 004: Phase 2 Full-Stack Architecture

**Date**: 2025-12-14
**Status**: Accepted
**Context**: Transitioning from Phase 1 (CLI) to Phase 2 (Full-Stack Web Application)
**Decision Makers**: Development Team
**Phase**: 2

---

## Context

Phase 1 delivered a functional CLI todo application with in-memory storage. Phase 2 requires transforming this into a multi-user web application with persistent storage, authentication, and modern web UI. This ADR documents all architectural decisions made during the Phase 2 planning session.

---

## Decision

We will build a full-stack web application using a **monorepo architecture** with Next.js frontend, FastAPI backend, and Neon PostgreSQL database, following **spec-driven development** with **architectural enforcement skills**.

---

## Architecture Decisions

### 1. Monorepo Structure

**Decision:** Organize as a monorepo with separate frontend, backend, and CLI directories.

**Structure:**
```
hackathon2/
├── .specify/              # SpecKit Plus configuration
├── specs/
│   ├── phase1/           # CLI specs (preserved)
│   └── phase2/           # Web app specs (new)
│       ├── features/     # User stories
│       ├── api/          # API contracts
│       ├── database/     # Schema design
│       └── ui/           # Component specs
├── shared/
│   └── types/            # Shared TypeScript/Python types
├── cli/                  # Phase 1 CLI (keep working)
├── frontend/             # Next.js application
│   └── CLAUDE.md
├── backend/              # FastAPI application
│   └── CLAUDE.md
├── CLAUDE.md             # Root monorepo guide
├── .env                  # Shared environment variables
└── docker-compose.yml    # Optional local development
```

**Rationale:**
- Single repository simplifies Claude Code context
- Easier to maintain type consistency
- Shared specs and documentation
- Preserves Phase 1 CLI for reference and manual use

**Alternatives Considered:**
- Separate repositories (rejected: harder for Claude Code to navigate)
- Merge CLI into web app (rejected: want to keep CLI working independently)

---

### 2. Authentication Architecture

**Decision:** Frontend-managed authentication with backend JWT validation.

**Architecture:**
```
Frontend (Next.js)
  ├── Better Auth manages user identity
  ├── Issues JWT tokens on login
  └── Stores JWT in secure HTTP-only cookie
       ↓ Authorization: Bearer <JWT>
Backend (FastAPI)
  ├── Validates JWT signature
  ├── Extracts user_id from token
  ├── Filters all queries by user_id
  └── NO users table
```

**Key Rules:**
1. Frontend issues JWT, backend validates JWT
2. NO user_id in URL paths (extract from token)
3. Every database query filtered by authenticated user_id
4. User isolation enforced on every operation
5. Backend is stateless and trusts JWT

**Rationale:**
- Clear separation of concerns
- Backend doesn't need user management complexity
- Stateless backend is more scalable
- User isolation enforced at data access layer

**Alternatives Considered:**
- Backend manages users (rejected: adds complexity)
- Session-based auth (rejected: less scalable)
- User ID in URL paths (rejected: security risk)

---

### 3. Database Design

**Decision:** PostgreSQL with SQLModel ORM, prioritizing Phase 2 simplicity.

**Schema:**
```sql
tasks (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,          -- From JWT, no FK
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  priority VARCHAR(20) DEFAULT 'medium',
  tags JSONB DEFAULT '[]',        -- Array, not junction table
  due_date TIMESTAMP,
  recurrence VARCHAR(20),
  deleted_at TIMESTAMP,           -- Soft delete
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at);
```

**Key Decisions:**

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Users Table** | NO users table | Auth is frontend concern |
| **user_id Type** | TEXT (from JWT) | No foreign key to users |
| **Priorities** | Enum stored as VARCHAR | Simple, no separate table |
| **Tags** | JSONB array | Phase 2 simplicity, migrate to junction in Phase 3+ if needed |
| **Recurrence** | VARCHAR field on task | Simple storage, logic in app layer |
| **Soft Deletes** | deleted_at timestamp | Safer than hard deletes, audit trail |
| **Audit History** | Deferred to Phase 5 | Event-driven pipeline with Kafka |

**Rationale:**
- Prioritize simplicity for Phase 2
- JSONB tags are fast and simple for limited tag usage
- Soft deletes provide safety net
- Can migrate to normalized tags in Phase 3+ if needed

**Alternatives Considered:**
- Tags as many-to-many junction table (rejected: overkill for Phase 2)
- Boolean is_deleted flag (rejected: timestamp provides more info)
- Separate recurrence table (rejected: adds complexity)

---

### 4. API Design

**Decision:** RESTful API with JWT authentication and versioning.

**Endpoints:**
```
GET    /api/v1/tasks              # List user's tasks
POST   /api/v1/tasks              # Create task
GET    /api/v1/tasks/{id}         # Get task
PUT    /api/v1/tasks/{id}         # Update task
DELETE /api/v1/tasks/{id}         # Soft delete task
PATCH  /api/v1/tasks/{id}/toggle  # Toggle completion
```

**Key Rules:**
1. All endpoints require valid JWT token
2. NO user_id in URL path (from token)
3. API versioning with `/v1/`
4. RESTful conventions
5. Consistent error responses

**Rationale:**
- Versioning allows future changes without breaking clients
- JWT in header is more secure than URL
- RESTful design is familiar and well-documented
- User isolation enforced automatically

**Alternatives Considered:**
- User ID in URL (e.g., `/api/{user_id}/tasks`) - rejected: redundant and insecure
- No versioning (rejected: harder to evolve API)
- GraphQL (rejected: added complexity for Phase 2)

---

### 5. Type Safety Strategy

**Decision:** API specs are the single source of truth for type generation.

**Flow:**
```
specs/phase2/api/tasks-endpoints.md
         ↓ (generate)
    ┌────────────────┐
    ↓                ↓
frontend/types/    backend/models.py
task.ts            (Pydantic)
```

**Implementation:**
- `@type-contract-enforcer` skill generates types from specs
- Frontend uses generated TypeScript interfaces
- Backend uses Pydantic models that match spec
- Build-time validation ensures consistency

**Rationale:**
- Single source of truth prevents drift
- Specs are human-readable documentation
- Generated types reduce manual errors
- Enforces contract between frontend and backend

**Alternatives Considered:**
- Manual type maintenance (rejected: error-prone, drift over time)
- Generate from backend models (rejected: makes backend the source of truth)
- No type generation (rejected: loses type safety benefits)

---

### 6. Frontend Data Access Pattern

**Decision:** Centralized API client with enforced patterns.

**Pattern:**
```typescript
// lib/api.ts - Single API client
export const api = {
  getTasks: () => fetch('/api/v1/tasks', { headers: authHeaders }),
  createTask: (data) => fetch('/api/v1/tasks', { method: 'POST', ... }),
  // ...
}

// Components use the client
import { api } from '@/lib/api';
const tasks = await api.getTasks();
```

**Rules (enforced by `@frontend-data-enforcer` skill):**
1. NO direct `fetch()` in components
2. All API calls through centralized client
3. Consistent error handling
4. Type-safe requests/responses

**Rationale:**
- Prevents spaghetti code
- Centralized error handling and retry logic
- Easy to add interceptors (auth, logging)
- Testable (mock the client, not individual fetches)

**Alternatives Considered:**
- Direct fetch in components (rejected: unmaintainable at scale)
- Multiple API clients (rejected: inconsistent patterns)
- No enforcement (rejected: discipline relies on developers)

---

### 7. CLI Integration

**Decision:** Keep Phase 1 CLI working as standalone application.

**Approach (Option B):**
- CLI remains in `cli/` directory
- Uses in-memory storage (MemoryStorage)
- NO API calls in Phase 2
- Runs independently: `python -m src.cli.main add "test"`
- Phase 3 may convert CLI to API client

**Rationale:**
- Preserves working Phase 1 code
- Useful for manual testing
- Educational reference
- No migration burden in Phase 2

**Alternatives Considered:**
- CLI calls the API (rejected: requires auth in Phase 2)
- Remove CLI entirely (rejected: loses working code and reference)
- Merge CLI into web UI (rejected: different use cases)

---

### 8. Skills Architecture

**Decision:** Context-aware, composable skills with agent coordination.

**Tier 1 Skills (Build First):**
1. `spec-interpreter` - Read and understand spec files
2. `type-contract-enforcer` - Generate/sync types from specs
3. `database-designer` - Design schemas and migrations
4. `phase1-migrator` - Port Phase 1 code to Phase 2
5. `auth-boundary-enforcer` - Enforce auth architecture rules

**Tier 2 Skills (Build Second):**
6. `tdd-conductor` - Guide test-driven development
7. `backend-architect` - Implement FastAPI routes
8. `frontend-composer` - Build Next.js components
9. `frontend-data-enforcer` - Enforce data access patterns
10. `better-auth-integrator` - Set up authentication

**Tier 3 Skills (Build As Needed):**
11. `api-contract-guardian` - Validate API consistency
12. `test-coverage-auditor` - Verify test coverage

**Skill Design Principles:**
- **Context-aware**: Agent activates skills based on task
- **Composable**: Multiple skills per command
- **Lightweight**: Start small (10-20 lines), grow only when needed
- **Actionable**: Output guidance, not verbose reports
- **No inter-skill communication**: Agent coordinates, skills don't call each other
- **No persistent learning**: Update spec or skill file explicitly

**Rationale:**
- Simple, predictable, debuggable
- Agent handles coordination (not hidden in skills)
- Explicit updates prevent drift
- Lightweight skills are easier to maintain

**Alternatives Considered:**
- Skills call other skills (rejected: hidden complexity)
- Large, comprehensive skills (rejected: hard to maintain)
- Implicit learning (rejected: unpredictable behavior)

---

### 9. Development Workflow

**Decision:** Story-driven development with TDD (Option C).

**Flow for Each Feature:**
```
1. Feature Spec
   ↓ @spec-interpreter
2. Database Schema + API Spec (parallel)
   ↓ @database-designer + @type-contract-enforcer
3. Backend Implementation (TDD)
   ↓ @tdd-conductor + @backend-architect
4. UI Spec
   ↓ @spec-interpreter
5. Frontend Implementation (TDD)
   ↓ @tdd-conductor + @frontend-composer
6. Validation
   ↓ @api-contract-guardian + @test-coverage-auditor
```

**Local Development:**
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - CLI (anytime)
cd cli
python -m src.cli.main list
```

**Environment:**
- Shared `.env` file in root
- Separate processes (no Docker Compose required for Phase 2)

**Rationale:**
- Feature specs drive implementation
- TDD ensures quality
- Parallel backend/frontend work possible
- Simple local setup

**Alternatives Considered:**
- Top-down (spec → all implementation) - rejected: big bang approach
- Core-first (database → everything else) - rejected: backend-heavy
- Docker Compose required - rejected: adds complexity for Phase 2

---

### 10. Testing Strategy

**Decision:** Separate unit tests, NO full-stack E2E in Phase 2.

**Backend Tests:**
```
backend/tests/
├── unit/              # Route handlers, models
└── integration/       # Database operations
```
- Pytest with FastAPI TestClient
- SQLModel in-memory database for tests
- Mock JWT authentication

**Frontend Tests:**
```
frontend/tests/
├── unit/              # Components, hooks
└── e2e/               # Playwright (critical flows only)
```
- Vitest for unit tests
- React Testing Library
- Mock API client
- Playwright for critical user flows

**NO Full-Stack E2E in Phase 2:**
- Deferred to Phase 3
- Too complex for current phase
- Unit tests provide sufficient coverage

**Rationale:**
- TDD approach ensures quality
- Separate testing keeps concerns isolated
- Full-stack E2E is expensive to maintain
- Phase 2 scope is limited enough for unit tests

**Alternatives Considered:**
- Full-stack E2E (rejected: overkill for Phase 2)
- No frontend tests (rejected: loses quality)
- Combined test suite (rejected: harder to run independently)

---

### 11. Spec Organization

**Decision:** Separate specs for each phase, organized by type.

**Structure:**
```
specs/
├── phase1/            # CLI specs (preserved)
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── phase2/            # Web app specs (new)
    ├── 00-phase2-overview.md
    ├── plan.md
    ├── tasks.md
    ├── features/      # User stories
    │   └── task-crud.md
    ├── api/           # API contracts
    │   └── tasks-endpoints.md
    ├── database/      # Schema design
    │   └── schema.md
    └── ui/            # Component specs
        └── task-list.md
```

**Rationale:**
- Clear separation between phases
- Organized by type (features, API, database, UI)
- Easy for skills to locate relevant specs
- Preserves Phase 1 for reference

**Alternatives Considered:**
- Flat structure (rejected: hard to navigate)
- Combined phase specs (rejected: confusing)
- Feature-based folders (rejected: cross-cutting concerns)

---

### 12. CLAUDE.md Hierarchy

**Decision:** Layered CLAUDE.md files with specific responsibilities.

**Structure:**
```
CLAUDE.md (root)          # Monorepo navigation, skills, workflows
  ├── frontend/CLAUDE.md  # Next.js patterns
  ├── backend/CLAUDE.md   # FastAPI patterns
  └── cli/CLAUDE.md       # Phase 1 CLI (preserved)
```

**Root CLAUDE.md includes:**
- Monorepo navigation instructions
- How to use skills
- Phase-specific workflows
- References to sub-CLAUDE.md files

**Rationale:**
- Context-appropriate guidance
- Prevents overwhelming single file
- Each area has specific patterns
- Root file provides overview

---

## Technology Stack Rationale

| Technology | Rationale |
|------------|-----------|
| **Next.js 15+** | Modern React framework, App Router, server components, good DX |
| **Tailwind CSS** | Utility-first, fast development, consistent design |
| **Better Auth** | Simple auth library, JWT support, Next.js integration |
| **FastAPI** | Fast, modern Python framework, automatic API docs, async support |
| **SQLModel** | Type-safe ORM, integrates with Pydantic, FastAPI-friendly |
| **Neon PostgreSQL** | Serverless, free tier, auto-scaling, good for hackathon |
| **TypeScript** | Type safety, better DX, catches errors at compile time |
| **Pydantic** | Data validation, type safety, integrates with SQLModel |
| **Pytest** | Standard Python testing, good FastAPI support |
| **Vitest** | Fast, modern, Vite-native test runner |

---

## Consequences

### Positive

✅ Clear separation between frontend and backend
✅ Type safety across the stack
✅ Authentication handled securely with JWT
✅ Skills enforce architectural boundaries
✅ Specs drive implementation (spec-driven development)
✅ Phase 1 CLI preserved for reference
✅ Monorepo simplifies development
✅ TDD ensures quality

### Negative

⚠️ Learning curve for Better Auth + JWT flow
⚠️ Monorepo can be harder to deploy separately
⚠️ Skills require maintenance and updates
⚠️ JSONB tags may need migration if usage grows

### Risks

🔴 Better Auth configuration complexity
🔴 JWT secret sharing between frontend/backend
🔴 Skills might not catch all violations initially
🔴 Type generation tool might need iteration

### Mitigation

- Better Auth has good documentation and examples
- Use environment variables for JWT secret sharing
- Start with basic skill rules, iterate based on issues
- Manual type validation until generator is reliable

---

## Related ADRs

- [ADR-001: Storage Abstraction Layer](001-storage-abstraction-layer.md)
- [ADR-002: CLI Technology Stack](002-cli-technology-stack.md)
- [ADR-003: Date/Time Handling for Recurrence](003-date-time-handling-for-recurrence.md)

---

## References

- [Hackathon Requirements](../../Hackathon.md)
- [Phase 1 Spec](../specs/phase1/spec.md)
- [Better Auth Documentation](https://www.better-auth.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-14 | Development Team | Initial Phase 2 architecture decisions |
