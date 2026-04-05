---
id: 006
title: Document two-token authentication architecture ADR
stage: plan
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-phase2-fullstack-web
branch: 002-phase2-fullstack-web
user: user
command: /sp.adr two-token-authentication-architecture
labels: ["adr", "authentication", "jwt", "two-token", "architecture-decision", "better-auth"]
links:
  spec: specs/002-phase2-fullstack-web/features/01-user-authentication.md
  ticket: null
  adr: history/adr/006-two-token-authentication-architecture.md
  pr: null
files:
  - history/adr/006-two-token-authentication-architecture.md
tests:
  - N/A (architecture documentation)
---

## Prompt

User command: `/sp.adr two-token-authentication-architecture`

Context: Following the forensic audit (PHR-005), an architecturally significant decision was identified: the two-token authentication architecture separating Better Auth session cookie (frontend middleware) from JWT token (backend API). This decision has long-term consequences, multiple viable alternatives, and cross-cutting impact on authentication, routing, and API architecture.

## Response snapshot

**ADR Created:** ADR-006: Two-Token Authentication Architecture (Session Cookie + JWT)

**Significance Test (ALL PASSED):**
- ✅ **Impact:** Affects all protected routes (frontend middleware), all API endpoints (backend validation), authentication flow across entire application lifecycle
- ✅ **Alternatives:** 5 alternatives considered (single token cookie, single token JWT, JWT in HTTP-only cookie, sessionStorage, in-memory)
- ✅ **Scope:** Cross-cutting concern affecting frontend routing, backend authorization, API client, session management, user experience

**Decision Summary:**
Use two separate authentication tokens with distinct responsibilities:

1. **Better Auth Session Cookie** (`better-auth.session_token`)
   - Purpose: Frontend middleware and route protection
   - Storage: HTTP-only cookie (secure)
   - Managed by: Better Auth automatically
   - Lifetime: 24 hours

2. **JWT Token** (via `authClient.token()`)
   - Purpose: Backend API authentication
   - Storage: localStorage (`jwt_token` key)
   - Managed by: Frontend application explicitly
   - Lifetime: 24 hours
   - Transmission: Authorization header

**Key Architecture Rules:**
- BOTH tokens required for full functionality
- Backend validates ONLY JWT (no cookie fallback)
- JWT must be explicitly retrieved and stored (not automatic)
- localStorage persistence survives page refreshes

**Alternatives Analyzed:**
1. Single Token (Session Cookie Only) - Rejected: stateful backend, performance penalty
2. Single Token (JWT Only) - Rejected: reinventing Better Auth session management
3. JWT in HTTP-Only Cookie - Rejected: Better Auth doesn't support, CORS complications
4. JWT in sessionStorage - Rejected: lost on tab close, poor UX
5. JWT in Memory - Rejected: lost on page refresh, terrible UX

**Decision Matrix Comparison:**
Chosen approach wins on: stateless backend, Better Auth compatibility, user experience (persistence), balance of security and functionality.

**Trade-offs Documented:**
- ✅ Positive: Clear separation, stateless backend, user isolation, persistent sessions
- ⚠️ Negative: Increased complexity, XSS vulnerability (localStorage), token synchronization
- 🔴 Risks: JWT not retrieved, in-memory storage, cookie confusion, lifetime divergence
- 🛡️ Mitigations: CSP headers, developer education, automatic refresh hook, E2E tests

**Implementation Details Included:**
- JWT retrieval flow (login)
- JWT persistence on page load
- Backend JWT validation
- API client integration
- Code examples for all components

**Related Decisions:**
- Extends ADR-004 (Phase 2 Full-Stack Architecture) with specific two-token implementation
- Builds on forensic audit findings (PHR-005) identifying spec ambiguity

## Outcome

- ✅ Impact: Architecturally significant decision documented with comprehensive rationale, alternatives, consequences, and implementation guidance
- 🧪 Tests: N/A (architecture documentation, implementation tests covered in tasks T026A-T032A)
- 📁 Files: 1 ADR created (006-two-token-authentication-architecture.md)
- 🔁 Next prompts: Implement corrected specifications (execute tasks T026A-T032A), or continue with next feature development
- 🧠 Reflection: The ADR successfully documents the architectural decision that emerged from the forensic audit. The two-token pattern is non-obvious (Better Auth's dual mechanisms are not well-documented), so this ADR serves as critical reference for current and future developers. The decision matrix and 5 alternatives provide clear rationale for why this approach was chosen over simpler or more secure alternatives.

## Evaluation notes (flywheel)

- Failure modes observed: None. ADR creation workflow executed successfully using manual file creation (no create-adr.sh script available). Applied significance test rigorously - this decision clearly passes all three criteria (impact, alternatives, scope).
- Graders run and results (PASS/FAIL): Significance test: PASS (all 3 criteria met). ADR completeness: PASS (decision, context, consequences, alternatives, implementation, references all included). Decision clustering: PASS (two-token architecture is a cohesive decision cluster, not over-granular).
- Prompt variant (if applicable): sp.adr workflow variant - user-specified decision title instead of automatic extraction from plan.md
- Next experiment (smallest change to try): Verify that plan.md references this ADR in the JWT Token Handling Strategy section, potentially add ADR link to better-auth-flow.md and jwt-validation.md contracts
