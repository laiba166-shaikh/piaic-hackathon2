# Environment Setup Guide

This monorepo contains separate backend (FastAPI) and frontend (Next.js) applications, each with its own environment configuration.

## Quick Setup

### 1. Backend Environment

```bash
cd src/core/backend
cp .env.example .env
# Edit .env and fill in your values
```

**Required Variables:**
- `DATABASE_URL` - Your backend Neon PostgreSQL connection string (for tasks)
- `JWT_SECRET` - Secret key for JWT tokens (must match frontend)
- `DEBUG` - Set to `True` for development

### 2. Frontend Environment

```bash
cd src/core/frontend  
cp .env.example .env.local
# Edit .env.local and fill in your values
```

**Required Variables:**
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `BETTER_AUTH_SECRET` - Better Auth secret key
- `BETTER_AUTH_URL` - Frontend URL (default: http://localhost:3000)
- `DATABASE_URL` - Better Auth Neon PostgreSQL connection string (for users)

## Important Notes

### Shared JWT Secret
The `JWT_SECRET` in backend must **match** the secret used by Better Auth in frontend. Better Auth generates JWT tokens that the backend validates.

### Separate Databases
- **Backend Database**: Stores application data (tasks, etc.)
- **Frontend Database**: Better Auth stores user data (users, sessions, accounts)

These should be **different** databases (can be in same Neon project, different branches).

### Security
- ✅ Never commit `.env` files to version control
- ✅ Use strong random secrets in production
- ✅ Generate secrets with: `openssl rand -base64 32`
- ❌ Don't share secrets between environments

## File Structure

```
project-root/
├── .env.example                    # Root template (reference only)
├── src/core/backend/
│   ├── .env                        # ⚠️ Git ignored - your actual backend config
│   └── .env.example                # Template for backend
└── src/core/frontend/
    ├── .env                        # ⚠️ Git ignored - Better Auth CLI uses this
    ├── .env.local                  # ⚠️ Git ignored - Next.js uses this
    └── .env.example                # Template for frontend

```

## Running the Applications

### Backend
```bash
cd src/core/backend
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd src/core/frontend
npm run dev
```

## Troubleshooting

**Backend won't start:**
- Check DATABASE_URL is valid
- Ensure JWT_SECRET is set
- Verify all dependencies installed: `pip install -r requirements.txt`

**Frontend authentication fails:**
- Verify DATABASE_URL points to Better Auth database
- Check BETTER_AUTH_SECRET is set
- Ensure migrations ran: `cd src/core/frontend && npx @better-auth/cli migrate`

**JWT validation errors:**
- Ensure JWT_SECRET matches between backend and Better Auth
- Check token hasn't expired (24 hour default)
