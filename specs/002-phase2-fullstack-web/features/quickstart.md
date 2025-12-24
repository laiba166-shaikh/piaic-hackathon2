# Quickstart Guide: User Authentication Setup

**Feature:** User Authentication
**Date:** 2025-12-21
**Status:** Ready for Implementation
**Estimated Setup Time:** 30-45 minutes

## Summary

This quickstart guide walks through setting up the complete user authentication system for Phase 2, including Better Auth on the frontend, JWT validation on the backend, and all required dependencies. By the end of this guide, you'll have a working authentication system where users can register, log in, log out, and access protected routes.

---

## Prerequisites

Before starting, ensure you have:

- **Node.js:** 18.x or higher
- **Python:** 3.11 or higher
- **PostgreSQL:** 14.x or higher (or Neon PostgreSQL account)
- **Git:** For version control
- **Code Editor:** VSCode, WebStorm, or similar
- **Terminal:** Bash, PowerShell, or similar

---

## Architecture Recap

```
Frontend (Next.js)                Backend (FastAPI)
- Better Auth                     - JWT Validation
- User Management                 - User Isolation
- JWT Token Issuance              - NO User Table
- Frontend Database               - Backend Database (tasks only)
```

**Important:** Frontend and backend use SEPARATE PostgreSQL databases.

---

## Part 1: Environment Setup

### Step 1.1: Generate JWT Secret

Generate a secure random secret for JWT token signing/validation:

```bash
# On macOS/Linux
openssl rand -base64 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))

# Example output:
# 8xVq9P2nL4mK7jH5gF3dS1aZ0wY9xC8vB7nM6kJ5hG4fE3dD2cB1a=
```

**Copy this output** - you'll use it in both frontend and backend `.env` files.

### Step 1.2: Setup PostgreSQL Databases

You need TWO separate PostgreSQL databases:

**Option A: Local PostgreSQL**

```bash
# Create frontend database (Better Auth)
createdb frontend_auth

# Create backend database (Task Management)
createdb backend_tasks

# Verify databases exist
psql -l
```

**Option B: Neon PostgreSQL (Serverless)**

1. Go to https://neon.tech/
2. Create a new project: "hackathon2-frontend"
3. Copy connection string (e.g., `postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/neondb`)
4. Create another project: "hackathon2-backend"
5. Copy connection string

**Save both connection strings** - you'll use them in `.env` files.

---

## Part 2: Frontend Setup (Better Auth)

### Step 2.1: Install Frontend Dependencies

```bash
cd frontend

# Install Next.js, React, and Better Auth dependencies
npm install better-auth drizzle-orm postgres
npm install -D drizzle-kit @types/node

# Install additional dependencies
npm install react react-dom next
npm install -D typescript @types/react @types/react-dom

# Verify installation
npm list better-auth drizzle-orm
```

### Step 2.2: Configure Frontend Environment Variables

Create `frontend/.env.local`:

```bash
# Database connection (Frontend - Better Auth)
DATABASE_URL=postgresql://user:password@localhost:5432/frontend_auth

# JWT Secret (MUST match backend)
JWT_SECRET=8xVq9P2nL4mK7jH5gF3dS1aZ0wY9xC8vB7nM6kJ5hG4fE3dD2cB1a=

# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

**Important:**
- Replace `DATABASE_URL` with your frontend database connection string
- Use the JWT secret generated in Step 1.1
- DO NOT commit `.env.local` to git (add to `.gitignore`)

### Step 2.3: Setup Drizzle Database Client

Create `frontend/lib/db.ts`:

```typescript
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is required");
}

const connectionString = process.env.DATABASE_URL;
const client = postgres(connectionString);

export const db = drizzle(client);
```

### Step 2.4: Configure Better Auth

Create `frontend/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
  }),

  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  session: {
    expiresIn: 60 * 60 * 24,  // 24 hours
    updateAge: 60 * 60,        // Update every hour
    cookieName: "auth-token",
    cookieOptions: {
      httpOnly: true,
      sameSite: "strict",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24,
    },
  },

  jwt: {
    secret: process.env.JWT_SECRET!,
    expiresIn: 60 * 60 * 24,
    algorithm: "HS256",
  },

  trustedOrigins: [
    process.env.NEXT_PUBLIC_API_URL!,
  ],

  baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
});

export const { signIn, signUp, signOut, getSession } = auth;
```

### Step 2.5: Create Better Auth API Routes

Create `frontend/app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/nextjs";

