---
name: better-auth-integrator
description: Set up Better Auth for frontend authentication with JWT token generation and secure cookie storage. Use when (1) setting up authentication in frontend, (2) configuring JWT token handling, (3) implementing login/logout flows, or (4) user asks about auth setup.
license: Complete terms in LICENSE.txt
---

# Better Auth Integrator

Configure Better Auth in Next.js for JWT-based authentication following ADR-004 architecture patterns.

## Workflow

Follow these steps when setting up Better Auth:

1. **Configure Better Auth in Next.js**
   - Install Better Auth packages
   - Set up auth configuration
   - Configure providers (email/password, OAuth)
   - Set JWT secret and options

2. **Set up JWT token generation**
   - Configure JWT signing algorithm
   - Define token payload (user_id, email)
   - Set token expiration
   - Share secret with backend

3. **Implement secure cookie storage**
   - HTTP-only cookies for tokens
   - Secure flag in production
   - SameSite configuration
   - Cookie expiration matches token

4. **Create auth hooks and utilities**
   - useAuth() hook for client components
   - getSession() for server components
   - Login/logout helpers
   - Protected route middleware

5. **Connect auth to API client**
   - Auto-include JWT in requests
   - Handle token refresh
   - Redirect on 401 errors
   - Clear auth on logout

## Output Format

Present Better Auth setup using this structure:

```
🔑 Auth Setup: [component/feature]

Configuration:
- Provider: Better Auth
- Token: JWT in HTTP-only cookie
- Algorithm: HS256
- Secret: From JWT_SECRET env var

Files Created/Modified:
- lib/auth.ts (Better Auth server config)
- lib/auth-client.ts (Client utilities)
- app/api/auth/[...all]/route.ts (Auth API routes)
- middleware.ts (Route protection)

Environment Variables:
- JWT_SECRET (shared with backend)
- BETTER_AUTH_URL
- BETTER_AUTH_SECRET

Next Steps:
1. Add login/signup pages
2. Implement protected routes
3. Connect to API client
```

## Required File Structure

```
frontend/
├── lib/
│   ├── auth.ts              # Better Auth server config
│   └── auth-client.ts       # Client-side auth utilities
│
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts # Better Auth API routes
│   │
│   ├── login/
│   │   └── page.tsx         # Login page
│   │
│   └── signup/
│       └── page.tsx         # Signup page
│
├── middleware.ts            # Protect routes
└── .env.local               # Environment variables
```

## Better Auth Server Configuration

**lib/auth.ts:**
```typescript
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

export const auth = betterAuth({
  database: {
    // Better Auth manages user storage
    provider: "sqlite",  // or "postgres" for production
    url: process.env.DATABASE_URL!
  },

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,  // Enable in production
  },

  // Optional: OAuth providers
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    },
  },

  session: {
    // JWT configuration
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours

    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7, // 7 days
    },
  },

  // JWT settings
  secret: process.env.JWT_SECRET!,  // MUST match backend

  // Cookie settings
  advanced: {
    cookiePrefix: "better-auth",
    useSecureCookies: process.env.NODE_ENV === "production",
    crossSubDomainCookies: {
      enabled: false,
    },
  },

  plugins: [
    nextCookies()  // Next.js cookie handling
  ],
});

export type Session = typeof auth.$Infer.Session;
```

**lib/auth-client.ts:**
```typescript
import { createAuthClient } from "better-auth/client";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",
});

// Client-side auth hooks
export const {
  useSession,
  signIn,
  signUp,
  signOut,
} = authClient;
```

**app/api/auth/[...all]/route.ts:**
```typescript
import { auth } from "@/lib/auth";

export const { GET, POST } = auth.handler;
```

## Authentication Flow (ADR-004)

