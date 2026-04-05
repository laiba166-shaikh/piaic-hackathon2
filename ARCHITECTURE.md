# Evolution of Todo - Multi-Phase Architecture

**Version:** 2.0.0
**Last Updated:** 2026-04-05

## Architecture Philosophy

This project demonstrates **progressive enhancement** through 5 phases while maintaining **independent runnable interfaces**. Each phase adds new capabilities without breaking previous phases.

## Core Principles

1. **Phase Self-Containment** - Each phase owns its own business logic; no shared coupling across phases
2. **Interface Independence** - CLI, Web, and Chatbot can run simultaneously
3. **Storage Abstraction** - Clean separation between business logic and persistence
4. **Phase Preservation** - Any phase can be demonstrated at any time

## Project Structure

```
hackathon2/
├── .specify/
│   ├── memory/
│   │   └── constitution.md              # Project governance
│   └── templates/                        # Spec-Kit templates
│
├── specs/                                # Spec-Driven Development specs
│   ├── 001-phase1-cli-todo/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── contracts/
│   │       └── storage.py               # ITaskStorage contract
│   ├── 002-phase2-fullstack-web/
│   │   ├── 00-phase2-overview.md
│   │   └── features/
│   │       ├── 01-user-authentication.md
│   │       ├── 02-task-crud.md
│   │       └── ...
│   ├── 003-phase3-chatbot/
│   ├── 004-phase4-k8s/
│   └── 005-phase5-cloud/
│
├── src/
│   ├── cli/                             # Phase 1: CLI application
│   │   ├── main.py                      # CLI entry point (Click)
│   │   ├── interactive.py               # Interactive shell mode
│   │   ├── commands/
│   │   │   ├── basic.py                 # add, list, done, undone, update, delete
│   │   │   └── intermediate.py          # search, filter, sort
│   │   ├── rendering/
│   │   │   ├── table.py                 # Rich table rendering
│   │   │   └── colors.py                # Priority/status color mapping
│   │   ├── logics/                      # Business logic (CLI-local)
│   │   │   ├── models.py                # Task, Priority, Recurrence (dataclasses)
│   │   │   ├── services.py              # TaskService
│   │   │   ├── exceptions.py            # TaskNotFoundError, ValidationError
│   │   │   ├── validators.py            # parse_tags, parse_due_date
│   │   │   ├── recurring.py             # calculate_next_occurrence
│   │   │   └── storage/
│   │   │       ├── base.py              # ITaskStorage abstract interface
│   │   │       └── memory.py            # MemoryStorage (in-memory, Phase 1)
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── contract/
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── core/                            # Phase 2+: Web application
│   │   ├── backend/                     # FastAPI backend
│   │   │   ├── main.py                  # FastAPI entry point
│   │   │   ├── api/v1/tasks.py          # CRUD endpoints
│   │   │   ├── models/task.py           # SQLModel DB model (user_id, soft delete)
│   │   │   ├── dependencies.py          # JWT auth, DB session
│   │   │   ├── db.py                    # SQLModel engine + session
│   │   │   ├── config.py                # Settings (DATABASE_URL, JWT_SECRET)
│   │   │   ├── migrations/              # Alembic migrations
│   │   │   ├── tests/
│   │   │   ├── pyproject.toml
│   │   │   └── .env.example
│   │   │
│   │   ├── frontend/                    # Next.js frontend
│   │   │   ├── app/                     # App Router
│   │   │   │   ├── (auth)/              # Login / Register pages
│   │   │   │   ├── (dashboard)/         # Protected dashboard
│   │   │   │   └── api/auth/            # Better Auth route handler
│   │   │   ├── components/
│   │   │   │   ├── auth/                # LoginForm, RegisterForm
│   │   │   │   └── tasks/               # TaskList, TaskForm, TaskCard
│   │   │   ├── contexts/
│   │   │   │   └── AuthProvider.tsx     # JWT session context
│   │   │   ├── lib/
│   │   │   │   ├── api.ts               # Centralized fetch wrapper (NEXT_PUBLIC_API_URL)
│   │   │   │   ├── auth.ts              # Better Auth server config
│   │   │   │   └── auth-client.ts       # Better Auth client config
│   │   │   ├── hooks/
│   │   │   ├── types/
│   │   │   ├── middleware.ts            # Auth route protection
│   │   │   ├── package.json
│   │   │   └── CLAUDE.md
│   │   │
│   │   └── shared/
│   │       └── types/
│   │           └── task.ts              # Shared TypeScript types
│   │
│   └── config.py                        # Root config (APP_NAME, logging)
│
├── history/
│   ├── prompts/                         # Prompt History Records (PHRs)
│   │   ├── constitution/
│   │   ├── 001-phase1-cli-todo/
│   │   ├── 002-phase2-fullstack-web/
│   │   └── general/
│   └── adr/                             # Architecture Decision Records
│
├── .env.example                         # Environment variables template
├── ARCHITECTURE.md                      # This file
├── CLAUDE.md                            # Claude Code instructions
└── README.md                            # Project overview
```

## Phase Evolution Strategy

### Phase 1: CLI with In-Memory Storage

**Entry Point:** `python -m src.cli.main`

