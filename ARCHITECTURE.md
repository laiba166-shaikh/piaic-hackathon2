# Evolution of Todo - Multi-Phase Architecture

**Version:** 1.0.0
**Last Updated:** 2025-12-09

## Architecture Philosophy

This project demonstrates **progressive enhancement** through 5 phases while maintaining **independent runnable interfaces**. Each phase adds new capabilities without breaking previous phases.

## Core Principles

1. **Shared Core Logic** - One source of truth for Task business logic
2. **Interface Independence** - CLI, Web, and Chatbot can run simultaneously
3. **Storage Abstraction** - Clean separation between business logic and persistence
4. **Phase Preservation** - Any phase can be demonstrated at any time

## Project Structure

```
hackathon2/
├── .specify/
│   ├── memory/
│   │   └── constitution.md         # Project governance
│   └── templates/                   # Spec-Kit templates
│
├── specs/                           # Spec-Driven Development specs
│   ├── phase1-cli/
│   │   ├── spec.md                 # CLI requirements
│   │   ├── plan.md                 # CLI implementation plan
│   │   └── tasks.md                # CLI tasks
│   ├── phase2-web/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
│   ├── phase3-chatbot/
│   ├── phase4-k8s/
│   └── phase5-cloud/
│
├── src/
│   ├── core/                        # Shared business logic (ALL PHASES)
│   │   ├── __init__.py
│   │   ├── models.py               # Task, User models
│   │   ├── services.py             # TaskService (CRUD operations)
│   │   ├── exceptions.py           # Custom exceptions
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── base.py             # ITaskStorage interface
│   │       ├── memory.py           # Phase 1: In-memory storage
│   │       └── database.py         # Phase 2+: PostgreSQL storage
│   │
│   ├── cli/                         # Phase 1: Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py                 # CLI entry point
│   │   └── commands.py             # CLI command handlers
│   │
│   ├── web/                         # Phase 2: Web application
│   │   ├── backend/
│   │   │   ├── main.py             # FastAPI entry point
│   │   │   ├── api/
│   │   │   │   └── routes.py       # REST endpoints
│   │   │   └── auth/
│   │   │       └── jwt.py          # Better Auth integration
│   │   └── frontend/
│   │       └── (Next.js app)
│   │
│   └── chatbot/                     # Phase 3: AI-powered chatbot
│       ├── mcp_server/             # MCP tools
│       │   ├── main.py
│       │   └── tools.py
│       └── agents/
│           └── todo_agent.py       # OpenAI Agents SDK
│
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile.cli
│   │   ├── Dockerfile.web
│   │   └── Dockerfile.chatbot
│   ├── phase4-minikube/            # Phase 4: Local Kubernetes
│   │   ├── helm/
│   │   └── manifests/
│   └── phase5-cloud/               # Phase 5: Cloud deployment
│       ├── helm/
│       ├── kafka/
│       └── dapr/
│
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_storage.py
│   ├── integration/
│   │   ├── test_cli.py
│   │   ├── test_api.py
│   │   └── test_chatbot.py
│   └── contract/
│       └── test_mcp_tools.py
│
├── history/
│   ├── prompts/                    # Prompt History Records
│   │   ├── constitution/
│   │   ├── phase1-cli/
│   │   ├── phase2-web/
│   │   └── ...
│   └── adr/                        # Architecture Decision Records
│
├── .env.example                    # Environment variables template
├── pyproject.toml                  # Python dependencies (UV)
├── ARCHITECTURE.md                 # This file
├── CLAUDE.md                       # Claude Code instructions
├── README.md                       # Project overview
└── constitution.md -> .specify/memory/constitution.md
```

## Phase Evolution Strategy

### Phase 1: CLI with In-Memory Storage

**Entry Point:** `python -m src.cli.main`

```python
# src/cli/main.py
from src.core.services import TaskService
from src.core.storage.memory import MemoryStorage

def main():
    storage = MemoryStorage()
    service = TaskService(storage)
    # CLI commands...
```

**Features:**
- Add, Delete, Update, View, Mark Complete tasks
- In-memory storage (data lost on exit)
- Pure Python, no external dependencies

