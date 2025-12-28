# ADR-006: Two-Token Authentication Architecture (Session Cookie + JWT)

> **Scope**: Authentication token architecture for Phase 2 full-stack web application separating frontend middleware authentication (session cookie) from backend API authentication (JWT token).

- **Status:** Accepted
- **Date:** 2025-12-29
- **Feature:** 002-phase2-fullstack-web (User Authentication)
- **Context:** Building a full-stack web application with Next.js frontend and FastAPI backend. Better Auth runs entirely on the frontend for user management, while the backend needs to verify which authenticated user is making API requests. This requires a clear authentication token strategy that works across both the frontend middleware layer (route protection) and the backend API layer (data access authorization).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Affects all protected routes (frontend middleware) and all API endpoints (backend validation), determines authentication flow across entire application lifecycle
     2) Alternatives: YES - Single token approach, different storage mechanisms (in-memory vs localStorage vs cookie), different transmission methods (header vs cookie)
     3) Scope: YES - Cross-cutting concern affecting frontend routing, backend authorization, API client architecture, session management, and user experience
-->

## Decision

**Use a two-token architecture with separate responsibilities:**

1. **Better Auth Session Cookie** (`better-auth.session_token`)
   - **Purpose:** Frontend authentication for Next.js middleware and route protection
   - **Storage:** HTTP-only cookie (secure, HttpOnly, SameSite=Strict)
   - **Lifetime:** 24 hours
   - **Managed by:** Better Auth automatically
   - **Used by:** Next.js middleware, frontend routing decisions, session existence checks

2. **JWT Token** (retrieved via `authClient.token()`)
   - **Purpose:** Backend API authentication for FastAPI endpoints
   - **Storage:** localStorage (`jwt_token` key)
   - **Lifetime:** 24 hours
   - **Managed by:** Frontend application explicitly
   - **Used by:** Backend API requests via `Authorization: Bearer <token>` header
   - **Contains:** User ID in `sub` claim, expiration in `exp` claim, signed with HS256

**Key Architecture Rules:**

1. **BOTH tokens are required** for full application functionality:
   - Session cookie enables frontend UX (middleware protection, dashboard access)
   - JWT token enables backend data access (API requests, user-specific data)

2. **Backend validates ONLY the JWT token:**
   - No session cookie validation on backend
   - Authorization header is the single input method
   - Backend trusts JWT signature and extracts `user_id` from `sub` claim

3. **JWT must be explicitly retrieved and stored:**
   - After successful login: Call `authClient.token()` and store in localStorage
   - After successful registration: Call `authClient.token()` and store in localStorage
   - On page load: Check localStorage, refresh from `authClient.token()` if missing
   - On logout: Clear both session cookie (via Better Auth) and JWT from localStorage

4. **JWT persistence strategy:**
   - Use localStorage (NOT in-memory) to survive page refreshes
   - Accept XSS vulnerability trade-off (mitigated by 24-hour token expiration)
   - Short-lived tokens limit damage from potential XSS attacks

## Context

**The Problem:**
Better Auth manages user credentials and sessions entirely on the frontend, but the FastAPI backend needs to know which user is making API requests without duplicating user management logic or maintaining backend sessions.

**Better Auth's Dual Authentication Mechanisms:**
Better Auth provides TWO separate authentication tokens that serve different purposes:

1. **Session Cookie** (`better-auth.session_token`):
   - Created automatically on successful login
   - HTTP-only, secure cookie
   - Used by Better Auth middleware for frontend route protection
   - Cannot be read by JavaScript (security feature)
   - Perfect for protecting Next.js routes

2. **JWT Token** (via `authClient.token()` endpoint):
   - Must be explicitly retrieved after login
   - Contains user ID in standard JWT format
   - Designed for external API authentication
   - Can be stored in localStorage/sessionStorage
   - Sent to backend in Authorization header