```python
# src/cli/main.py
from src.cli.logics.storage.memory import MemoryStorage
from src.cli.logics.services import TaskService

storage = MemoryStorage()
service = TaskService(storage)
```

**Features:**
- Add, delete, update, view, mark complete/incomplete tasks
- Priority levels (high/medium/low), tags, due dates, recurring tasks
- Search, filter, sort
- In-memory storage (data lost on exit — use interactive mode)
- Rich table-based UI with color indicators

**Run:**
```bash
cd hackathon2
uv pip install -e src/cli
python -m src.cli.main          # interactive mode
python -m src.cli.main --help   # one-shot commands
```

---

### Phase 2: Full-Stack Web Application

**Entry Points:**
- Backend: `cd src/core/backend && uvicorn main:app --reload`
- Frontend: `cd src/core/frontend && npm run dev`
- CLI: `python -m src.cli.main` (still works independently)

```python
# src/core/backend/main.py
from fastapi import FastAPI
from src.core.backend.api.v1.tasks import router

app = FastAPI()
app.include_router(router)
```

**New Features:**
- RESTful API (`/api/v1/tasks`) with FastAPI
- Next.js App Router frontend
- PostgreSQL (Neon) persistence via SQLModel + Alembic
- Multi-user support with per-user task isolation
- Better Auth + EdDSA JWT authentication
- JWKS-based token verification

**Environment Variables (src/core/backend/.env):**
```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET=your-secret-key-at-least-32-chars
DEBUG=False
```

**Frontend Environment (src/core/frontend/.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Deployment:**
- Backend → Railway / Render (set env vars, run `alembic upgrade head`)
- Frontend → Vercel (set root dir to `src/core/frontend`, set `NEXT_PUBLIC_API_URL`)

---

### Phase 3: AI Chatbot with MCP

**Entry Points:**
- CLI: `python -m src.cli.main` ✅
- Backend: `uvicorn main:app --reload` ✅
- Frontend: `npm run dev` ✅
- Chatbot: `python -m chatbot.mcp_server.main`

**New Features:**
- MCP server exposing task operations as tools
- OpenAI Agents SDK for AI reasoning
- Natural language task management
- Stateless chat endpoint with DB conversation storage

---

### Phase 4: Local Kubernetes Deployment

**Focus:** Containerization and local orchestration

- Dockerize all interfaces
- Helm charts + Minikube deployment
- kubectl-ai and kagent for operations

```bash
kubectl exec -it cli-pod -- python -m src.cli.main
```

---

### Phase 5: Cloud Deployment with Advanced Features

**New:**
- Kafka for event-driven architecture
- Dapr for distributed runtime
- Deploy to DigitalOcean / GKE / AKS

---

## Storage Abstraction

The CLI uses a typed abstract interface to allow swapping storage backends:

```python
# src/cli/logics/storage/base.py
class ITaskStorage(ABC):
    @abstractmethod
    def create(self, task: Task) -> Task: ...
    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]: ...
    @abstractmethod
    def list_all(self) -> List[Task]: ...
    @abstractmethod
    def update(self, task: Task) -> Task: ...
    @abstractmethod
    def delete(self, task_id: int) -> bool: ...
```

| Phase | Storage | Location |
|---|---|---|
| Phase 1 | `MemoryStorage` (dict, in-memory) | `src/cli/logics/storage/memory.py` |
| Phase 2+ | SQLModel + PostgreSQL | `src/core/backend/models/task.py` |

The backend does **not** reuse the CLI storage layer — it owns its own SQLModel model with `user_id`, soft delete (`deleted_at`), and Alembic migrations.

---

## Running All Phases

### Phase 1 (CLI only)
```bash
python -m src.cli.main
```

### Phase 2 (Full-Stack Web)
```bash
# Terminal 1 — Backend
cd src/core/backend && uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd src/core/frontend && npm run dev

# Terminal 3 — CLI (independent)
python -m src.cli.main
```

### Phase 3+ (All interfaces)
```bash
# Terminal 1 — CLI
python -m src.cli.main

# Terminal 2 — Backend
cd src/core/backend && uvicorn main:app --reload

# Terminal 3 — Frontend
cd src/core/frontend && npm run dev

# Terminal 4 — Chatbot
python -m chatbot.mcp_server.main
```

---

## Architecture Benefits

| Aspect | Benefit |
|---|---|
| **Phase Self-Containment** | ✅ `src/cli/logics/` is fully owned by Phase 1 — no cross-phase coupling |
| **Spec-Driven** | ✅ Each phase has its own spec under `specs/` |
| **Test-First** | ✅ Unit, integration, and contract tests per phase |
| **Phase Independence** | ✅ Any phase can be demonstrated at any time |
| **Deployment Clarity** | ✅ Backend → Railway/Render, Frontend → Vercel, CLI → local |
| **Maintainability** | ✅ Changes to CLI logic don't affect web backend and vice versa |
| **Hackathon Demo** | ✅ Show evolution without losing previous work |

---

**Key Insight:** This architecture demonstrates real software engineering — designing systems that scale, evolve, and maintain quality across growth. Each phase is independently runnable, testable, and deployable.
