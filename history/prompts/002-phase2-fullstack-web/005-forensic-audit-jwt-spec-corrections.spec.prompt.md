---
id: 005
title: Forensic audit and JWT authentication spec corrections
stage: spec
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-phase2-fullstack-web
branch: 002-phase2-fullstack-web
user: user
command: forensic audit and spec corrections
labels: ["authentication", "jwt", "better-auth", "spec-correction", "forensic-audit", "two-token-architecture"]
links:
  spec: specs/002-phase2-fullstack-web/features/01-user-authentication.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-phase2-fullstack-web/features/01-user-authentication.md
  - specs/002-phase2-fullstack-web/features/contracts/better-auth-flow.md
  - specs/002-phase2-fullstack-web/features/contracts/jwt-validation.md
  - specs/002-phase2-fullstack-web/plan.md
  - specs/002-phase2-fullstack-web/tasks.md
tests:
  - N/A (specification correction work)
---

## Prompt

You are acting as a senior systems architect and spec-auditor. I have already written: feature specifications, an implementation plan, a tasks.md file using a spec-driven workflow (Spec Kit Plus). Despite this, my Better Auth implementation drifted from the intended design and caused authentication failures.

Your job is to perform a **forensic audit** of my specifications and plans to explain WHY this happened and WHERE the process broke.

**Context:**
- Stack: Next.js 16+ frontend, Python FastAPI backend, SQLModel ORM, Neon PostgreSQL, Better Auth
- Challenge: Better Auth runs on frontend, FastAPI backend needs to verify which user is making requests
- Solution: JWT tokens signed by Better Auth, validated by FastAPI
- Problem: Implementation failed because specs didn't explicitly document JWT token retrieval and storage

**Requirements:**
1. Forensic Spec Audit - Compare specs vs Better Auth real behavior, identify implicit assumptions
2. Root Cause Analysis - Explain WHY the incorrect implementation was reasonable given the specs
3. Correct the Specifications (MANDATORY) - Rewrite/add explicit auth behavior rules, cookie vs JWT responsibilities, middleware boundaries
4. Update the Implementation Plan - Add missing steps, validation checkpoints, stop conditions
5. Rewrite/Add Tasks - Add missing tasks with stronger acceptance criteria
6. Validation Checklist - Produce final checklist to prevent future spec drift

**Follow-up:** "update the specs with these corrections"

## Response snapshot

Performed comprehensive forensic audit and corrected all specification files:

**Root Causes Identified:**
1. AC4 ambiguity: "JWT token stored in HTTP-only cookie" conflated Better Auth session cookie with JWT token
2. Missing JWT retrieval workflow: No specification for `authClient.token()` call
3. Missing persistence requirements: No explicit localStorage requirement
4. Two-token architecture not documented: Session cookie vs JWT token responsibilities unclear

**Specifications Corrected:**

1. **01-user-authentication.md**
   - Replaced AC4 with explicit JWT retrieval flow after login
   - Added AC13: JWT Token Lifecycle Management (login → refresh → API call)
   - Mandated localStorage storage for persistence
   - Documented two-token architecture (session cookie + JWT)

2. **better-auth-flow.md**
   - Added Method 5: `authClient.token()` with complete usage patterns
   - Documented when to call: after login, after registration, on page load, after 401
   - Provided code examples for JWT retrieval and storage

3. **jwt-validation.md**
   - Removed cookie fallback ambiguity
   - Mandated Authorization header only: `Authorization: Bearer <token>`
   - Simplified backend implementation (single input method)
   - Clarified Better Auth JWT plugin does NOT set JWT in cookies

4. **plan.md**
   - Added JWT Token Handling Strategy section
   - Updated Phase 0 research questions with JWT-critical items
   - Documented two-token architecture decision and rationale

5. **tasks.md**
   - Enhanced T022: Better Auth setup with JWT plugin configuration
   - Added T026A: Create JWT storage utility (localStorage)
   - Added T026B: Integrate JWT retrieval in LoginForm
   - Added T026C: Integrate JWT retrieval in RegisterForm
   - Added T026D: Update LogoutButton to clear JWT
   - Added T030A: Create JWT refresh hook for page load
   - Added T032A: E2E test for JWT persistence after refresh
   - Updated task count: 85 → 91 tasks

**Key Technical Corrections:**
- Better Auth has TWO separate tokens:
  - `better-auth.session_token` (HTTP-only cookie) → Next.js middleware
  - JWT token (from `authClient.token()`) → Backend API authentication
- JWT MUST be stored in localStorage (not in-memory) for persistence
- JWT MUST be sent in Authorization: Bearer header (no cookie fallback)
- Backend validates ONLY Authorization header (simplified from dual-input spec)

## Outcome

- ✅ Impact: All 5 specification files corrected with explicit JWT handling requirements. Eliminated ambiguity that caused implementation drift.
- 🧪 Tests: 6 new tasks added including E2E test for JWT persistence (T032A)
- 📁 Files: 5 spec files updated, 6 new tasks added (T026A-D, T030A, T032A)
- 🔁 Next prompts: Implementation of corrected specs (execute tasks T026A-T032A), or create validation checklist as separate artifact
- 🧠 Reflection: The forensic audit successfully identified that the specs conflated two distinct authentication mechanisms. The root cause was not missing information but AMBIGUOUS information - AC4 implied Better Auth handled everything automatically. The fix required explicit separation of responsibilities and mandatory implementation steps.

## Evaluation notes (flywheel)

- Failure modes observed: Implicit assumptions in acceptance criteria (AC4 "JWT in cookie" was technically true for session cookie but misleading). Tasks that appeared complete without validating critical integration points (JWT retrieval and storage were never explicitly required).
- Graders run and results (PASS/FAIL): N/A (spec correction work, implementation testing pending)
- Prompt variant (if applicable): Forensic audit prompt pattern with explicit deliverables (6 numbered requirements)
- Next experiment (smallest change to try): Implement T026A (JWT storage utility) first to validate localStorage persistence pattern before integrating into forms
