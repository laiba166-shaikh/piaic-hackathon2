# ADR-002: CLI Technology Stack (Click + Rich)

> **Scope**: Integrated CLI technology stack for command parsing, validation, and visual rendering. Clustered decision covering framework (Click) and rendering library (Rich) as they work together to deliver CLI experience.

- **Status:** Accepted
- **Date:** 2025-12-10
- **Feature:** 001-phase1-cli-todo
- **Context:** Phase 1 requires professional CLI with table-based visualization, unicode/color support with ASCII fallback, command validation, and excellent testing. Need production-ready tools that integrate well and reduce implementation complexity. Must support cross-platform (Windows/macOS/Linux) and varying terminal capabilities.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Affects how all 15+ CLI commands are built, tested, and rendered. Determines developer experience and user experience.
     2) Alternatives: YES - Multiple viable stacks (Typer+Tabulate, argparse+manual ANSI, custom solutions) with different tradeoffs
     3) Scope: YES - Cross-cutting across all CLI commands, rendering, testing, terminal detection
-->

## Decision

**Use Click (CLI framework) + Rich (rendering library) as integrated CLI stack.**

**Components**:
- **CLI Framework**: Click 8.x for command parsing, validation, options, testing
- **Rendering**: Rich 13.x for table formatting, colors, terminal detection, unicode support
- **Integration**: Click commands render output via Rich Console/Table

**Rationale for Clustering**:
- Both are CLI-specific (would not use Rich for web interface)
- Both change together if CLI approach changes
- Testing strategy depends on both (Click's `CliRunner` + Rich's output validation)
- Terminal capability detection (Rich) affects command design (Click)

## Consequences

### Positive

**Click Benefits**:
- ✅ **Stability**: 10+ years production-proven (Flask, AWS CLI, Kubernetes CLI)
- ✅ **Testing**: Excellent `CliRunner` harness for integration tests
- ✅ **Validation**: Built-in type coercion (`click.Choice`, `click.INT`) and error messages
- ✅ **Ecosystem**: Widely adopted, extensive documentation, active community
- ✅ **Subcommands**: Clean command grouping (`@click.group()`)

**Rich Benefits**:
- ✅ **Auto-Detection**: Automatically detects terminal capabilities (unicode, colors) and falls back gracefully
- ✅ **Responsive**: Auto-adjusts table column widths based on terminal size
- ✅ **Unicode**: Native support for box drawing characters (╔═╗) with ASCII fallback (+--+)
- ✅ **Color**: Full RGB support with automatic ANSI fallback
- ✅ **Future-Proof**: Built-in progress bars, panels, trees for Phase 2+ features

**Integration Benefits**:
- ✅ **Consistent**: Same library (Rich) for all visual output (tables, errors, success messages)
- ✅ **DX**: Simple API - `console.print(table)` vs manual ANSI code construction
- ✅ **Cross-Platform**: Both handle Windows/macOS/Linux terminal differences

### Negative

**Click Drawbacks**:
- ⚠️ **Decorator Syntax**: Less intuitive than Typer's native type hints (learning curve)
- ⚠️ **Boilerplate**: More verbose than Typer for simple commands

**Rich Drawbacks**:
- ⚠️ **Dependency**: Adds external dependency vs manual ANSI codes (but saves 500+ lines)
- ⚠️ **Size**: Larger package than Tabulate (~1MB vs ~100KB)

**Stack Drawbacks**:
- ⚠️ **Lock-in**: If switching from CLI to TUI (terminal UI), would need to replace Rich with Textual (though Textual is built by same author)

**Mitigation**: Complexity justified by constitution requirements for clean code and professional UX. Click's stability outweighs decorator learning curve. Rich's size (1MB) negligible for CLI app.

## Alternatives Considered

### Alternative A: Typer + Tabulate

**Stack**:
- Framework: Typer (type hint-based CLI)
- Rendering: Tabulate (lightweight tables)

**Pros**:
- Typer: More Pythonic (native type hints vs decorators)
- Tabulate: Smaller footprint (~100KB)

**Cons**:
- Typer: Built on Click, adds abstraction layer without Phase 1 benefits
- Typer: Only 3 years old vs Click's 10+ years
- Tabulate: Manual terminal capability detection required
- Tabulate: Manual column width calculations
- Tabulate: Basic ANSI colors only (no RGB, no auto-detection)

**Why Rejected**: Click's stability and Rich's auto-detection outweigh Typer's type hint convenience. Spec requires unicode with fallback (FR-031-043) - Rich handles automatically, Tabulate requires manual implementation.

### Alternative B: argparse + Manual ANSI Codes

**Stack**:
- Framework: argparse (stdlib)
- Rendering: Manual ANSI escape codes

**Pros**:
- Zero external dependencies
- Maximum control over rendering

**Cons**:
- argparse: Verbose API, poor testing story, manual validation
- Manual ANSI: ~500 lines of code for table rendering, colors, terminal detection
- No unicode fallback logic (requires manual implementation)
- Maintenance burden: Team maintains rendering code vs using battle-tested library

**Why Rejected**: Violates constitution principle of using well-vetted libraries. Estimated 500+ lines of manual rendering code vs ~50 lines with Rich. Reinventing wheel contradicts clean code principles.

### Alternative C: Fire + Colorama

**Stack**:
- Framework: Fire (Google's CLI library)
- Rendering: Colorama (color support)

**Pros**:
- Fire: Auto-generates CLI from function signatures (zero boilerplate)
- Colorama: Cross-platform color support

**Cons**:
- Fire: "Magic" - hard to control, poor for complex CLIs, limited validation
- Fire: Poor testing story (no equivalent to Click's `CliRunner`)
- Colorama: Only colors, no table formatting (would still need Rich or Tabulate)
- Fire: Less adoption than Click (higher risk of abandonment)

**Why Rejected**: Fire too "magical" for production CLI with 15+ commands and validation requirements. Poor testing story conflicts with constitution's test-first requirement.

## References

- Feature Spec: `specs/001-phase1-cli-todo/spec.md` (FR-031 to FR-043: CLI Visualization Requirements)
- Implementation Plan: `specs/001-phase1-cli-todo/plan.md` (AD-002, AD-003)
- Research: `specs/001-phase1-cli-todo/research.md` (Sections 1, 2, 6)
- Constitution: `.specify/memory/constitution.md` (Principle II: Clean Code, Use well-vetted libraries)
- Click Documentation: https://click.palletsprojects.com/
- Rich Documentation: https://rich.readthedocs.io/
- Related ADRs: None

---

**Acceptance Criteria Verification**:
- ✅ Decision clusters CLI framework + rendering (integrated stack, change together)
- ✅ Explicit alternatives with pros/cons and rejection rationale
- ✅ Consequences cover both positive (stability, auto-detection) and negative (decorator syntax, dependency size)
- ✅ References link to spec requirements (FR-031-043), plan.md, research.md
