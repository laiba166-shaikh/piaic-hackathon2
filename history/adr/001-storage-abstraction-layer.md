# ADR-001: Storage Abstraction Layer for Phase Evolution

> **Scope**: Architectural pattern for isolating storage implementation from business logic to enable zero-rewrite migration from in-memory (Phase 1) to database (Phase 2+).

- **Status:** Accepted
- **Date:** 2025-12-10
- **Feature:** 001-phase1-cli-todo
- **Context:** Building a multi-phase todo application that evolves from CLI (Phase 1) → Web (Phase 2) → AI Chatbot (Phase 3) → Kubernetes (Phase 4) → Cloud (Phase 5). Phase 1 uses in-memory storage, but Phase 2+ requires PostgreSQL persistence. We need an architecture that allows storage migration without rewriting core business logic (TaskService).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Affects core architecture across all 5 phases, determines how business logic interacts with storage
     2) Alternatives: YES - Direct dict access, Repository pattern, DAO pattern all viable with different tradeoffs
     3) Scope: YES - Cross-cutting concern affecting TaskService, all CLI commands, future web API, future chatbot
-->

## Decision

**Use Strategy Pattern with `ITaskStorage` abstract interface to decouple business logic from storage implementation.**

**Components**:
- **Interface**: `ITaskStorage` (ABC) defining contract: `create()`, `get()`, `list_all()`, `update()`, `delete()`
- **Phase 1 Implementation**: `MemoryStorage` (dict-based, in-memory)
- **Phase 2+ Implementation**: `DatabaseStorage` (SQLModel + Neon PostgreSQL)
- **Business Logic**: `TaskService` depends only on `ITaskStorage` interface, not concrete implementations

**Pattern**: Strategy pattern (behavioral design pattern for swappable algorithms/implementations)

**Key Principle**: Dependency Inversion - high-level `TaskService` depends on abstraction (`ITaskStorage`), not concretions (`MemoryStorage`/`DatabaseStorage`)

## Consequences

### Positive

- **Zero Core Logic Changes**: `TaskService` unchanged between Phase 1 and Phase 2 - only swap `MemoryStorage` for `DatabaseStorage` at initialization
- **Testability**: Business logic can be tested with mock storage (fast unit tests without I/O)
- **Contract Tests**: `ITaskStorage` contract tests in Phase 1 validate that Phase 2 `DatabaseStorage` will comply
- **Phase Independence**: CLI can run with in-memory OR database via environment variable (demo flexibility)
- **Future-Proof**: Phase 3 chatbot and Phase 4 K8s reuse exact same core logic and storage interface
- **Clean Architecture**: Enforces separation of concerns - business logic isolated from infrastructure

### Negative

- **Initial Complexity**: Adds abstraction layer for Phase 1 when simple dict would work
- **Learning Curve**: Team must understand Strategy pattern and dependency injection
- **Over-Engineering Risk**: If project never reaches Phase 2, abstraction was unnecessary
- **Testing Overhead**: Must test both interface contract AND concrete implementations

**Mitigation**: Complexity justified by constitution requirement for scalability and phase evolution. Contract tests in Phase 1 pay off in Phase 2+ by catching interface violations early.

## Alternatives Considered

### Alternative A: Direct Dict Access in TaskService

```python
class TaskService:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}  # Direct dict

    def create_task(self, task: Task) -> Task:
        self._counter += 1
        task.id = self._counter
        self._tasks[task.id] = task
        return task
```

**Why Rejected**:
- Phase 2 migration requires **rewriting entire `TaskService`**
- All business logic methods (`create_task`, `search_tasks`, `filter_tasks`, etc.) must change from dict operations to database queries
- Cannot reuse Phase 1 core logic in Phase 2+ web/chatbot
- Violates Open/Closed Principle (open for extension, closed for modification)
- **Estimated rework**: 500-800 lines of business logic rewritten

### Alternative B: Repository Pattern (DDD)

```python
class TaskRepository:
    def save(self, task: Task) -> None: pass
    def find_by_id(self, id: int) -> Task: pass
    def find_all(self) -> List[Task]: pass
    # + aggregate root, unit of work, etc.
```

**Why Rejected**:
- **Over-engineering** for simple CRUD operations (violates YAGNI - You Aren't Gonna Need It)
- Repository pattern designed for complex domain models with aggregate roots, entities, value objects
- Our `Task` is a simple data entity, not a complex aggregate
- Additional concepts: Unit of Work, Aggregate Root, Domain Events - unnecessary complexity for Phase 1 scope
- **Estimated overhead**: 300+ lines of repository infrastructure vs 150 lines for Strategy pattern

### Alternative C: DAO (Data Access Object) Pattern

```python
class TaskDAO:
    def insert(self, task: Task) -> int: pass
    def select_by_id(self, id: int) -> Task: pass
    def select_all(self) -> List[Task]: pass
    def update(self, task: Task) -> None: pass
    def delete(self, id: int) -> None: pass
```

**Why Rejected**:
- DAO is essentially same as our `ITaskStorage` but with legacy naming (insert/select vs create/get)
- No meaningful difference in architecture
- Strategy pattern + modern naming (`ITaskStorage`) more Pythonic

## References

- Feature Spec: `specs/001-phase1-cli-todo/spec.md`
- Implementation Plan: `specs/001-phase1-cli-todo/plan.md` (AD-001)
- Storage Contract: `specs/001-phase1-cli-todo/contracts/storage.py`
- Research: `specs/001-phase1-cli-todo/research.md` (Section 1)
- Constitution: `.specify/memory/constitution.md` (Principle II: Clean Code, Modularity, Scalability)
- Related ADRs: ADR-003 (Date/Time Handling - also affects storage for due_date field)

---

**Acceptance Criteria Verification**:
- ✅ Decision clusters storage abstraction components (interface, implementations, pattern)
- ✅ Explicit alternatives listed with rejection rationale and rework estimates
- ✅ Consequences cover positive (zero-rewrite, testability) and negative (complexity, over-engineering risk)
- ✅ References link to plan.md, contracts, constitution
