# TASKMATE

A full-stack task management application built across 5 progressive phases — from a CLI tool to a cloud-deployed, AI-powered web app.

**Current phase: Phase 2 — Full-Stack Web Application**

---

## What is TASKMATE?

TASKMATE lets users create, manage, and track tasks with a clean journal-themed interface. Each user's tasks are private and isolated. Authentication is handled via email/password with JWT tokens.

The project is structured as a **monorepo with independently runnable phases** — the CLI from Phase 1 still works alongside the Phase 2 web app.

---

## Tech Stack (Phase 2)

| Layer | Technology |
|---|---|
| Frontend | Next.js 16+ (App Router), TypeScript, Tailwind CSS |
| Auth | Better Auth (email/password + EdDSA JWT plugin) |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL via [Neon](https://neon.tech) (serverless) |
| ORM | SQLModel + Alembic migrations |
| CLI (Phase 1) | Click, Rich |

---

## Project Structure

```
hackathon2/
├── src/
│   ├── cli/                    # Phase 1 — CLI application (Click + Rich)
│   └── core/
│       ├── backend/            # Phase 2 — FastAPI REST API
│       └── frontend/           # Phase 2 — Next.js web app
├── specs/                      # Spec-Driven Development artifacts
├── history/                    # Prompt History Records + ADRs
├── Procfile                    # Deployment start command (repo root)
├── ARCHITECTURE.md             # Full multi-phase architecture
└── ENV_SETUP.md                # Environment variables quick reference
```

---

## Quick Start (Phase 2)

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Neon](https://neon.tech) PostgreSQL database

---

### 1. Backend

```bash
cd src/core/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env — fill in DATABASE_URL and FRONTEND_URL
```

**.env (backend):**
```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
FRONTEND_URL=http://localhost:3000
DEBUG=True
```

```bash
# Run database migrations
alembic upgrade head

# Start the API server (must run from inside src/core/backend/)
uvicorn main:app --reload --port 8000
```

API available at → http://localhost:8000  
Swagger docs → http://localhost:8000/docs

> See [`src/core/backend/README.md`](src/core/backend/README.md) for full backend setup.

---

### 2. Frontend

```bash
cd src/core/frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local — fill in all variables
```

**.env.local (frontend):**
```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=<run: openssl rand -base64 32>
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
# Start the dev server
npm run dev
```

App available at → http://localhost:3000

> See [`src/core/frontend/README.md`](src/core/frontend/README.md) for full frontend setup.

---

### Environment Variables — Key Points

| Variable | Where | Description |
|---|---|---|
| `DATABASE_URL` | Backend `.env` + Frontend `.env.local` | **Same Neon database** — backend stores tasks, frontend (Better Auth) stores users/sessions |
| `BETTER_AUTH_SECRET` | Frontend `.env.local` only | Signs JWT tokens — generate with `openssl rand -base64 32` |
| `FRONTEND_URL` | Backend `.env` | Backend fetches JWKS public keys from `FRONTEND_URL/api/auth/jwks` to verify tokens — no shared secret needed |
| `NEXT_PUBLIC_API_URL` | Frontend `.env.local` | FastAPI backend URL, exposed to browser |

> There is **no `JWT_SECRET` in the backend**. Token verification uses EdDSA asymmetric keys — the backend fetches the public key from the frontend's JWKS endpoint.

> Full environment guide → [`ENV_SETUP.md`](ENV_SETUP.md)

---

## Authentication Flow

```
User → Frontend (Better Auth) → Issues EdDSA JWT → Stored in HTTP-only cookie
                                                          ↓
                                       Backend receives JWT in Authorization header
                                                          ↓
                              Backend fetches public key from /api/auth/jwks
                                                          ↓
                                        Token verified → user_id extracted
```

---

## Deployment

### Backend

The backend uses **flat local imports** that require `src/core/backend/` to be on Python's path.

**Option A — Set root directory to `src/core/backend/`** (Railway, Render dashboard setting):
```bash
# Start command
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Option B — Deploy from repo root** (uses the committed `Procfile`):
```
web: PYTHONPATH=src/core/backend uvicorn src.core.backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Production environment variables for backend:
```bash
DATABASE_URL=postgresql://...
FRONTEND_URL=https://your-frontend.com
DEBUG=False
```

### Frontend

Deploy to **Vercel** (recommended for Next.js):
- Set root directory to `src/core/frontend`
- Add all `.env.local` variables in the Vercel dashboard

Or deploy to Railway/Render:
- Set root directory to `src/core/frontend`
- Build command: `npm run build`
- Start command: `npm run start`

Production environment variables for frontend:
```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=<your-secret>
BETTER_AUTH_URL=https://your-frontend.com
NEXT_PUBLIC_API_URL=https://your-backend.com
```

---

## Phase 1 — CLI (still works)

```bash
cd hackathon2
pip install -e src/cli
python -m src.cli.main           # interactive mode
python -m src.cli.main --help    # one-shot commands
```

The CLI runs completely independently — no backend or database required (uses in-memory storage).

---

## Running Everything Together (Phase 2)

Open 2 terminals:

```bash
# Terminal 1 — Backend
cd src/core/backend
source .venv/Scripts/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd src/core/frontend
npm run dev
```

---

## Further Reading

| Document | Description |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Full multi-phase architecture, phase evolution strategy, storage abstraction, and all entry points |
| [`src/core/backend/README.md`](src/core/backend/README.md) | Backend setup, API endpoints, JWT verification, deployment options, troubleshooting |
| [`src/core/frontend/README.md`](src/core/frontend/README.md) | Frontend setup, Better Auth config, environment variables, deployment |
| [`ENV_SETUP.md`](ENV_SETUP.md) | Quick environment variables reference for both services |

---

## Phases Roadmap

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Complete | CLI with in-memory storage (Click + Rich) |
| Phase 2 | ✅ Complete | Full-stack web app (FastAPI + Next.js + PostgreSQL) |
| Phase 3 | Planned | AI Chatbot with MCP server (OpenAI Agents SDK) |
| Phase 4 | Planned | Local Kubernetes deployment (Docker + Helm + Minikube) |
| Phase 5 | Planned | Cloud deployment (Kafka, Dapr, DigitalOcean/GKE) |