```
┌─────────────────────────────────────────────────────┐
│ User Action                                         │
└───────────────────────┬─────────────────────────────┘
                        │
                        │ Email/Password or OAuth
                        ↓
┌─────────────────────────────────────────────────────┐
│ Better Auth (Frontend)                              │
├─────────────────────────────────────────────────────┤
│ 1. Validates credentials                            │
│ 2. Creates user record (in Better Auth DB)          │
│ 3. Generates JWT token with user_id                 │
│ 4. Sets HTTP-only cookie                            │
└───────────────────────┬─────────────────────────────┘
                        │
                        │ JWT Cookie: { sub: user_id, email, exp }
                        ↓
┌─────────────────────────────────────────────────────┐
│ Protected Page/Component                            │
├─────────────────────────────────────────────────────┤
│ - JWT automatically included in API requests        │
│ - Backend validates JWT signature                   │
│ - Backend extracts user_id from token               │
└─────────────────────────────────────────────────────┘
```

## Protected Routes with Middleware

**middleware.ts:**
```typescript
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { auth } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  // Protect routes that require authentication
  const protectedPaths = ["/tasks", "/profile", "/settings"];
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (isProtectedPath && !session?.user) {
    // Redirect to login if not authenticated
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect authenticated users away from auth pages
  const authPaths = ["/login", "/signup"];
  const isAuthPath = authPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (isAuthPath && session?.user) {
    return NextResponse.redirect(new URL("/tasks", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/tasks/:path*",
    "/profile/:path*",
    "/settings/:path*",
    "/login",
    "/signup",
  ],
};
```

## Login Page Example

**app/login/page.tsx:**
```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signIn } from "@/lib/auth-client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const { data, error: signInError } = await signIn.email({
        email,
        password,
      });

      if (signInError) {
        throw new Error(signInError.message);
      }

      // JWT cookie is set automatically
      router.push("/tasks");
      router.refresh();

    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Login</h1>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}
```

## Using Auth in Components

**Server Component (get session):**
```typescript
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export default async function ProfilePage() {
  const session = await auth.api.getSession({
    headers: await headers()
  });

  if (!session?.user) {
    redirect("/login");
  }

  return (
    <div>
      <h1>Welcome, {session.user.email}</h1>
      <p>User ID: {session.user.id}</p>
    </div>
  );
}
```

**Client Component (use hook):**
```typescript
"use client";

import { useSession, signOut } from "@/lib/auth-client";

export function UserMenu() {
  const { data: session, isPending } = useSession();

  if (isPending) return <div>Loading...</div>;

  if (!session?.user) {
    return <a href="/login">Login</a>;
  }

  return (
    <div>
      <span>{session.user.email}</span>
      <button onClick={() => signOut()}>
        Logout
      </button>
    </div>
  );
}
```

## Environment Variables

**.env.local:**
```bash
# JWT Secret (MUST match backend)
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-better-auth-secret

# Database for Better Auth user storage
DATABASE_URL=file:./auth.db  # SQLite for dev
# DATABASE_URL=postgres://... # PostgreSQL for production

# Optional: OAuth providers
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Backend Coordination

**Important: Backend must validate JWT tokens**

The backend receives JWT tokens and must:
1. Validate signature using same JWT_SECRET
2. Extract user_id from `sub` claim
3. Use user_id for all database queries

**Backend validation example (FastAPI):**
```python
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,  # MUST match frontend
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401)
        return user_id
    except JWTError:
        raise HTTPException(status_code=401)
```

## Key Rules

- **JWT secret shared with backend** - Same JWT_SECRET in both .env files
- **HTTP-only cookies** - Prevents XSS attacks
- **Frontend issues tokens** - Better Auth creates and manages JWTs
- **Backend validates tokens** - Verifies signature and extracts user_id
- **Include user_id in JWT** - Stored in `sub` claim
- **Protect routes with middleware** - Redirect unauthenticated users
- **No users table in backend** - Better Auth manages user data
- **Secure cookies in production** - Set secure flag for HTTPS
- **Handle 401 errors** - Redirect to login on token expiration
- **Session refresh** - Update tokens before expiration
