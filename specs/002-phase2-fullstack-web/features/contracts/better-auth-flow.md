# API Contract: Better Auth Frontend Authentication Flow

**Feature:** User Authentication
**Component:** Frontend Authentication (Better Auth)
**Date:** 2025-12-21
**Status:** Contract Approved
**Type:** Frontend Authentication Service

## Summary

This contract defines the authentication flow managed by Better Auth on the frontend. Better Auth handles user registration, login, logout, session management, and JWT token issuance. The frontend uses Better Auth's Next.js integration to create API routes at `/api/auth/*` that manage all authentication operations. Better Auth stores user credentials in a separate PostgreSQL database and issues JWT tokens that the backend validates. This contract documents all Better Auth methods, flows, and integration points with the Next.js application.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐         ┌──────────────────┐       │
│  │ User Interacts │────────>│ Better Auth      │       │
│  │ with Login/    │         │ Methods          │       │
│  │ Register Form  │         │ (signIn, signUp) │       │
│  └────────────────┘         └─────────┬────────┘       │
│                                       │                 │
│                                       ↓                 │
│                            ┌──────────────────┐         │
│                            │ Better Auth      │         │
│                            │ API Routes       │         │
│                            │ /api/auth/*      │         │
│                            └─────────┬────────┘         │
│                                      │                  │
│                                      ↓                  │
│                           ┌─────────────────┐           │
│                           │ PostgreSQL DB   │           │
│                           │ (User Storage)  │           │
│                           └─────────┬───────┘           │
│                                     │                   │
│                                     ↓                   │
│                          ┌──────────────────┐           │
│                          │ JWT Token Issued │           │
│                          │ Set in Cookie    │           │
│                          └──────────┬───────┘           │
└─────────────────────────────────────┼───────────────────┘
                                      │
                                      ↓
                         ┌────────────────────────┐
                         │  Backend API Requests  │
                         │  (with JWT in cookie)  │
                         └────────────────────────┘
```

**Key Principle:** Better Auth manages ALL authentication operations on the frontend. The backend NEVER creates, updates, or deletes users - it only validates JWT tokens.

---

## Better Auth Configuration

### Setup and Installation

**Dependencies:**
```bash
npm install better-auth drizzle-orm postgres
```

**Configuration File:**
```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  // Database adapter (Drizzle with PostgreSQL)
  database: drizzleAdapter(db, {
    provider: "pg",
  }),

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24,  // 24 hours
    updateAge: 60 * 60,        // Update session every hour
    cookieName: "auth-token",
    cookieOptions: {
      httpOnly: true,
      sameSite: "strict",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24,  // 24 hours
    },
  },

  // JWT configuration
  jwt: {
    secret: process.env.JWT_SECRET!,
    expiresIn: 60 * 60 * 24,  // 24 hours
    algorithm: "HS256",
  },

  // Trusted origins for CORS
  trustedOrigins: [
    process.env.NEXT_PUBLIC_API_URL!,  // Backend API URL
  ],

  // Base URL for API routes
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
});

// Export client methods
export const { signIn, signUp, signOut, getSession } = auth;
```

**API Routes Setup:**
```typescript
// frontend/app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/nextjs";

// Better Auth creates all auth endpoints automatically
export const { GET, POST } = toNextJsHandler(auth);
```

**Environment Variables:**
```bash
# frontend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/frontend_auth
JWT_SECRET=your-super-secret-key-at-least-256-bits-long-random-string
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

---

## Authentication Methods

### Method 1: signUp()

**Purpose:** Register a new user account

**Function Signature:**
```typescript
async function signUp(credentials: {
  email: string;
  password: string;
  name?: string;
}): Promise<{
  user: User;
  session: Session;
}>
```

**Input:**
- **email** (required): Valid email address (max 254 characters)
- **password** (required): Password (min 8 characters, max 128 characters)
- **name** (optional): Display name (max 255 characters)

**Process:**
1. Validate email format and password length
2. Check if email already exists in database
3. Hash password with bcrypt (work factor 10+)
4. Create user record in database
5. Generate JWT token with user_id in 'sub' claim
6. Set HTTP-only cookie with JWT token
7. Create session record
8. Return user and session objects

**Success Response:**
```typescript
{
  user: {
    id: "550e8400-e29b-41d4-a716-446655440000",  // UUID
    email: "user@example.com",
    emailVerified: false,
    name: "John Doe",
    createdAt: "2025-12-21T10:00:00Z",
    updatedAt: "2025-12-21T10:00:00Z"
  },
  session: {
    id: "session-uuid",
    expiresAt: "2025-12-22T10:00:00Z",  // 24 hours later
    userId: "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Errors:**
- **400 Bad Request:** Email already registered
  ```json
  {
    "error": "Email already registered",
    "code": "EMAIL_EXISTS"
  }
  ```
- **400 Bad Request:** Invalid email format
  ```json
  {
    "error": "Invalid email address",
    "code": "INVALID_EMAIL"
  }
  ```
- **400 Bad Request:** Password too short
  ```json
  {
    "error": "Password must be at least 8 characters",
    "code": "PASSWORD_TOO_SHORT"
  }
  ```

**Usage Example:**
```typescript
// frontend/components/auth/RegisterForm.tsx
"use client";
import { signUp } from "@/lib/auth";
import { useRouter } from "next/navigation";

export function RegisterForm() {
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    try {
      await signUp({
        email: formData.get("email") as string,
        password: formData.get("password") as string,
      });

      // Redirect to dashboard after successful registration
      router.push("/");
    } catch (error) {
      // Handle error (show error message to user)
      console.error("Registration failed:", error);
    }
  };

  return <form onSubmit={handleSubmit}>{/* Form fields */}</form>;
}
```

**Side Effects:**
- ✅ User record created in database
- ✅ Password hashed and stored securely
- ✅ JWT token issued and stored in HTTP-only cookie
- ✅ User automatically logged in after registration
- ✅ Session created

---

### Method 2: signIn()

**Purpose:** Authenticate existing user with email and password

**Function Signature:**
```typescript
async function signIn(credentials: {
  email: string;
  password: string;
}): Promise<{
  user: User;
  session: Session;
}>
```

**Input:**
- **email** (required): User's email address
- **password** (required): User's password

**Process:**
1. Look up user by email in database
2. If user not found, return error "Invalid email or password"
3. Retrieve hashed password from database
4. Verify password using bcrypt compare
5. If password doesn't match, return error "Invalid email or password"
6. Generate JWT token with user_id in 'sub' claim
7. Set HTTP-only cookie with JWT token
8. Create new session record
9. Return user and session objects

**Success Response:**
```typescript
{
  user: {
    id: "550e8400-e29b-41d4-a716-446655440000",
    email: "user@example.com",
    emailVerified: false,
    name: "John Doe",
    createdAt: "2025-12-21T09:00:00Z",
    updatedAt: "2025-12-21T10:00:00Z"
  },
  session: {
    id: "session-uuid",
    expiresAt: "2025-12-22T10:00:00Z",
    userId: "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Errors:**
- **401 Unauthorized:** Invalid credentials
  ```json
  {
    "error": "Invalid email or password",
    "code": "INVALID_CREDENTIALS"
  }
  ```
- **400 Bad Request:** Missing email or password
  ```json
  {
    "error": "Email and password are required",
    "code": "MISSING_CREDENTIALS"
  }
  ```

**Usage Example:**
```typescript
// frontend/components/auth/LoginForm.tsx
"use client";
import { signIn } from "@/lib/auth";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    try {
      await signIn({
        email: formData.get("email") as string,
        password: formData.get("password") as string,
      });

      // Redirect to dashboard after successful login
      router.push("/");
    } catch (error) {
      // Handle error (show error message to user)
      console.error("Login failed:", error);
    }
  };

  return <form onSubmit={handleSubmit}>{/* Form fields */}</form>;
}
```

**Side Effects:**
- ✅ JWT token issued and stored in HTTP-only cookie
- ✅ New session created (or existing session updated)
- ✅ User redirected to dashboard

**Security Notes:**
- Passwords are NEVER logged or returned in responses
- Password verification uses constant-time comparison (bcrypt prevents timing attacks)
- Failed login attempts do not reveal whether email exists (generic error message)

---

### Method 3: signOut()

**Purpose:** End user's session and clear authentication cookie

**Function Signature:**
```typescript
async function signOut(): Promise<void>
```

**Input:** None (reads session from cookie)

**Process:**
1. Read auth-token cookie
2. Decode JWT to get session ID
3. Delete session from database
4. Clear auth-token cookie from browser
5. Return success (no response body)

**Success Response:**
- **Status:** 200 OK (no body)
- **Side Effect:** Cookie cleared, session deleted

**Errors:**
- **401 Unauthorized:** No active session (user already logged out)
  ```json
  {
    "error": "No active session",
    "code": "NO_SESSION"
  }
  ```

**Usage Example:**
```typescript
// frontend/components/auth/LogoutButton.tsx
"use client";
import { signOut } from "@/lib/auth";
import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await signOut();

      // Redirect to login page after logout
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      // Even if error, still redirect to login
      router.push("/login");
    }
  };

  return <button onClick={handleLogout}>Log out</button>;
}
```

**Side Effects:**
- ✅ HTTP-only cookie cleared from browser
- ✅ Session deleted from database
- ✅ User cannot make authenticated requests until re-login

---

### Method 4: getSession()

**Purpose:** Check if user is authenticated and retrieve session data

**Function Signature:**
```typescript
async function getSession(): Promise<{
  user: User;
  session: Session;
} | null>
```

**Input:** None (reads session from cookie)

**Process:**
1. Read auth-token cookie
2. If cookie missing, return null
3. Decode and validate JWT token
4. Check if token is expired
5. Look up session in database
6. If session expired, return null
7. Look up user by user_id from JWT
8. Return user and session objects

**Success Response (Authenticated):**
```typescript
{
  user: {
    id: "550e8400-e29b-41d4-a716-446655440000",
    email: "user@example.com",
    emailVerified: false,
    name: "John Doe",
    createdAt: "2025-12-21T09:00:00Z",
    updatedAt: "2025-12-21T10:00:00Z"
  },
  session: {
    id: "session-uuid",
    expiresAt: "2025-12-22T10:00:00Z",
    userId: "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Success Response (Not Authenticated):**
```typescript
null
```

**Usage Example (Server Component):**
```typescript
// frontend/app/page.tsx
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login");  // Not authenticated, redirect to login
  }

  return (
    <div>
      <h1>Welcome, {session.user.email}!</h1>
      {/* Dashboard content */}
    </div>
  );
}
```

**Usage Example (Client Component with Hook):**
```typescript
// frontend/hooks/useAuth.ts
"use client";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

