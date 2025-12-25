# Research: User Authentication Implementation

**Feature:** User Authentication
**Date:** 2025-12-21
**Status:** Research Complete
**Input:** Phase 0 unknowns from plan.md

## Summary

This research document resolves all technical unknowns identified in the planning phase for implementing user authentication using Better Auth on the frontend and JWT validation on the backend. Key decisions include using Better Auth's Next.js 16 App Router integration, sharing JWT secrets via environment variables, implementing HTTP-only cookies with SameSite=Strict, and establishing clear patterns for JWT validation, error handling, and testing.

---

## Research Item 1: Better Auth Configuration for Next.js 16 App Router

### Decision
Use Better Auth's official Next.js 16 App Router integration with API routes for authentication endpoints.

### Investigation
- **Better Auth Documentation:** Provides first-class Next.js support via `better-auth/nextjs` package
- **App Router Pattern:** Better Auth creates API routes at `/api/auth/*` automatically
- **Configuration:** Create `lib/auth.ts` with Better Auth configuration, export client and server methods
- **Database:** Better Auth uses Drizzle ORM or Prisma for user storage (we'll use Drizzle with PostgreSQL)

### Implementation Pattern
```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg", // PostgreSQL
  }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60, // Update session every hour
  },
  jwt: {
    secret: process.env.JWT_SECRET!,
    expiresIn: 60 * 60 * 24, // 24 hours
  },
  trustedOrigins: [process.env.NEXT_PUBLIC_API_URL!], // Backend URL for CORS
});

export const { signIn, signUp, signOut, getSession } = auth;
```

```typescript
// frontend/app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/nextjs";

export const { GET, POST } = toNextJsHandler(auth);
```

### Rationale
- **Official Support:** Better Auth provides native Next.js 16 integration
- **Automatic API Routes:** `[...all]` dynamic route handles all auth endpoints
- **Type Safety:** TypeScript support built-in
- **Database Flexibility:** Drizzle adapter works with Neon PostgreSQL

### Alternatives Considered
- **NextAuth.js:** More complex, heavier dependency, not as modern
- **Auth0/Clerk:** External services, adds cost and latency
- **Manual JWT:** Reinventing the wheel, error-prone

**Resources:**
- [Better Auth Docs](https://www.better-auth.com/docs/nextjs)
- [Next.js 16 App Router API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)

---

## Research Item 2: JWT Secret Sharing Between Frontend and Backend

### Decision
Share JWT secret via environment variables with a single source of truth in root `.env` file.

### Investigation
- **Environment Variables:** Both Next.js and FastAPI support `.env` files
- **Security:** JWT_SECRET must be same on frontend (signs tokens) and backend (validates tokens)
- **Convention:** Use `JWT_SECRET` variable name, minimum 256-bit random string

### Implementation Pattern

**Root `.env` file:**
```bash
# Shared JWT secret (minimum 32 characters for HS256)
JWT_SECRET=your-super-secret-key-at-least-256-bits-long-random-string

# Frontend (Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost:5432/frontend_auth

# Backend (FastAPI)
BACKEND_DATABASE_URL=postgresql://user:password@localhost:5432/backend_tasks
```

**Frontend (Next.js):**
```typescript
// frontend/lib/auth.ts
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error("JWT_SECRET environment variable is required");
}
```

**Backend (FastAPI):**
```python
# backend/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        env_prefix = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")

settings = Settings()
```

### Rationale
- **Single Source of Truth:** One `.env` file prevents secret mismatch
- **Fail Fast:** Application won't start without JWT_SECRET (prevents insecure deployment)
- **Convention:** Standard environment variable pattern used across ecosystems

### Alternatives Considered
- **Separate secrets per environment:** Increases risk of mismatch, rejected
- **Hardcoded secrets:** Insecure, rejected
- **Secret management service (AWS Secrets Manager):** Overkill for Phase 2, deferred to Phase 4

**Security Note:** Never commit `.env` to git. Use `.env.example` with placeholder values.

---

## Research Item 3: HTTP-Only Cookie Configuration

### Decision
Use HTTP-only cookies with SameSite=Strict and Secure flag for JWT token storage.

### Investigation
- **HTTP-Only:** Prevents JavaScript access (XSS protection)
- **SameSite=Strict:** Prevents cross-site request forgery (CSRF protection)
- **Secure:** Requires HTTPS in production (prevents man-in-the-middle attacks)
- **Path:** Set to `/` for application-wide access
- **Max-Age:** 24 hours (matches JWT expiration)

### Implementation Pattern

**Frontend (Better Auth automatically sets cookie):**
Better Auth handles cookie configuration internally, but we can customize:

```typescript
// frontend/lib/auth.ts
export const auth = betterAuth({
  // ... other config
  session: {
    cookieName: "auth-token",
    cookieOptions: {
      httpOnly: true,
      sameSite: "strict", // CSRF protection
      secure: process.env.NODE_ENV === "production", // HTTPS only in prod
      path: "/",
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },
});
```

**Backend (reads cookie or Authorization header):**
```python
# backend/dependencies.py
from fastapi import Cookie, Header, HTTPException
from typing import Optional

async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_token: Optional[str] = Cookie(None)
) -> str:
    """Extract JWT from Authorization header or cookie."""
    token = None

    # Try Authorization header first (Bearer token)
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    # Fallback to cookie
    elif auth_token:
        token = auth_token

    if not token:
        raise HTTPException(status_code=401, detail="Authorization required")

    # Validate token (see Research Item 6)
    return validate_jwt(token)
```

### Rationale
- **XSS Protection:** HTTP-only prevents malicious scripts from stealing tokens
- **CSRF Protection:** SameSite=Strict prevents cross-origin requests with cookies
- **HTTPS Enforcement:** Secure flag prevents token interception
- **Dual-Method Support:** Backend accepts both cookie and header (flexibility for testing)

### Alternatives Considered
- **Local Storage:** Vulnerable to XSS, rejected
- **Session Storage:** Lost on tab close, poor UX, rejected
- **SameSite=Lax:** Allows some cross-site requests, less secure, rejected

**Resources:**
- [MDN: HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

## Research Item 4: Better Auth Database Schema

### Decision
Use Better Auth's automatic schema generation with Drizzle ORM on PostgreSQL.

### Investigation
- **Better Auth Tables:** Creates `user`, `session`, `account`, `verification` tables automatically
- **Drizzle Migrations:** Better Auth generates migrations, we run them during setup
- **Separation:** Frontend database separate from backend task database (two PostgreSQL instances on Neon)

### Database Schema (Generated by Better Auth)

```sql
-- Frontend database (Better Auth managed)

CREATE TABLE "user" (
  "id" TEXT PRIMARY KEY,
  "email" TEXT NOT NULL UNIQUE,
  "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
  "name" TEXT,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
  "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE "session" (
  "id" TEXT PRIMARY KEY,
  "expiresAt" TIMESTAMP NOT NULL,
  "ipAddress" TEXT,
  "userAgent" TEXT,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE "account" (
  "id" TEXT PRIMARY KEY,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "accountId" TEXT NOT NULL,
  "providerId" TEXT NOT NULL,
  "accessToken" TEXT,
  "refreshToken" TEXT,
  "expiresAt" TIMESTAMP,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE "verification" (
  "id" TEXT PRIMARY KEY,
  "identifier" TEXT NOT NULL,
  "value" TEXT NOT NULL,
  "expiresAt" TIMESTAMP NOT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Password table (Better Auth stores hashed passwords securely)
CREATE TABLE "password" (
  "hash" TEXT NOT NULL,
  "userId" TEXT NOT NULL PRIMARY KEY REFERENCES "user"("id") ON DELETE CASCADE
);

-- Indexes
CREATE INDEX "idx_session_userId" ON "session"("userId");
CREATE INDEX "idx_account_userId" ON "account"("userId");
CREATE INDEX "idx_verification_identifier" ON "verification"("identifier");
```

### Migration Pattern

```typescript
// frontend/lib/db.ts
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

const connectionString = process.env.DATABASE_URL!;
const client = postgres(connectionString);
export const db = drizzle(client);
```

```bash
# Run Better Auth migrations
npm run db:migrate
```

### Rationale
- **Automatic Schema:** Better Auth manages tables, we don't write migrations manually
- **Secure by Default:** Passwords hashed with bcrypt, email stored securely
- **Separate Database:** Frontend auth database independent from backend tasks database (clear separation)

### Alternatives Considered
- **Single shared database:** Violates separation of concerns, rejected
- **Manual user table management:** Reinvents Better Auth, error-prone, rejected

**Important:** Backend does NOT have a users table. Backend trusts user_id from JWT.

---

## Research Item 5: Frontend Middleware Pattern for Protected Routes

### Decision
Use Next.js 16 middleware with Better Auth session check to protect routes.

### Investigation
- **Middleware Location:** `middleware.ts` in `app/` directory
- **Pattern:** Check for valid session, redirect unauthenticated users to /login
- **Protected Routes:** All routes except /login, /register, /api/auth/*
- **Matcher:** Use Next.js matcher config to specify protected routes

### Implementation Pattern

```typescript
// frontend/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { auth } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes (no auth required)
  const publicRoutes = ["/login", "/register"];
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));
  const isAuthAPI = pathname.startsWith("/api/auth");

  // Allow public routes and auth API
  if (isPublicRoute || isAuthAPI) {
    return NextResponse.next();
  }

  // Check session for protected routes
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  // Redirect to login if no session
  if (!session) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname); // Return to original URL after login
    return NextResponse.redirect(loginUrl);
  }

  // Allow access to protected route
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon)
     * - public files (public directory)
     */
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
```

**Additional Pattern: Redirect Authenticated Users Away from Auth Pages**

```typescript
// In middleware.ts, add before allowing public routes:
if (isPublicRoute && session) {
  // User is logged in, redirect away from login/register
  return NextResponse.redirect(new URL("/", request.url));
}
```

### Rationale
- **Centralized Protection:** One middleware protects all routes
- **Better Auth Integration:** Uses auth.api.getSession() for session validation
- **Return URL:** Stores original URL, redirects back after login (better UX)
- **Performance:** Middleware runs at edge (fast response)

### Alternatives Considered
- **Per-page auth checks:** Duplicates logic across pages, rejected
- **Client-side only protection:** Insecure (user can bypass), rejected
- **HOC pattern:** More complex than middleware, rejected

**Resources:**
- [Next.js Middleware Docs](https://nextjs.org/docs/app/building-your-application/routing/middleware)

---

## Research Item 6: Backend JWT Validation with PyJWT

### Decision
Use PyJWT library with HS256 algorithm for JWT validation in FastAPI dependency.

### Investigation
- **Library:** PyJWT (most popular Python JWT library)
- **Algorithm:** HS256 (symmetric key, same secret for sign and verify)
- **Claims:** Extract 'sub' claim for user_id, check 'exp' for expiration
- **Dependency Injection:** FastAPI Depends() pattern for reusable validation

### Implementation Pattern

```python
# backend/dependencies.py
from fastapi import Depends, HTTPException, Security, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from .config import settings

security = HTTPBearer(auto_error=False)  # Don't auto-raise on missing token

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    auth_token: Optional[str] = Cookie(None, alias="auth-token")
) -> str:
    """
    Validate JWT token and extract user_id from 'sub' claim.

    Supports two token sources:
    1. Authorization header: Bearer <token>
    2. Cookie: auth-token=<token>

    Returns:
        user_id (str): User identifier from JWT 'sub' claim

    Raises:
        HTTPException 401: Invalid, expired, or missing token
    """
    token = None

    # Try Authorization header first
    if credentials:
        token = credentials.credentials
    # Fallback to cookie
    elif auth_token:
        token = auth_token

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authorization required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and validate JWT
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

**Usage in Route:**
```python
# backend/api/v1/tasks.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ...dependencies import get_current_user, get_db
from ...models import Task

router = APIRouter(prefix="/api/v1", tags=["tasks"])

@router.get("/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Get all tasks for authenticated user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()
    return tasks
```

### Rationale
- **PyJWT Standard:** Industry-standard library, well-tested
- **HS256 Algorithm:** Simple, fast, suitable for single-issuer scenario
- **Dependency Injection:** Reusable across all routes, no code duplication
- **Dual Token Source:** Supports both header and cookie (flexibility)
- **Clear Errors:** Specific error messages for debugging

### Alternatives Considered
- **Python-JOSE:** Similar to PyJWT, but PyJWT is more popular
- **RS256 (asymmetric):** Overkill for Phase 2, no need for separate keys
- **Manual token parsing:** Error-prone, reinventing the wheel, rejected

**Installation:**
```bash
pip install pyjwt
```

**Resources:**
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)

---

## Research Item 7: Error Handling Patterns for Expired/Invalid Tokens

### Decision
Frontend intercepts 401 errors from backend, displays user-friendly message, and redirects to login.

### Investigation
- **Error Detection:** Backend returns 401 Unauthorized for expired/invalid tokens
- **Frontend Response:** Detect 401 in API client, show toast notification, redirect to /login
- **Error Messages:** User-friendly (not technical)
- **State Cleanup:** Clear any cached data on logout/401

### Implementation Pattern

**Backend (from Research Item 6):**
Returns specific error messages:
- "Authorization required" (no token)
- "Token has expired" (exp claim passed)
- "Invalid token" (bad signature or format)
- "Invalid token: missing user_id" (missing 'sub' claim)

**Frontend API Client:**
```typescript
// frontend/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class AuthError extends Error {
  constructor(message: string, public statusCode: number) {
    super(message);
    this.name = "AuthError";
  }
}

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    credentials: "include", // Send cookies
  });

  // Handle authentication errors
  if (response.status === 401) {
    const error = await response.json().catch(() => ({
      detail: "Authentication required"
    }));

    // Show user-friendly toast
    showToast(getUserFriendlyMessage(error.detail));

    // Redirect to login
    window.location.href = "/login";

    throw new AuthError(error.detail, 401);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: "Request failed"
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

function getUserFriendlyMessage(technicalMessage: string): string {
  const messages: Record<string, string> = {
    "Authorization required": "Please log in to continue",
    "Token has expired": "Your session has expired. Please log in again.",
    "Invalid token": "Your session is invalid. Please log in again.",
    "Invalid token: missing user_id": "Authentication error. Please log in again.",
  };

  return messages[technicalMessage] || "Authentication error. Please log in again.";
}

function showToast(message: string) {
  // Implementation depends on toast library (e.g., react-hot-toast)
  // For Phase 2, simple implementation:
  alert(message); // Replace with toast UI in implementation
}

export const api = {
  getTasks: () => fetchWithAuth<Task[]>("/api/v1/tasks"),
  createTask: (data: TaskCreate) =>
    fetchWithAuth<Task>("/api/v1/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  // ... other methods
};
```

### Rationale
- **Centralized Handling:** All 401 errors handled in one place (DRY)
- **User-Friendly:** Technical errors translated to human-readable messages
- **Automatic Redirect:** User doesn't need to manually navigate to login
- **Toast Notification:** User sees why they're being redirected (better UX)

### Alternatives Considered
- **Per-component error handling:** Duplicates logic, rejected
- **Silent redirect:** Confusing for users, rejected
- **Retry logic:** Tokens don't auto-recover, rejected

---

## Research Item 8: CORS Configuration for Frontend-Backend Communication

### Decision
Configure FastAPI CORS middleware to allow frontend origin with credentials.

### Investigation
- **Same-Origin Policy:** Browser blocks cross-origin requests by default
- **Frontend Origin:** http://localhost:3000 (dev), https://your-domain.com (prod)
- **Backend Origin:** http://localhost:8000 (dev), https://api.your-domain.com (prod)
- **Credentials:** Required for sending cookies (credentials: 'include')
- **Allowed Headers:** Authorization, Content-Type
- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

### Implementation Pattern

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app = FastAPI(title="Task Management API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend dev server
        settings.frontend_url,     # Production frontend (from env)
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Length"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# ... routes
```

**Frontend Fetch Configuration:**
```typescript
// frontend/lib/api.ts
fetch(`${API_BASE}${endpoint}`, {
  credentials: "include", // Send cookies cross-origin
  // ... other options
});
```

### Rationale
- **Security:** Only specific origins allowed (not wildcard `*`)
- **Credentials:** Enables cookie-based auth
- **Performance:** max_age reduces preflight requests
- **Explicit Methods/Headers:** Principle of least privilege

### Alternatives Considered
- **Same-origin deployment:** Frontend and backend on same domain (complex setup, rejected for Phase 2)
- **Wildcard origins (`*`):** Insecure, doesn't work with credentials, rejected
- **Proxy:** Adds complexity, not needed for development, rejected

**Environment Variables:**
```bash
# backend/.env
FRONTEND_URL=http://localhost:3000  # Dev
# FRONTEND_URL=https://your-app.com  # Prod
```

**Resources:**
- [FastAPI CORS Docs](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

## Research Item 9: Testing Patterns for JWT-Based Authentication

### Decision
Mock JWT tokens in tests, test validation logic independently from Better Auth.

### Investigation
- **Frontend Tests:** Mock Better Auth methods, test UI components with fake sessions
- **Backend Tests:** Generate valid/invalid test JWT tokens, test dependency validation
- **E2E Tests:** Playwright with real auth flow (register → login → protected route)

### Implementation Pattern

**Backend Tests:**
```python
# backend/tests/fixtures/jwt_tokens.py
import jwt
from datetime import datetime, timedelta
from ..config import settings

def create_test_jwt(user_id: str = "test-user-123", expired: bool = False) -> str:
    """Generate a test JWT token."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=-1 if expired else 24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def create_invalid_jwt() -> str:
    """Generate JWT with wrong secret (invalid signature)."""
    payload = {
        "sub": "test-user-123",
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, "wrong-secret", algorithm="HS256")
```

```python
# backend/tests/test_dependencies.py
import pytest
from fastapi import HTTPException
from ..dependencies import get_current_user
from .fixtures.jwt_tokens import create_test_jwt, create_invalid_jwt

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Valid token returns user_id."""
    token = create_test_jwt(user_id="user-123")
    # Mock HTTPAuthorizationCredentials
    from fastapi.security import HTTPAuthorizationCredentials
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user_id = await get_current_user(credentials=credentials)
    assert user_id == "user-123"

@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    """Expired token raises 401."""
    token = create_test_jwt(expired=True)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()

@pytest.mark.asyncio
async def test_get_current_user_invalid_signature():
    """Invalid signature raises 401."""
    token = create_invalid_jwt()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert "invalid" in exc_info.value.detail.lower()

@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    """Missing token raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None, auth_token=None)

    assert exc_info.value.status_code == 401
    assert "required" in exc_info.value.detail.lower()
```

**Frontend Tests:**
```typescript
// frontend/tests/unit/useAuth.test.ts
import { renderHook, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { useAuth } from "@/hooks/useAuth";
import * as authLib from "@/lib/auth";

// Mock Better Auth
vi.mock("@/lib/auth", () => ({
  getSession: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

describe("useAuth", () => {
  it("returns session when user is logged in", async () => {
    const mockSession = {
      user: { id: "user-123", email: "test@example.com" },
    };
    vi.mocked(authLib.getSession).mockResolvedValue(mockSession);

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.session).toEqual(mockSession);
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  it("returns null when user is not logged in", async () => {
    vi.mocked(authLib.getSession).mockResolvedValue(null);

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.session).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });
});
```

**E2E Tests:**
```typescript
// frontend/tests/e2e/login.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test("user can register, login, and access protected routes", async ({ page }) => {
    // Register
    await page.goto("/register");
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL("/");

    // Logout
    await page.click("text=Log out");
    await expect(page).toHaveURL("/login");

    // Login
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');

    // Should redirect to dashboard again
    await expect(page).toHaveURL("/");

    // Should be able to access protected routes
    await page.goto("/tasks");
    await expect(page).toHaveURL("/tasks");
  });

  test("unauthenticated user is redirected to login", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page).toHaveURL("/login?redirect=/tasks");
  });
});
```

### Rationale
- **Unit Tests:** Fast, isolated, test validation logic without external dependencies
- **Mocking:** Better Auth methods mocked to avoid database calls in tests
- **E2E Tests:** Cover critical user flows with real browser interactions
- **Test Tokens:** Custom JWT generator creates valid/invalid tokens for all scenarios

### Alternatives Considered
- **Real database in tests:** Slow, flaky, rejected for unit tests (ok for integration tests)
- **No mocking:** Tests would depend on Better Auth internals, brittle, rejected
- **Only E2E tests:** Slow feedback loop, rejected

---

## Research Item 10: Accessibility Best Practices for Authentication Forms

### Decision
Follow WCAG 2.1 Level AA guidelines for authentication forms (labels, ARIA, keyboard navigation, focus management).

### Investigation
- **WCAG 2.1 AA:** Industry standard for web accessibility
- **Key Requirements:** Labels for inputs, error announcements, keyboard navigation, focus indicators
- **Tools:** Screen reader testing (NVDA, JAWS), keyboard-only navigation, automated tools (axe)

### Implementation Pattern

```typescript
// frontend/components/auth/LoginForm.tsx
"use client";
import { useState, useRef, useEffect } from "react";
import { signIn } from "@/lib/auth";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const emailInputRef = useRef<HTMLInputElement>(null);

  // Focus first field on mount
  useEffect(() => {
    emailInputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await signIn({ email, password });
      // Redirect handled by Better Auth
    } catch (err) {
      setError("Invalid email or password. Please try again.");
      setLoading(false);
      // Focus first field after error
      emailInputRef.current?.focus();
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* Error message with ARIA live region */}
      {error && (
        <div
          role="alert"
          aria-live="assertive"
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
        >
          <span className="sr-only">Error: </span>
          {error}
        </div>
      )}

      {/* Email field with label and validation */}
      <div className="mb-4">
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Email Address
          <span className="text-red-500" aria-label="required">*</span>
        </label>
        <input
          ref={emailInputRef}
          id="email"
          type="email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          aria-required="true"
          aria-invalid={!!error}
          aria-describedby={error ? "login-error" : undefined}
          autoComplete="email"
          disabled={loading}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Password field with toggle visibility */}
      <div className="mb-6">
        <label
          htmlFor="password"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Password
          <span className="text-red-500" aria-label="required">*</span>
        </label>
        <div className="relative">
          <input
            id="password"
            type="password"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-required="true"
            aria-invalid={!!error}
            autoComplete="current-password"
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {/* Password toggle button (implementation omitted for brevity) */}
        </div>
      </div>

      {/* Submit button with loading state */}
      <button
        type="submit"
        disabled={loading}
        aria-busy={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Logging in..." : "Log in"}
      </button>
    </form>
  );
}
```

**Key Accessibility Features:**
- **Labels:** All inputs have `<label>` elements with `htmlFor`
- **ARIA Attributes:**
  - `aria-required="true"` on required fields
  - `aria-invalid="true"` on fields with errors
  - `aria-describedby` links fields to error messages
  - `role="alert"` + `aria-live="assertive"` on error messages (announced immediately)
  - `aria-busy="true"` on submit button during loading
- **Keyboard Navigation:**
  - All interactive elements focusable (no `tabindex="-1"` on buttons/inputs)
  - Focus indicators visible (ring on focus)
  - Focus management: auto-focus on first field, return to first field on error
- **Semantic HTML:**
  - `<form>`, `<button type="submit">`, `<input type="email">`, `<input type="password">`
  - `<label>` instead of `<div>` for field labels
- **Screen Reader Support:**
  - Error messages announced (aria-live)
  - Required fields indicated (`<span class="sr-only">required</span>`)
  - Loading states announced (aria-busy)

### Rationale
- **Legal Compliance:** Many jurisdictions require WCAG 2.1 AA
- **Inclusive Design:** 15% of users have disabilities (WHO estimate)
- **Better UX for Everyone:** Clear labels and keyboard navigation benefit all users
- **SEO:** Semantic HTML improves search engine indexing

### Alternatives Considered
- **No accessibility:** Excludes users with disabilities, rejected
- **WCAG 2.1 AAA:** Overkill for Phase 2, more expensive, AA is sufficient
- **Custom ARIA widgets:** Complex, error-prone, use native HTML instead

**Testing Tools:**
- [axe DevTools](https://www.deque.com/axe/devtools/) - Automated accessibility testing
- [NVDA Screen Reader](https://www.nvaccess.org/) - Free Windows screen reader
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Accessibility audit

**Resources:**
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN: ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [WebAIM: Form Accessibility](https://webaim.org/techniques/forms/)

---

## Summary of Decisions

| Research Item | Decision | Key Technology |
|---------------|----------|----------------|
| 1. Better Auth Config | Official Next.js 16 App Router integration | better-auth/nextjs, Drizzle ORM |
| 2. JWT Secret Sharing | Single `.env` file with JWT_SECRET variable | Environment variables |
| 3. HTTP-Only Cookies | SameSite=Strict, Secure, HttpOnly, 24hr expiry | Better Auth cookie config |
| 4. Better Auth Schema | Automatic schema generation, separate DB from backend | Drizzle migrations |
| 5. Frontend Middleware | Next.js middleware with session check | middleware.ts |
| 6. Backend JWT Validation | PyJWT with HS256, FastAPI Depends() | PyJWT, dependency injection |
| 7. Error Handling | Centralized 401 handling in API client, user-friendly messages | fetchWithAuth wrapper |
| 8. CORS Configuration | FastAPI CORS middleware with credentials | CORSMiddleware |
| 9. Testing Patterns | Mock JWT tokens, unit + E2E tests | Pytest, Vitest, Playwright |
| 10. Accessibility | WCAG 2.1 AA compliance, ARIA, keyboard navigation | Semantic HTML, ARIA attributes |

---

## Next Steps

1. **Phase 1: Generate data-model.md** - Document user_id field in tasks table (no users table)
2. **Phase 1: Generate API contracts** - JWT validation and Better Auth flow specifications
3. **Phase 1: Generate quickstart.md** - Developer setup guide with step-by-step instructions
4. **Phase 2: Generate tasks.md** - TDD tasks for implementation (red-green-refactor)

All research unknowns are now resolved. Proceed to Phase 1 design artifacts.
