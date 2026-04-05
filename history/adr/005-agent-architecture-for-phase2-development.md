# ADR 005: Agent Architecture for Phase 2 Development

**Date**: 2025-12-21
**Status**: Accepted
**Context**: Implementing Phase 2 Full-Stack Web Application with Claude Code
**Decision Makers**: Development Team
**Phase**: 2

---

## Context

Phase 2 requires implementing a full-stack web application with multiple coordinated layers (specs, database, backend, frontend, tests). We have created 16 specialized skills to handle different aspects of development. To maximize development velocity while maintaining visibility and control, we need to define a set of focused agents that utilize these skills effectively.

**Key Requirements:**
- Maintain visibility into development progress
- Avoid "black box" agents doing too much at once
- Enable parallel work on different layers when possible
- Ensure quality gates before merging
- Support complete workflow from planning to deployment

**Available Skills (16 total):**
- Foundation: spec-interpreter, spec-architect, monorepo-coordinator, type-contract-enforcer
- Architecture: database-designer, phase1-migrator, auth-boundary-enforcer, backend-architect
- Frontend: frontend-composer, frontend-data-enforcer, better-auth-integrator
- Quality: tdd-conductor, tests-generator, test-coverage-auditor, api-contract-guardian
- Meta: skill-creator

---

## Decision

We will create **7 focused agents** organized into three phases (Planning, Implementation, Validation) to cover the complete development workflow while maintaining clear visibility and focused responsibilities.

---

## Agent Architecture

### Phase 1: Planning

#### Agent 1: Spec Writer Agent
**Purpose:** Create complete, validated specifications for new features

**Skills:**
- spec-architect (write structured specs)
- spec-interpreter (validate completeness)

**Responsibilities:**
- Create feature specifications with all required sections
- Ensure specs are clear, complete, and testable
- Validate specs before implementation begins
- Document design decisions

**When to use:**
- Planning new features
- Documenting architectural decisions
- Before any implementation work starts

---

### Phase 2: Implementation

#### Agent 2: Spec Coordinator Agent
**Purpose:** Read specs, coordinate changes, generate shared types

**Skills:**
- spec-interpreter (understand requirements)
- type-contract-enforcer (generate shared types)
- monorepo-coordinator (coordinate cross-layer changes)

**Responsibilities:**
- Read and analyze feature specifications
- Generate TypeScript/Pydantic types from specs
- Coordinate changes across monorepo boundaries
- Ensure spec authority is maintained

**When to use:**
- Start of any implementation
- After spec is approved
- Before any code changes

**Output:**
- Shared types in `shared/types/`
- Cross-layer coordination plan

---

#### Agent 3: Schema Architect Agent
**Purpose:** Design database models and migrations

**Skills:**
- database-designer (SQLModel schemas)
- phase1-migrator (port from Phase 1 if needed)

**Responsibilities:**
- Design PostgreSQL schemas with SQLModel
- Apply Phase 2 patterns (soft deletes, JSONB tags)
- Create database migrations
- Port Phase 1 models when applicable

**When to use:**
- Before backend implementation
- Database schema changes
- Adding new entities

**Output:**
- SQLModel models in `src/core/backend/models/`
- Alembic migrations
- Database indexes and constraints

---

#### Agent 4: API Developer Agent
**Purpose:** Implement FastAPI backend routes and business logic

**Skills:**
- backend-architect (FastAPI routes, dependencies)
- auth-boundary-enforcer (JWT validation, user isolation)

**Responsibilities:**
- Implement FastAPI route handlers
- Create Pydantic request/response schemas
- Enforce authentication and user isolation
- Implement business logic in service layer

**When to use:**
- Backend feature implementation
- API endpoint creation
- After database models are ready

**Output:**
- Route handlers in `src/core/backend/routers/`
- Pydantic schemas in `src/core/backend/schemas/`
- Service layer in `src/core/backend/services/`

---

#### Agent 5: UI Developer Agent
**Purpose:** Build Next.js frontend components and user flows

**Skills:**
- frontend-composer (React components, App Router)
- frontend-data-enforcer (centralized API client)
- better-auth-integrator (Better Auth setup)

**Responsibilities:**
- Create Next.js pages and components
- Implement UI/UX requirements from specs
- Enforce centralized API client usage
- Set up authentication flows

