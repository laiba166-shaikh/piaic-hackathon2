<!--
Sync Impact Report:
- Version change: [UNKNOWN] → 1.0.0
- Added principles: All seven core principles for Todo Phase I
- Added sections: Technical Constraints, Development Workflow, Governance
- Templates status:
  ✅ plan-template.md - No updates required (principles compatible)
  ✅ spec-template.md - No updates required (principles compatible)
  ✅ tasks-template.md - No updates required (principles compatible)
- Follow-up TODOs: None
-->

# Todo Phase I Constitution

## Core Principles

### I. Spec-Driven Development

All functionality originates from specifications created with Spec-Kit Plus. Specs define behavior, inputs, outputs, and edge cases before implementation. Claude Code is used to translate specs into code without manual boilerplate. Implementation never precedes an approved specification.

**Non-negotiable rules:**
- MUST create and approve specifications before any implementation
- Specs MUST define behavior, inputs, outputs, and edge cases
- MUST NOT begin implementation without an approved specification
- MUST use Spec-Kit Plus for all specification creation

### II. Minimal, Modular, In-Memory Design

Phase I operates entirely in memory with no persistence layer. The codebase is organized into cohesive modules implementing the five required features: Add, Delete, Update, View, and Mark Complete. State management remains isolated and predictable to support future evolution toward distributed architectures.

**Non-negotiable rules:**
- MUST operate entirely in memory (no persistence layer)
- MUST implement exactly five features: Add, Delete, Update, View, Mark Complete
- MUST organize code into cohesive modules with clear responsibilities
- MUST keep state management isolated and predictable
- MUST NOT add persistence, databases, or external state storage

### III. Test-First Workflow

Tests must be written before implementation and reflect approved specifications. The development loop follows: write test → confirm failure → implement optimal solution → refactor. Unit test coverage is mandatory for all features, and refactoring must preserve externally observable behavior.

**Non-negotiable rules:**
- MUST write tests before implementation
- MUST confirm tests fail before implementing
- MUST follow Red-Green-Refactor cycle: write test → fail → implement → refactor
- MUST achieve unit test coverage for all features
- MUST preserve externally observable behavior during refactoring
- Tests MUST reflect approved specifications

### IV. CLI-First Interaction Model

All functionality is exposed through a command-line interface. Inputs come from CLI arguments or stdin; outputs are written to stdout in human-readable or JSON formats. Errors and invalid inputs must go to stderr. The CLI defines the authoritative interaction contract.

**Non-negotiable rules:**
- MUST expose all functionality through CLI
- MUST accept inputs from CLI arguments or stdin
- MUST write outputs to stdout (human-readable or JSON)
- MUST write errors and invalid inputs to stderr
- CLI contract is authoritative; all other interfaces are derived
- MUST support both human-readable and JSON output formats

### V. Simplicity and Clean Code

Solutions must remain clear, optimal, and maintainable. No premature abstractions or unnecessary patterns are allowed. Modules must have well-defined responsibilities, predictable control flow, and readable naming. YAGNI and single-responsibility principles apply throughout.

**Non-negotiable rules:**
- MUST keep solutions clear, optimal, and maintainable
- MUST NOT create premature abstractions
- MUST NOT add unnecessary patterns or complexity
- Modules MUST have well-defined single responsibilities
- MUST use predictable control flow
- MUST use readable, self-documenting names
- MUST follow YAGNI (You Aren't Gonna Need It)
- MUST follow Single Responsibility Principle

### VI. Observability for a Console App

The application must produce predictable, testable output. Error messages must follow consistent structure. Logging, when present, must be concise and strictly scoped to debugging needs.

**Non-negotiable rules:**
- MUST produce predictable, testable output
- Error messages MUST follow consistent structure
- Logging MUST be concise when present
- Logging MUST be scoped strictly to debugging needs
- Output format MUST be deterministic for testing

### VII. Mandatory Python Type Hints

All production code must include complete Python type hints. Function signatures, return types, class attributes, and public interfaces must be fully annotated. Type hints serve as part of the contract defined by specifications and must remain synchronized with behavior and tests.

**Non-negotiable rules:**
- MUST include complete Python type hints in all production code
- Function signatures MUST be fully type-annotated (parameters and return types)
- Class attributes MUST be type-annotated
- Public interfaces MUST be fully type-annotated
- Type hints MUST remain synchronized with specifications, behavior, and tests
- MUST NOT ship code with incomplete or missing type annotations

## Technical Constraints

The following technical constraints are mandatory for Todo Phase I:

- **Package Manager**: UV is the package and environment manager
- **Python Version**: Python 3.12+ is required for all runtime and tooling
- **Specification Tool**: Specs must be authored and enforced using Spec-Kit Plus
- **Development Tool**: Development and refinement use Claude Code; manual editing is limited to logic and structure not auto-generated
- **Project Structure**: Must follow standard Python layout with separate modules and a dedicated test directory
- **Prohibited Technologies**: No persistence, web frameworks, or databases are permitted in Phase I

**Rationale**: These constraints ensure consistency, reproducibility, and alignment with project goals. UV provides deterministic dependency management. Python 3.12+ enables modern type hint features. Spec-Kit Plus enforces specification-driven development. The prohibition on persistence/databases keeps Phase I focused on core logic.

## Development Workflow

The following workflow is mandatory for all development:

1. **Define or update specifications** for each feature using Spec-Kit Plus
2. **Review and approve specifications** before any implementation steps
3. **Write failing tests** aligned with specifications
4. **Generate initial implementation** using Claude Code; refine as necessary
5. **Ensure complete type hints** in all modules and functions
6. **Verify passing tests** and apply refactoring while preserving behavior
7. **Submit code for review** with affirmation of spec compliance, type completeness, and test coverage
8. **Merge only when all quality gates pass**

**Quality Gates** (all must pass before merge):
- Specification approved and current
- Tests written before implementation
- All tests passing
- Complete type hint coverage
- Code review completed
- Behavior preserved (no regressions)

## Governance

This constitution governs all development decisions for Todo Phase I. Compliance with this constitution is mandatory for all contributions.

**Amendment Procedure**:
- Amendments require documented rationale, projected impact, and migration considerations
- Version must be incremented according to semantic versioning:
  - MAJOR: Backward incompatible governance/principle removals or redefinitions
  - MINOR: New principle/section added or materially expanded guidance
  - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
- Amendment must update all dependent templates and documentation
- All changes must be reviewed and approved before taking effect

**Compliance Review**:
- All pull requests must verify compliance with constitutional principles
- Code review must check: spec compliance, test coverage, type completeness, principle adherence
- Any deviation from principles must be explicitly justified and approved
- Unjustified complexity or principle violations must be rejected

**Supersession**:
- This constitution remains in force until superseded by the Phase II constitution
- Phase II constitution must be explicitly ratified
- Migration path from Phase I to Phase II must be documented

**Version**: 1.0.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