export function useAuth() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSession() {
      const session = await getSession();
      setSession(session);
      setLoading(false);
    }
    loadSession();
  }, []);

  return {
    session,
    user: session?.user ?? null,
    isAuthenticated: !!session,
    loading,
  };
}
```

**Usage in Client Component:**
```typescript
// frontend/components/UserProfile.tsx
"use client";
import { useAuth } from "@/hooks/useAuth";

export function UserProfile() {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Not logged in</div>;

  return <div>Logged in as {user.email}</div>;
}
```

**Side Effects:** None (read-only operation)

---

## Auto-Generated API Routes

Better Auth automatically creates API routes at `/api/auth/*` when you use `toNextJsHandler()`:

### POST /api/auth/sign-up

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"  // Optional
}
```

**Success Response (200 OK):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "emailVerified": false,
    "name": "John Doe",
    "createdAt": "2025-12-21T10:00:00Z",
    "updatedAt": "2025-12-21T10:00:00Z"
  },
  "session": {
    "id": "session-uuid",
    "expiresAt": "2025-12-22T10:00:00Z",
    "userId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Sets Cookie:**
```http
Set-Cookie: auth-token=<JWT_TOKEN>; HttpOnly; SameSite=Strict; Secure; Path=/; Max-Age=86400
```

### POST /api/auth/sign-in

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Success Response (200 OK):**
```json
{
  "user": { /* ... */ },
  "session": { /* ... */ }
}
```

**Sets Cookie:** Same as sign-up

### POST /api/auth/sign-out

**Request:** No body (reads cookie)

**Success Response (200 OK):**
```json
{
  "success": true
}
```

**Clears Cookie:**
```http
Set-Cookie: auth-token=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0
```

### GET /api/auth/session

**Request:** No body (reads cookie)

**Success Response (200 OK - Authenticated):**
```json
{
  "user": { /* ... */ },
  "session": { /* ... */ }
}
```

**Success Response (200 OK - Not Authenticated):**
```json
null
```

---

## Middleware Integration (Protected Routes)

**Purpose:** Automatically redirect unauthenticated users to login page

**Implementation:**
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
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If user is logged in and tries to access auth pages, redirect to dashboard
  if (isPublicRoute && session) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Allow access to protected route
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
```