**When to use:**
- Frontend feature implementation
- UI component creation
- After backend API is ready (or mocked)

**Output:**
- Pages in `src/core/frontend/app/`
- Components in `src/core/frontend/components/`
- API client methods in `src/core/frontend/lib/api.ts`

---

#### Agent 6: Test Engineer Agent
**Purpose:** Generate comprehensive test suites for all layers

**Skills:**
- tests-generator (all test scenarios)
- tdd-conductor (TDD workflow guidance)

**Responsibilities:**
- Generate backend tests (Pytest + FastAPI)
- Generate frontend tests (Vitest + RTL)
- Cover all scenarios (happy path, validation, auth, edge cases)
- Guide TDD workflow when requested

**When to use:**
- After implementation (or during if doing TDD)
- Filling test coverage gaps
- Before PR creation

**Output:**
- Backend tests in `src/core/backend/tests/`
- Frontend tests in `src/core/frontend/tests/`
- Integration tests

---

### Phase 3: Validation

#### Agent 7: Quality Guardian Agent
**Purpose:** Validate compliance, boundaries, and test coverage before merge

**Skills:**
- api-contract-guardian (validate spec ↔ backend ↔ frontend)
- test-coverage-auditor (ensure adequate tests)
- auth-boundary-enforcer (verify user isolation)
- monorepo-coordinator (check boundaries)

**Responsibilities:**
- Validate API consistency across all layers
- Audit test coverage against acceptance criteria
- Verify authentication boundaries and user isolation
- Check monorepo import rules and boundaries

**When to use:**
- Before creating PRs
- Code review validation
- Pre-deployment checks

**Output:**
- Validation report
- List of violations and fixes
- Coverage gaps identified

---

## Workflow Integration

### Typical Feature Implementation Flow

```
1. Planning Phase
   └─ Spec Writer Agent
      → Creates specs/phase2/features/[feature].md
      → Validates completeness

2. Implementation Phase (Sequential or Parallel)

   2.1 Coordination (Always First)
       └─ Spec Coordinator Agent
          → Reads spec
          → Generates shared/types/
          → Plans cross-layer changes

   2.2 Database Layer
       └─ Schema Architect Agent
          → Creates src/core/backend/models/
          → Generates migrations

   2.3 Backend Layer (After 2.2)
       └─ API Developer Agent
          → Implements src/core/backend/routers/
          → Creates src/core/backend/schemas/

   2.4 Frontend Layer (After 2.3 or parallel with mocks)
       └─ UI Developer Agent
          → Creates src/core/frontend/app/
          → Builds src/core/frontend/components/

   2.5 Test Layer (After 2.3 and 2.4, or TDD throughout)
       └─ Test Engineer Agent
          → Generates src/core/backend/tests/
          → Generates src/core/frontend/tests/

3. Validation Phase (Always Last)
   └─ Quality Guardian Agent
      → Validates all contracts
      → Audits test coverage
      → Checks boundaries
      → Approves for PR
```

---

## Rationale

### Why 7 Agents?

**Clear Separation of Concerns:**
- Each agent has 2-3 skills maximum
- Focused, understandable responsibilities
- Easy to debug and understand what went wrong

**Visibility:**
- User sees exactly what each agent is doing
- Can stop/modify at each stage
- Not a "black box" mega-agent

**Flexibility:**
- Can run agents independently
- Can parallelize some agents (frontend + backend)
- Can skip agents if not needed (e.g., no DB changes)

**Quality Gates:**
- Spec validation before implementation
- Coordination before coding
- Quality guardian before merge

### Why Not Fewer Agents?

**Original "Feature Builder" Agent (Rejected):**
- Combined agents 2-6 into one
- Too much responsibility
- Lost visibility into progress
- Harder to stop/modify mid-flow

**Pros:** Faster for simple features
**Cons:** Black box, hard to debug, lost visibility
**Decision:** User feedback - "I will lose the visibility of the work"

### Why Not More Agents?

**Could split further (Not chosen):**
- Separate agent for each skill (16 agents)
- Too granular, context switching overhead
- Harder to coordinate

**Current balance:**
- Enough agents for visibility
- Not so many that coordination is complex

---

## Skill Coverage

**All 16 Skills Mapped:**