**Deliverable:** Working CLI app with full CRUD operations

---

### Phase 2: Web Application with Database

**Entry Points:**
- CLI: `python -m src.cli.main` (still works with memory storage)
- Web Backend: `python -m src.web.backend.main`
- Web Frontend: `cd src/web/frontend && npm run dev`

```python
# src/web/backend/main.py
from src.core.services import TaskService
from src.core.storage.database import DatabaseStorage

def create_app():
    storage = DatabaseStorage(connection_string=os.getenv("DATABASE_URL"))
    service = TaskService(storage)
    # FastAPI routes...
```

**New Features:**
- RESTful API with FastAPI
- Next.js frontend
- PostgreSQL (Neon) persistence
- Multi-user support with Better Auth
- JWT authentication

**Phase 1 Preservation:**
- CLI still runnable with: `python -m src.cli.main`
- CLI can optionally use DB: `python -m src.cli.main --storage=database`

**Deliverable:** Full-stack web app + working CLI

---

### Phase 3: AI Chatbot with MCP

**Entry Points:**
- CLI: `python -m src.cli.main` ✅
- Web: `python -m src.web.backend.main` ✅
- Chatbot: `python -m src.chatbot.mcp_server.main`

```python
# src/chatbot/mcp_server/tools.py
from src.core.services import TaskService
from src.core.storage.database import DatabaseStorage

def create_mcp_tools():
    storage = DatabaseStorage(...)
    service = TaskService(storage)
    # MCP tool wrappers around service methods...
```

**New Features:**
- OpenAI ChatKit UI
- MCP server exposing task operations
- OpenAI Agents SDK for AI logic
- Natural language task management
- Stateless chat endpoint with DB conversation storage

**Phase 1 & 2 Preservation:**
- CLI: Still works ✅
- Web App: Still works ✅
- Chatbot: New interface using same core logic

**Deliverable:** AI chatbot + web app + CLI all functional

---

### Phase 4: Local Kubernetes Deployment

**Focus:** Containerization and local orchestration

**Changes:**
- Dockerize all three interfaces
- Create Helm charts
- Deploy to Minikube
- Use kubectl-ai and kagent for operations

**Phase 1-3 Preservation:**
- All interfaces still work locally
- Now also work in Kubernetes pods
- Can demo CLI: `kubectl exec -it cli-pod -- python -m src.cli.main`

---

### Phase 5: Cloud Deployment with Advanced Features

**New Features:**
- Recurring tasks, due dates, reminders
- Priorities, tags, search, filter, sort
- Kafka for event-driven architecture
- Dapr for distributed runtime
- Deploy to DigitalOcean/GKE/AKS

**Phase 1-4 Preservation:**
- All interfaces still work ✅
- All deployment modes still work ✅
- Advanced features enhance all interfaces

---

## Storage Abstraction (Critical for Phase Independence)

### Interface Definition

```python
# src/core/storage/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models import Task

class ITaskStorage(ABC):
    """Abstract interface for task storage."""

    @abstractmethod
    def create(self, task: Task) -> Task:
        """Create a new task."""
        pass

    @abstractmethod
    def get(self, task_id: int, user_id: str) -> Optional[Task]:
        """Get a task by ID."""
        pass

    @abstractmethod
    def list(self, user_id: str, status: Optional[str] = None) -> List[Task]:
        """List all tasks for a user."""
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update an existing task."""
        pass

    @abstractmethod
    def delete(self, task_id: int, user_id: str) -> bool:
        """Delete a task."""
        pass
```

### Implementations

**Phase 1: Memory Storage**
```python
# src/core/storage/memory.py
class MemoryStorage(ITaskStorage):
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._counter = 0

    def create(self, task: Task) -> Task:
        self._counter += 1
        task.id = self._counter
        self._tasks[task.id] = task
        return task
    # ... other methods
```

**Phase 2+: Database Storage**
```python
# src/core/storage/database.py
class DatabaseStorage(ITaskStorage):
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

    def create(self, task: Task) -> Task:
        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
    # ... other methods
```

## Configuration Strategy