**Behavior:**
- ✅ Unauthenticated users accessing `/` → redirected to `/login?redirect=/`
- ✅ Authenticated users accessing `/login` → redirected to `/`
- ✅ Public routes (`/login`, `/register`) accessible to all
- ✅ API routes (`/api/auth/*`) always accessible
- ✅ Static files and images not protected

---

## JWT Token Format

### Issued by Better Auth

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "iat": 1734705600,  // Issued at (Unix timestamp)
  "exp": 1734792000,  // Expiration (24 hours later)
  "iss": "better-auth",  // Issuer
  "aud": "task-api"  // Audience (optional)
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  JWT_SECRET
)
```

**Cookie Value:**
```http
auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJpYXQiOjE3MzQ3MDU2MDAsImV4cCI6MTczNDc5MjAwMCwiaXNzIjoiYmV0dGVyLWF1dGgiLCJhdWQiOiJ0YXNrLWFwaSJ9.signature
```

---

## User Data Model (Better Auth Managed)

Better Auth creates these tables automatically:

**Table: `user`**
```sql
CREATE TABLE "user" (
  "id" TEXT PRIMARY KEY,  -- UUID
  "email" TEXT NOT NULL UNIQUE,
  "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
  "name" TEXT,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
  "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Table: `password`**
```sql
CREATE TABLE "password" (
  "hash" TEXT NOT NULL,  -- bcrypt hash
  "userId" TEXT NOT NULL PRIMARY KEY REFERENCES "user"("id") ON DELETE CASCADE
);
```

**Table: `session`**
```sql
CREATE TABLE "session" (
  "id" TEXT PRIMARY KEY,
  "expiresAt" TIMESTAMP NOT NULL,
  "ipAddress" TEXT,
  "userAgent" TEXT,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## Security Guarantees

**Better Auth Provides:**
- ✅ Password hashing with bcrypt (work factor 10+)
- ✅ HTTP-only cookies (prevents XSS attacks)
- ✅ SameSite=Strict cookies (prevents CSRF attacks)
- ✅ Secure flag in production (requires HTTPS)
- ✅ JWT expiration (24 hours, prevents long-term exposure)
- ✅ Constant-time password comparison (prevents timing attacks)
- ✅ Email uniqueness validation (prevents duplicate accounts)
- ✅ SQL injection protection (parameterized queries via Drizzle ORM)

**Developer Responsibilities:**
- ⚠️ Keep JWT_SECRET secure (never commit to git)
- ⚠️ Use HTTPS in production (Secure cookie flag)
- ⚠️ Validate input on forms (client-side validation)
- ⚠️ Handle errors gracefully (don't expose sensitive info)

---

## Testing Better Auth

### Mock Better Auth Methods

```typescript
// frontend/tests/mocks/auth.ts
import { vi } from "vitest";

export const mockSignUp = vi.fn();
export const mockSignIn = vi.fn();
export const mockSignOut = vi.fn();
export const mockGetSession = vi.fn();

vi.mock("@/lib/auth", () => ({
  signUp: mockSignUp,
  signIn: mockSignIn,
  signOut: mockSignOut,
  getSession: mockGetSession,
}));
```

### Unit Test Example

```typescript
// frontend/tests/unit/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { mockSignIn } from "../mocks/auth";
import { LoginForm } from "@/components/auth/LoginForm";

describe("LoginForm", () => {
  it("calls signIn with email and password", async () => {
    mockSignIn.mockResolvedValue({
      user: { id: "user-123", email: "test@example.com" },
      session: { id: "session-123" },
    });

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Log in" }));

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      });
    });
  });
});
```

### E2E Test Example

```typescript
// frontend/tests/e2e/auth-flow.spec.ts
import { test, expect } from "@playwright/test";