| Agent | Skills | Count |
|-------|--------|-------|
| Spec Writer | spec-architect, spec-interpreter | 2 |
| Spec Coordinator | spec-interpreter, type-contract-enforcer, monorepo-coordinator | 3 |
| Schema Architect | database-designer, phase1-migrator | 2 |
| API Developer | backend-architect, auth-boundary-enforcer | 2 |
| UI Developer | frontend-composer, frontend-data-enforcer, better-auth-integrator | 3 |
| Test Engineer | tests-generator, tdd-conductor | 2 |
| Quality Guardian | api-contract-guardian, test-coverage-auditor, auth-boundary-enforcer, monorepo-coordinator | 4 |

**Note:** Some skills used by multiple agents:
- spec-interpreter: Spec Writer + Spec Coordinator (different purposes)
- auth-boundary-enforcer: API Developer (implementation) + Quality Guardian (validation)
- monorepo-coordinator: Spec Coordinator (planning) + Quality Guardian (validation)

---

## Alternatives Considered

### Alternative 1: Mega Agent
**Description:** Single agent with all 16 skills

**Pros:**
- One command does everything
- Fastest for simple features

**Cons:**
- Black box - no visibility
- Hard to debug failures
- Can't customize workflow
- All-or-nothing approach

**Decision:** Rejected - user feedback on losing visibility

---

### Alternative 2: Layer-Based Agents (3 agents)
**Description:** Backend Agent, Frontend Agent, Quality Agent

**Pros:**
- Simple to understand
- Matches architecture layers

**Cons:**
- Still too coarse-grained
- Lost coordination step
- Database + API combined (too much)
- No separate spec planning

**Decision:** Rejected - not enough granularity

---

### Alternative 3: Skill-Per-Agent (16 agents)
**Description:** One agent per skill

**Pros:**
- Maximum flexibility
- Clear 1:1 mapping

**Cons:**
- Too many agents to manage
- Excessive context switching
- Coordination overhead
- User has to orchestrate everything

**Decision:** Rejected - too granular

---

## Consequences

### Positive

**Development Velocity:**
- Clear workflow from spec to deployment
- Agents can run in parallel where possible
- Automated test generation

**Quality:**
- Mandatory spec validation
- Quality gates before merge
- Comprehensive test coverage

**Visibility:**
- See exactly what each agent does
- Can stop/modify at each step
- Understand where issues occur

**Maintainability:**
- Each agent has clear purpose
- Easy to update individual agents
- Skills can be improved independently

### Negative

**Coordination Overhead:**
- Need to run multiple agents
- Must understand workflow order
- More commands than mega-agent

**Mitigation:** Create helper scripts or workflows that chain agents for common scenarios

**Learning Curve:**
- Users need to understand 7 agents
- Must know when to use which agent

**Mitigation:** This ADR + documentation, workflow examples

---

## Success Criteria

This architecture will be considered successful if:

1. **Velocity:** Features go from spec to tested code in < 1 day
2. **Quality:** All PRs pass Quality Guardian validation
3. **Visibility:** Team can see and control each implementation step
4. **Adoption:** Team prefers agents over manual implementation
5. **Coverage:** All 16 skills used regularly in workflow

---

## Future Considerations

### Potential Enhancements

**Workflow Automation:**
- Create meta-workflows that chain agents for common patterns
- Example: "Full Feature Flow" = Spec Writer → Spec Coordinator → Schema → API → UI → Test → Quality Guardian

**Agent Composition:**
- Allow users to compose custom agent chains
- Save frequently used combinations

**Parallel Execution:**
- Enable API Developer + UI Developer to run simultaneously with mocked backend
- Coordinate merge at the end

**Interactive Mode:**
- Agents pause for user approval between steps
- Show preview of changes before applying

---

## Review and Updates

**Review Schedule:** After every 5 features implemented using agents

**Update Triggers:**
- If agents consistently need to be run in unexpected order
- If visibility is still insufficient
- If new skills are added
- If user feedback suggests changes

**Next Review:** After Phase 2 MVP completion

---

## References

- ADR 004: Phase 2 Full-Stack Architecture
- `.claude/skills/` - All 16 skill definitions
- Phase 2 Specs: `specs/phase2/`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-21 | Create 7 focused agents | Balance between visibility and automation |
| 2025-12-21 | Reject mega-agent approach | User feedback: "I will lose the visibility of the work" |
| 2025-12-21 | Use 3-phase workflow | Clear separation: Planning → Implementation → Validation |