```python
# src/core/config.py
from enum import Enum

class StorageType(Enum):
    MEMORY = "memory"
    DATABASE = "database"

def get_storage(storage_type: StorageType = None):
    """Factory function to get appropriate storage."""
    if storage_type is None:
        storage_type = os.getenv("STORAGE_TYPE", "memory")

    if storage_type == StorageType.MEMORY:
        return MemoryStorage()
    elif storage_type == StorageType.DATABASE:
        return DatabaseStorage(os.getenv("DATABASE_URL"))
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
```

## Running Different Phases

### Phase 1 (CLI only, in-memory)
```bash
# Set storage to memory
export STORAGE_TYPE=memory

# Run CLI
python -m src.cli.main
```

### Phase 2+ (CLI with database)
```bash
# Set storage to database
export STORAGE_TYPE=database
export DATABASE_URL=postgresql://...

# Run CLI (now uses DB)
python -m src.cli.main

# Or run web app
python -m src.web.backend.main
```

### Phase 3+ (All interfaces)
```bash
# Terminal 1: CLI
python -m src.cli.main

# Terminal 2: Web Backend
python -m src.web.backend.main

# Terminal 3: Web Frontend
cd src/web/frontend && npm run dev

# Terminal 4: Chatbot MCP Server
python -m src.chatbot.mcp_server.main
```

## Demo Strategy for Hackathon Judges

### 90-Second Demo Video Script

```
0:00-0:15: "Phase 1 - CLI App"
  → Show: python -m src.cli.main
  → Demo: Add task, list tasks, mark complete

0:15-0:30: "Phase 2 - Web App"
  → Show: Browser with Next.js UI
  → Demo: Same operations via web interface

0:30-0:45: "Phase 3 - AI Chatbot"
  → Show: ChatKit interface
  → Demo: "Add a task to buy groceries"

0:45-1:00: "Phase 4 - Kubernetes"
  → Show: kubectl get pods
  → Demo: All three interfaces running in K8s

1:00-1:15: "Phase 5 - Cloud + Advanced Features"
  → Show: DigitalOcean dashboard
  → Demo: Recurring tasks, Kafka events

1:15-1:30: "All Phases Still Work!"
  → Show: Split screen - CLI, Web, Chatbot all working simultaneously
  → Text overlay: "Shared core, multiple interfaces, clean architecture"
```

## Testing Strategy

### Unit Tests (Test Core Logic)
```python
# tests/unit/test_services.py
def test_task_service_with_memory_storage():
    storage = MemoryStorage()
    service = TaskService(storage)
    task = service.create_task(title="Test", user_id="user1")
    assert task.id is not None

def test_task_service_with_database_storage():
    storage = DatabaseStorage(test_db_url)
    service = TaskService(storage)
    task = service.create_task(title="Test", user_id="user1")
    assert task.id is not None
```

### Integration Tests (Test Interfaces)
```python
# tests/integration/test_cli.py
def test_cli_add_command():
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "add", "Buy milk"],
        capture_output=True
    )
    assert "Task added" in result.stdout.decode()
```

## Benefits of This Architecture

| Aspect | Benefit |
|--------|---------|
| **Constitution Compliance** | ✅ Clean Code, Modularity, Scalability principles enforced |
| **Spec-Driven** | ✅ Each phase has its own spec, all use same core |
| **Test-First** | ✅ Core logic tests work across all phases |
| **Phase Independence** | ✅ Can demo any phase at any time |
| **Code Reuse** | ✅ 80% code sharing, 20% interface-specific |
| **Maintainability** | ✅ Bug fix in core fixes all interfaces |
| **Hackathon Demo** | ✅ Show evolution without losing previous work |

## Next Steps

1. ✅ Constitution established
2. 🔄 Create Phase 1 specification
3. Implement Phase 1 (CLI + Core + Tests)
4. Create Phase 2 specification
5. Add Web interface (reuse core)
6. ... continue through Phase 5

---

**Key Insight:** This architecture demonstrates that you understand **real software engineering** - not just cobbling together features, but designing systems that scale, evolve, and maintain quality across growth.