test("user can register, login, and logout", async ({ page }) => {
  // Register
  await page.goto("/register");
  await page.fill('input[name="email"]', "newuser@example.com");
  await page.fill('input[name="password"]', "password123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");  // Redirected to dashboard

  // Logout
  await page.click("text=Log out");
  await expect(page).toHaveURL("/login");

  // Login
  await page.fill('input[name="email"]', "newuser@example.com");
  await page.fill('input[name="password"]', "password123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");  // Redirected to dashboard again
});
```

---

## Error Handling

### Frontend Error Handling Pattern

```typescript
// frontend/components/auth/LoginForm.tsx
import { signIn } from "@/lib/auth";

export function LoginForm() {
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");  // Clear previous errors

    try {
      await signIn({ email, password });
      router.push("/");
    } catch (err: any) {
      // Better Auth errors have error.code and error.message
      if (err.code === "INVALID_CREDENTIALS") {
        setError("Invalid email or password. Please try again.");
      } else if (err.code === "NETWORK_ERROR") {
        setError("Network error. Please check your connection.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div role="alert">{error}</div>}
      {/* Form fields */}
    </form>
  );
}
```

---

## Summary

**Better Auth Provides:**
- ✅ Complete authentication system (registration, login, logout)
- ✅ JWT token generation and management
- ✅ HTTP-only cookie storage (secure)
- ✅ Session management
- ✅ Password hashing (bcrypt)
- ✅ Database integration (Drizzle ORM)
- ✅ Next.js 16 App Router integration
- ✅ TypeScript support
- ✅ Security best practices (CSRF, XSS, SQL injection protection)

**Frontend Responsibilities:**
- ✅ Call Better Auth methods (signIn, signUp, signOut, getSession)
- ✅ Handle errors and display user-friendly messages
- ✅ Redirect users based on authentication state
- ✅ Protect routes with middleware
- ✅ Configure JWT secret and database connection

**Backend Responsibilities:**
- ✅ Validate JWT tokens (see jwt-validation.md contract)
- ✅ Extract user_id from tokens
- ✅ Enforce user isolation in queries
- ❌ NO user management (Better Auth handles this)

This contract defines the complete frontend authentication flow managed by Better Auth. The backend only validates JWT tokens - it never creates, updates, or deletes users.