**The Forensic Audit Finding:**
The original specification conflated these two tokens, stating "JWT token stored in HTTP-only cookie" which was ambiguous. This led developers to assume Better Auth automatically handled everything, when in fact the JWT must be explicitly retrieved and managed by the application.

## Consequences

### Positive

✅ **Clear Separation of Concerns:**
   - Frontend middleware uses session cookie (Better Auth's domain)
   - Backend API uses JWT token (FastAPI's domain)
   - No confusion about which token serves which purpose

✅ **Stateless Backend:**
   - Backend validates JWT without session storage
   - Horizontal scaling is trivial (no session synchronization)
   - Fast JWT validation (<50ms per request)

✅ **User Isolation Enforced:**
   - Every backend query automatically filtered by `user_id` from JWT
   - No possibility of cross-user data access
   - User ID cannot be spoofed (JWT signature verification)

✅ **Persistent Sessions:**
   - localStorage survives page refreshes
   - Users stay authenticated across browser restarts (until token expires)
   - Better UX than in-memory storage

✅ **Frontend Flexibility:**
   - Session cookie enables seamless routing protection
   - JWT enables API calls from client components
   - Both tokens work independently but complement each other

### Negative

⚠️ **Increased Complexity:**
   - Developers must understand TWO separate tokens
   - Explicit JWT retrieval adds implementation steps
   - Logout must clear both tokens (not automatic)

⚠️ **XSS Vulnerability (localStorage):**
   - JWT in localStorage is accessible to malicious scripts
   - If XSS occurs, attacker can steal JWT and make API calls
   - Trade-off accepted for persistence requirement

⚠️ **Token Synchronization:**
   - Session cookie and JWT have separate lifetimes
   - Possible (rare) state: session valid but JWT expired → must refresh JWT
   - Requires explicit refresh logic on page load

⚠️ **Learning Curve:**
   - Better Auth documentation doesn't emphasize two-token pattern
   - Developers unfamiliar with JWT might find this confusing
   - Requires clear documentation and examples

### Risks

🔴 **JWT Not Retrieved After Login:**
   - Symptom: User can navigate frontend but gets 401 on API calls
   - Mitigation: Explicit acceptance criteria (AC4, AC13) mandate JWT retrieval
   - Detection: E2E test validates JWT persistence (T032A)

🔴 **JWT Stored In-Memory Instead of localStorage:**
   - Symptom: Authentication lost on page refresh
   - Mitigation: Task T026A explicitly creates localStorage utility
   - Detection: E2E test validates persistence after refresh (T032A)

🔴 **Backend Accepts Cookie Instead of Header:**
   - Symptom: Cookie confusion, potential security holes
   - Mitigation: jwt-validation.md mandates Authorization header only
   - Detection: Backend tests reject requests without Authorization header

🔴 **JWT and Session Cookie Lifetimes Diverge:**
   - Symptom: Inconsistent auth state (logged in but API fails)
   - Mitigation: Both tokens set to 24-hour lifetime
   - Detection: Monitor for 401 errors with valid session cookie

### Mitigation

**XSS Protection:**
- Content Security Policy (CSP) headers
- React auto-escapes output (XSS prevention)
- Input sanitization on all forms
- Short-lived tokens (24 hours) limit exposure
- Consider httpOnly cookie for JWT in Phase 3+ (requires backend changes)

**Developer Education:**
- Clear documentation in better-auth-flow.md (Method 5)
- Code examples in jwt-validation.md
- Explicit tasks (T026A-D, T030A) with acceptance criteria
- E2E test demonstrating complete flow

**Automatic JWT Refresh:**
- Hook on page load checks for JWT in localStorage
- If missing but session exists, calls `authClient.token()`
- Transparent to user (automatic recovery)

## Alternatives Considered

### Alternative 1: Single Token (Session Cookie Only)

**Approach:** Use Better Auth session cookie for both frontend middleware and backend API authentication.

**Implementation:**
- Backend reads `better-auth.session_token` cookie from requests
- Backend validates session cookie against Better Auth's session database
- User ID extracted from session database lookup

**Rejected Because:**
- ❌ Backend becomes stateful (must query session database)
- ❌ Violates "stateless backend" principle
- ❌ Backend now depends on Better Auth internals
- ❌ Horizontal scaling requires session synchronization
- ❌ Performance penalty (database lookup per request vs. JWT validation)
- ❌ Tight coupling between frontend auth library and backend

**When This Works:**
- Monolithic applications where frontend and backend share session storage
- Applications with sticky sessions (not horizontally scaled)

---

### Alternative 2: Single Token (JWT Only)

**Approach:** Use only JWT for both frontend middleware and backend API authentication.

**Implementation:**
- Better Auth issues JWT on login
- Frontend middleware validates JWT (or trusts it blindly)
- Backend validates JWT signature
- No session cookie at all

**Rejected Because:**
- ❌ Frontend middleware would need to validate JWT (crypto operations in middleware)
- ❌ Better Auth session cookie already handles frontend auth perfectly
- ❌ Reinventing the wheel (Better Auth provides session management)
- ❌ Poor UX (no automatic session cookie refresh)
- ❌ Middleware performance penalty (JWT validation on every route)

**When This Works:**
- API-only applications (no server-side routing)
- Mobile apps where all requests go through API
- Microservices where session management is centralized

---

### Alternative 3: JWT in HTTP-Only Cookie

**Approach:** Better Auth sets JWT in HTTP-only cookie (instead of manual retrieval).

**Implementation:**
- Better Auth configured to set JWT in cookie automatically
- Backend reads JWT from cookie
- No localStorage needed

**Rejected Because:**
- ❌ Better Auth JWT plugin does NOT support setting JWT in cookie
- ❌ Would require custom Better Auth plugin implementation
- ❌ Cookie size limits (JWT can be large with many claims)
- ❌ CORS complications (cookies require SameSite configuration)
- ❌ Cannot read JWT on frontend for debugging/inspection

**When This Works:**
- If Better Auth supported it natively (it doesn't)
- Applications with same-origin frontend/backend
- When localStorage XSS risk is unacceptable

---

### Alternative 4: JWT in sessionStorage

**Approach:** Same as chosen approach but use sessionStorage instead of localStorage.

**Implementation:**
- JWT stored in `sessionStorage.setItem('jwt_token', token)`
- Cleared when browser tab closes
- Otherwise identical to current approach

**Rejected Because:**
- ❌ Lost on browser tab close (poor UX for multi-tab workflows)
- ❌ Users must re-authenticate every time they open app
- ❌ Does NOT survive page refreshes in new tabs
- ❌ Better Auth session cookie persists, creating inconsistent state

**When This Works:**
- High-security applications requiring session-only auth
- Banking applications where logout-on-close is required
- Applications where users never use multiple tabs

---

### Alternative 5: In-Memory JWT Storage

**Approach:** Store JWT in React state/context (not localStorage).

**Implementation:**
- JWT stored in React Context on login
- Lost on page refresh
- Must call `authClient.token()` on every app initialization

**Rejected Because:**
- ❌ Lost on page refresh (terrible UX)
- ❌ Better Auth session cookie persists but JWT is gone
- ❌ User appears logged in (session exists) but gets 401 on API calls
- ❌ Must re-retrieve JWT on EVERY page load (performance penalty)
- ❌ Race condition: frontend renders before JWT retrieved

**When This Works:**
- Extremely high-security environments
- Applications where page refresh is rare
- When localStorage XSS risk is absolutely unacceptable

---

### Decision Matrix

| Alternative | Stateless Backend | Frontend Perf | UX (Persistence) | Security | Complexity | Better Auth Compatibility |
|-------------|-------------------|---------------|------------------|----------|------------|---------------------------|
| **Two-Token (Chosen)** | ✅ Yes | ✅ Fast | ✅ Excellent | ⚠️ localStorage XSS | ⚠️ Medium | ✅ Native |
| Single Token (Cookie) | ❌ No (stateful) | ✅ Fast | ✅ Excellent | ✅ HttpOnly | ✅ Low | ⚠️ Workaround |
| Single Token (JWT) | ✅ Yes | ❌ Slow (middleware JWT) | ⚠️ Good | ✅ No localStorage | ⚠️ Medium | ❌ Custom |
| JWT in HttpOnly Cookie | ✅ Yes | ✅ Fast | ✅ Excellent | ✅ HttpOnly | ⚠️ Medium | ❌ Not supported |
| JWT in sessionStorage | ✅ Yes | ✅ Fast | ❌ Tab-only | ⚠️ sessionStorage XSS | ✅ Low | ✅ Native |
| JWT in Memory | ✅ Yes | ❌ Slow (refresh) | ❌ Poor (lost) | ✅ No XSS | ⚠️ Medium | ✅ Native |

**Chosen approach wins on:**
- Stateless backend (scalability)
- Better Auth compatibility (no custom plugins)
- User experience (persistence across refreshes)
- Balance of security and functionality

## Implementation Details

### JWT Retrieval Flow (Login)

```typescript
// src/core/frontend/components/auth/LoginForm.tsx
const handleSubmit = async (e) => {
  e.preventDefault();

  // Step 1: Authenticate with Better Auth
  const { data, error } = await authClient.signIn.email({
    email,
    password,
  });

  if (error) {
    setError(error.message);
    return;
  }

  // Step 2: CRITICAL - Retrieve JWT for backend
  const tokenResult = await authClient.token();
  if (tokenResult.data) {
    localStorage.setItem('jwt_token', tokenResult.data.token);
  }

  // Step 3: Redirect to dashboard
  router.push('/');
};
```

### JWT Persistence on Page Load

```typescript
// src/core/frontend/hooks/useAuthInit.ts
useEffect(() => {
  async function initAuth() {
    const session = await authClient.getSession();
    const jwt = localStorage.getItem('jwt_token');

    // Session exists but no JWT → retrieve JWT
    if (session.data && !jwt) {
      const tokenResult = await authClient.token();
      if (tokenResult.data) {
        localStorage.setItem('jwt_token', tokenResult.data.token);
      }
    }

    // No session → clear JWT if exists
    if (!session.data && jwt) {
      localStorage.removeItem('jwt_token');
    }
  }

  initAuth();
}, []);
```

### Backend JWT Validation

```python
# src/core/backend/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validate JWT token and extract user_id from 'sub' claim.

    Token MUST be provided in Authorization header: Bearer <token>
    NO cookie fallback.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(401, detail="Invalid token: missing user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail="Invalid token")
```

### API Client Integration

```typescript
// src/core/frontend/lib/api.ts
export const api = {
  getTasks: async () => {
    const token = localStorage.getItem('jwt_token');
    const response = await fetch('/api/v1/tasks', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  },
  // ... other API methods
};
```

## Related ADRs

- [ADR-004: Phase 2 Full-Stack Architecture](004-phase2-fullstack-architecture.md) - High-level authentication architecture
- [ADR-002: CLI Technology Stack](002-cli-technology-stack.md) - Phase 1 authentication (none)

## References

- [User Authentication Specification](../../specs/002-phase2-fullstack-web/features/01-user-authentication.md)
- [Implementation Plan](../../specs/002-phase2-fullstack-web/plan.md#jwt-token-handling-strategy-jwt-strategymd)
- [JWT Validation Contract](../../specs/002-phase2-fullstack-web/features/contracts/jwt-validation.md)
- [Better Auth Flow Contract](../../specs/002-phase2-fullstack-web/features/contracts/better-auth-flow.md)
- [Better Auth Documentation](https://www.better-auth.com/)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [Forensic Audit PHR](../../history/prompts/002-phase2-fullstack-web/005-forensic-audit-jwt-spec-corrections.spec.prompt.md)

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-29 | Development Team | Initial ADR documenting two-token architecture decision after forensic audit |