export const { GET, POST } = toNextJsHandler(auth);
```

This creates all authentication endpoints automatically:
- `POST /api/auth/sign-up`
- `POST /api/auth/sign-in`
- `POST /api/auth/sign-out`
- `GET /api/auth/session`

### Step 2.6: Run Better Auth Migrations

Better Auth will auto-create tables on first run. Start the dev server to trigger migrations:

```bash
cd frontend
npm run dev
```

**Check logs for:**
```
Better Auth: Database tables created successfully
  - user
  - password
  - session
  - account
  - verification
```

**Verify in database:**
```bash
psql frontend_auth

# List tables
\dt

# Should see:
# user
# password
# session
# account
# verification
```

---

## Part 3: Backend Setup (JWT Validation)

### Step 3.1: Install Backend Dependencies

```bash
cd backend

# Install FastAPI and JWT dependencies
pip install fastapi uvicorn pyjwt sqlmodel psycopg2-binary pydantic-settings

# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Verify installation
pip list | grep -E "fastapi|pyjwt|sqlmodel"
```

### Step 3.2: Configure Backend Environment Variables

Create `backend/.env`:

```bash
# Database connection (Backend - Task Management)
DATABASE_URL=postgresql://user:password@localhost:5432/backend_tasks

# JWT Secret (MUST match frontend)
JWT_SECRET=8xVq9P2nL4mK7jH5gF3dS1aZ0wY9xC8vB7nM6kJ5hG4fE3dD2cB1a=

# JWT Configuration
JWT_ALGORITHM=HS256

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

**Important:**
- Replace `DATABASE_URL` with your backend database connection string
- Use the SAME JWT secret as frontend (from Step 1.1)
- DO NOT commit `.env` to git (add to `.gitignore`)

### Step 3.3: Create Settings Configuration

Create `backend/config.py`:

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")
        if len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")

