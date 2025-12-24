---
id: 003
title: User Authentication Planning
stage: plan
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-phase2-fullstack-web
branch: 002-phase2-fullstack-web
user: system
command: /sp.plan
labels: ["authentication", "better-auth", "jwt", "planning", "phase2"]
links:
  spec: specs/002-phase2-fullstack-web/features/01-user-authentication.md
  ticket: null
  adr: history/adr/004-phase2-fullstack-architecture.md
  pr: null
files:
  - specs/002-phase2-fullstack-web/features/plan.md
  - specs/002-phase2-fullstack-web/features/research.md
  - specs/002-phase2-fullstack-web/features/data-model.md
  - specs/002-phase2-fullstack-web/features/contracts/jwt-validation.md
  - specs/002-phase2-fullstack-web/features/contracts/better-auth-flow.md
  - specs/002-phase2-fullstack-web/features/quickstart.md
tests:
  - No tests created during planning phase
---

## Prompt

Execute the implementation planning workflow using the plan template to generate design artifacts for the User Authentication feature (01-user-authentication.md).

This is the first feature of Phase 2 (Full-Stack Web Application) and establishes the authentication foundation using Better Auth on the frontend and JWT validation on the backend. The planning workflow should follow the structure in the plan template to:

- Fill Technical Context (language, dependencies, storage, testing, platform, performance goals)
- Fill Constitution Check section from constitution
- Evaluate gates (ERROR if violations unjustified)
- Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
- Phase 1: Generate data-model.md, contracts/, quickstart.md

The command ends after Phase 2 planning and reports branch, plan path, and generated artifacts.

## Response snapshot

Completed the full implementation planning workflow for User Authentication feature:

**Phase 0 (Research):**
- Generated research.md resolving 10 technical unknowns:
  1. Better Auth configuration for Next.js 15 App Router
  2. JWT secret sharing between frontend and backend (environment variables)
  3. HTTP-only cookie configuration with SameSite and Secure flags
  4. Better Auth database schema and migration setup
  5. Frontend middleware pattern for protected routes (Next.js 15)
  6. Backend JWT validation with PyJWT (algorithm, expiration, claims)
  7. Error handling patterns for expired/invalid tokens
  8. CORS configuration for frontend-backend communication
  9. Testing patterns for JWT-based authentication (mocking tokens)
  10. Accessibility best practices for authentication forms (WCAG 2.1 AA)

**Phase 1 (Design Artifacts):**
- Generated plan.md with:
  - Technical Context (TypeScript 5.x, Python 3.11+, Better Auth, PyJWT, PostgreSQL)
  - Constitution Check (all 6 principles PASS)
  - Project Structure (monorepo with frontend/backend separation)
  - Complexity Tracking (no violations)
  - Phase 0 research plan and Phase 1 design artifact plan

- Generated data-model.md documenting:
  - Two-database architecture (frontend Better Auth DB + backend tasks DB)
  - NO users table in backend (critical design decision)
  - user_id field specification (string, indexed, from JWT 'sub' claim)
  - Better Auth managed tables (user, password, session, account, verification)
  - Security considerations and data isolation patterns

- Generated contracts/:
  - jwt-validation.md: Backend get_current_user() dependency contract
    - Input: Authorization header or HTTP-only cookie
    - Output: user_id string from 'sub' claim
    - Errors: 401 for missing/expired/invalid tokens
    - Implementation example and test cases

  - better-auth-flow.md: Frontend authentication flow contract
    - Methods: signUp(), signIn(), signOut(), getSession()
    - Auto-generated API routes at /api/auth/*
    - JWT token format and cookie configuration
    - Middleware integration for protected routes

- Generated quickstart.md with:
  - Prerequisites (Node.js 18+, Python 3.11+, PostgreSQL 14+)
  - Step-by-step setup for both frontend and backend
  - Environment variable configuration
  - Better Auth and PyJWT installation
  - Database setup and migrations
  - Verification steps and common troubleshooting

**Constitutional Compliance:**
- ✅ Spec-Driven Development: Complete 12-section feature spec exists
- ✅ Clean Code: Modular (Better Auth + JWT dependency), typed (TypeScript + Pydantic)
- ✅ Test-First: TDD workflow planned, test fixtures documented
- ✅ Version Control: Branch 002-phase2-fullstack-web, GitHub workflow
- ✅ Observability: Logging planned for auth operations, errors, performance
- ✅ Performance: JWT validation <50ms, auth operations <500ms
- ✅ Security: HTTP-only cookies, CSRF protection, user isolation, JWT validation

**Key Architectural Decisions:**
1. Frontend-managed authentication (Better Auth) with backend JWT validation only
2. NO users table in backend (trust JWT tokens from frontend)
3. Two separate PostgreSQL databases (frontend auth + backend tasks)
4. Stateless backend (no session storage)
5. JWT tokens with 24-hour expiration (no refresh tokens in Phase 2)
6. WCAG 2.1 AA accessibility compliance

## Outcome

- ✅ Impact: Complete implementation plan created for User Authentication feature with all design artifacts (plan.md, research.md, data-model.md, contracts/, quickstart.md). Foundation ready for TDD implementation.
- 🧪 Tests: No tests created during planning phase. Test patterns documented in research.md (PyJWT fixtures, Better Auth mocking, E2E Playwright tests).
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, jwt-validation.md, better-auth-flow.md, quickstart.md)
- 🔁 Next prompts: Run /sp.tasks to generate tasks.md with test-driven implementation tasks (red-green-refactor cycles). Then implement frontend Better Auth integration, backend JWT dependency, and UI components.
- 🧠 Reflection: The two-database architecture (frontend Better Auth + backend tasks) simplifies backend significantly by eliminating user management. Backend trusts JWT tokens and focuses solely on task data and user isolation. This clear separation of concerns aligns with constitution principles (Clean Code, Modularity).

## Evaluation notes (flywheel)

- Failure modes observed: None. PowerShell script unavailable (pwsh not found), but successfully completed planning using agent-native approach (direct file creation).
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all 6 core principles validated)
  - Plan Completeness: PASS (all sections filled)
  - Research Coverage: PASS (all 10 unknowns resolved)
  - Contract Clarity: PASS (jwt-validation.md and better-auth-flow.md comprehensive)
  - Quickstart Usability: PASS (step-by-step setup with troubleshooting)
- Prompt variant (if applicable): N/A (standard /sp.plan command)
- Next experiment (smallest change to try): Consider splitting research.md into multiple files per research item for better organization in Phase 3+ features (single file works well for Phase 2).
