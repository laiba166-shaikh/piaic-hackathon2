# Frontend - Phase 2 Todo App

Next.js frontend with Better Auth authentication and a journal-themed UI.

## Tech Stack

- **Next.js 16+ (App Router)** - React framework with server components
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Better Auth** - Authentication (email/password + JWT plugin)
- **PostgreSQL** - Better Auth stores user/session tables here (via Neon)

## Project Structure

```
src/core/frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── login/              # Login page
│   ├── register/           # Registration page
│   └── tasks/              # Task pages
├── components/             # Reusable UI components
│   ├── auth/               # Authentication components
│   ├── tasks/              # Task-related components
│   └── ui/                 # Generic UI (Button, Input, Modal)
├── lib/
│   ├── auth.ts             # Better Auth server configuration
│   └── api.ts              # Centralized backend API client
├── hooks/                  # Custom React hooks
├── types/                  # TypeScript type definitions
└── __tests__/              # Unit and E2E tests
```

## Setup

### Prerequisites

- Node.js 18+
- npm or pnpm
- Neon PostgreSQL database (shared with backend)

### Installation

1. **Install dependencies:**

```bash
cd src/core/frontend
npm install
```

2. **Configure environment variables:**

```bash
cp .env.example .env.local
```

Edit `.env.local` and fill in your values:

```bash
# .env.local
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=<generate-with-openssl-rand-base64-32>
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string — Better Auth stores user and session tables here (same DB as backend) |
| `BETTER_AUTH_SECRET` | Yes | Secret key for signing Better Auth sessions and JWT tokens. Generate with: `openssl rand -base64 32` |
| `BETTER_AUTH_URL` | No | Base URL of this Next.js app, used by Better Auth for callbacks (default: `http://localhost:3000`) |
| `NEXT_PUBLIC_API_URL` | No | FastAPI backend URL, exposed to the browser (default: `http://localhost:8000`) |

> **Tip:** `DATABASE_URL` is used by **both** services — the frontend manages auth tables (users, sessions) and the backend manages the tasks table, all in the same Neon database.

> **Tip:** Generate `BETTER_AUTH_SECRET`:
> ```bash
> openssl rand -base64 32
> # or with Python:
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

## Development

### Run the development server

```bash
cd src/core/frontend
npm run dev
```

App available at http://localhost:3000

### Other commands

```bash
npm run build        # Production build
npm run lint         # ESLint
npm run format       # Prettier
npm run test         # Unit tests (Vitest)
npm run test:e2e     # E2E tests (Playwright)
```

## Deployment

### Environment variables in production

Set these in your deployment platform (Vercel, Railway, Render, etc.):

```bash
DATABASE_URL=postgresql://...           # Neon connection string
BETTER_AUTH_SECRET=<your-secret>        # Same secret used in local dev
BETTER_AUTH_URL=https://your-app.com    # Your deployed frontend URL
NEXT_PUBLIC_API_URL=https://your-api.com  # Your deployed backend URL
```

### Vercel

This is a Next.js app and deploys to Vercel with zero configuration:
- Set root directory to `src/core/frontend`
- Add the environment variables above in the Vercel dashboard

### Other platforms (Railway, Render)

- Set **root directory** to `src/core/frontend`
- Start command: `npm run start`
- Build command: `npm run build`
- Add environment variables in the platform dashboard

## Authentication Flow

Better Auth handles all authentication via `/api/auth/*` routes:

1. User signs up or logs in via the frontend form
2. Better Auth creates a session and stores it in PostgreSQL
3. Better Auth's JWT plugin issues an EdDSA-signed JWT token
4. The JWT is stored in an HTTP-only cookie
5. The backend verifies incoming JWTs using the public key from `/api/auth/jwks`

**Public routes:** `/login`, `/register`
**Protected routes:** `/`, `/tasks/*` (middleware redirects unauthenticated users to `/login`)

## Troubleshooting

### `DATABASE_URL environment variable is required` error
`.env.local` is missing or not in the right location. It must be at `src/core/frontend/.env.local`.

### `BETTER_AUTH_SECRET environment variable is required` error
Add `BETTER_AUTH_SECRET` to `.env.local`. Generate one with `openssl rand -base64 32`.

### Signup/login returns 500
Check that `DATABASE_URL` points to a valid Neon PostgreSQL instance and the Better Auth tables exist. Better Auth auto-creates its tables on first run.

### Backend API calls fail (CORS or network error)
- Confirm the FastAPI backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` matches the backend URL
- Verify CORS is configured in the backend to allow `http://localhost:3000`

## Additional Resources

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [Better Auth Docs](https://www.better-auth.com/docs)
- [Better Auth JWT Plugin](https://www.better-auth.com/docs/plugins/jwt)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