settings = Settings()
```

### Step 3.4: Create JWT Validation Dependency

Create `backend/dependencies.py`:

```python
from fastapi import Depends, HTTPException, Security, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from .config import settings

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    auth_token: Optional[str] = Cookie(None, alias="auth-token")
) -> str:
    """
    Validate JWT token and extract user_id from 'sub' claim.

    Args:
        credentials: JWT token from Authorization header
        auth_token: JWT token from HTTP-only cookie

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

### Step 3.5: Setup FastAPI with CORS

Create `backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="Backend API for task management with JWT authentication"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend dev server
        settings.frontend_url,     # Production frontend
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Length"],
    max_age=600,
)

@app.get("/")
async def root():
    return {"message": "Task Management API - Phase 2"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Step 3.6: Create Backend Database Tables

Create `backend/models.py`:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)  # From JWT 'sub' claim
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

Create `backend/create_db.py`:

```python
from sqlmodel import SQLModel, create_engine
from .config import settings
from .models import Task

engine = create_engine(settings.database_url)

def create_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    create_tables()
```

Run the database creation script:

```bash
cd backend
python -m backend.create_db
```

**Verify in database:**
```bash
psql backend_tasks

# List tables
\dt

# Describe tasks table
\d tasks

# Should see:
# - id (integer, primary key)
# - user_id (varchar, indexed)
# - title, description, completed, etc.
```

### Step 3.7: Start Backend Server

```bash
cd backend
uvicorn backend.main:app --reload --port 8000
```

**Check logs for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## Part 4: Verification

### Step 4.1: Test Frontend (Better Auth)

**Open browser:** http://localhost:3000

**Create test user via API:**
```bash
curl -X POST http://localhost:3000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Expected Response:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "emailVerified": false,
    "createdAt": "2025-12-21T10:00:00Z"
  },
  "session": {
    "id": "session-uuid",
    "expiresAt": "2025-12-22T10:00:00Z",
    "userId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Verify in database:**
```bash
psql frontend_auth
SELECT * FROM "user";
# Should see: test@example.com user record
```

### Step 4.2: Test Backend (JWT Validation)

**Get JWT token from sign-up response** (or login):

```bash
# Login to get token
curl -X POST http://localhost:3000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt -v

# Extract token from Set-Cookie header
# Look for: Set-Cookie: auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Test backend endpoint with JWT:**

```bash
# Test with Authorization header
curl -X GET http://localhost:8000/health \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Test with cookie
curl -X GET http://localhost:8000/health \
  -b cookies.txt
```

**Expected:** Backend accepts request, no 401 error.

### Step 4.3: Test End-to-End Flow

**Test the complete authentication flow:**

1. **Register new user:**
   ```bash
   curl -X POST http://localhost:3000/api/auth/sign-up \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password123"}' \
     -c cookies.txt
   ```

2. **Verify session exists:**
   ```bash
   curl -X GET http://localhost:3000/api/auth/session \
     -b cookies.txt
   ```
   Expected: User and session data returned

3. **Logout:**
   ```bash
   curl -X POST http://localhost:3000/api/auth/sign-out \
     -b cookies.txt \
     -c cookies.txt
   ```

4. **Verify session cleared:**
   ```bash
   curl -X GET http://localhost:3000/api/auth/session \
     -b cookies.txt
   ```
   Expected: `null`

---

## Part 5: Common Issues and Troubleshooting

### Issue 1: "JWT_SECRET environment variable is required"

**Cause:** `.env` file missing or JWT_SECRET not set

**Fix:**
```bash
# Check if .env file exists
ls -la .env .env.local

# Verify JWT_SECRET is set
cat .env | grep JWT_SECRET

# If missing, add to .env:
echo "JWT_SECRET=<your-secret-here>" >> .env
```

### Issue 2: "CORS error: Access-Control-Allow-Origin"

**Cause:** Frontend URL not in backend CORS allowed origins

**Fix:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Make sure this matches frontend URL
    ],
    allow_credentials=True,  # Required for cookies
    # ...
)
```

### Issue 3: "Database connection error"

**Cause:** Incorrect DATABASE_URL or PostgreSQL not running

**Fix:**
```bash
# Test database connection
psql <DATABASE_URL>

# Start PostgreSQL (if local)
brew services start postgresql  # macOS
sudo service postgresql start   # Linux

# Verify DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database
```

### Issue 4: "Invalid token" error on backend

**Cause:** JWT_SECRET mismatch between frontend and backend

**Fix:**
```bash
# Compare secrets
echo "Frontend:"
cat frontend/.env.local | grep JWT_SECRET

echo "Backend:"
cat backend/.env | grep JWT_SECRET

# They MUST be identical
# If different, copy frontend secret to backend .env
```

### Issue 5: "Token has expired" immediately after login

**Cause:** System clock skew or `exp` claim too short

**Fix:**
```bash
# Check system time
date

# Sync system time (macOS)
sudo sntp -sS time.apple.com

# Sync system time (Linux)
sudo ntpdate pool.ntp.org

# Verify JWT expiration in auth.ts is 24 hours
# jwt: { expiresIn: 60 * 60 * 24 }
```

---

## Part 6: Next Steps

After completing this quickstart:

1. ✅ **Frontend Auth Working:** Users can register, log in, log out
2. ✅ **Backend JWT Validation Working:** Backend can validate tokens
3. ✅ **Database Setup Complete:** Two separate PostgreSQL databases

**What's Next:**

1. **Create UI Components:**
   - Login page (`frontend/app/login/page.tsx`)
   - Registration page (`frontend/app/register/page.tsx`)
   - Logout button (`frontend/components/auth/LogoutButton.tsx`)

2. **Add Protected Routes:**
   - Middleware (`frontend/middleware.ts`)
   - Dashboard page (`frontend/app/page.tsx`)

3. **Write Tests:**
   - Frontend unit tests (Vitest)
   - Backend JWT validation tests (Pytest)
   - E2E tests (Playwright)

4. **Implement Task CRUD:**
   - Task API routes using `get_current_user` dependency
   - Task UI components

**Run /sp.tasks to generate implementation tasks.md**

---

## Quick Reference

### Frontend Commands

```bash
cd frontend

# Start dev server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

### Backend Commands

```bash
cd backend

# Start dev server
uvicorn backend.main:app --reload --port 8000

# Run tests
pytest

# Create database tables
python -m backend.create_db
```

### Database Commands

```bash
# Connect to frontend database
psql frontend_auth

# Connect to backend database
psql backend_tasks

# List tables
\dt

# Describe table
\d table_name

# Query users
SELECT * FROM "user";

# Query tasks
SELECT * FROM tasks;
```

---

## Summary

**You've successfully set up:**

✅ Frontend with Better Auth (user management, JWT tokens)
✅ Backend with JWT validation (stateless authentication)
✅ Two PostgreSQL databases (frontend auth + backend tasks)
✅ CORS configuration (frontend can call backend)
✅ JWT secret sharing (frontend and backend use same secret)
✅ Database tables (Better Auth tables + tasks table)
✅ Development environment (both servers running)

**Total Setup Time:** ~30-45 minutes

**Ready for implementation!** Proceed to `/sp.tasks` to generate TDD implementation tasks.

---

**Questions or Issues?**

- Check [Troubleshooting Section](#part-5-common-issues-and-troubleshooting)
- Review [Better Auth Docs](https://www.better-auth.com/docs/nextjs)
- Review [FastAPI Docs](https://fastapi.tiangolo.com/)
- Check [JWT Contract](./contracts/jwt-validation.md)
- Check [Better Auth Contract](./contracts/better-auth-flow.md)

