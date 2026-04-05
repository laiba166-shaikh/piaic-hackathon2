# Backend - Phase 2 Todo App

FastAPI backend with JWT authentication and PostgreSQL database.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM (SQLAlchemy + Pydantic)
- **PostgreSQL** - Database (via Neon serverless)
- **Alembic** - Database migrations
- **PyJWT** - JWT token validation (EdDSA via JWKS)
- **Ruff** - Linting and formatting
- **uv** - Fast Python package installer

## Project Structure

```
src/core/backend/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration (Pydantic Settings)
├── db.py                   # Database connection
├── dependencies.py         # Shared dependencies (JWT validation via JWKS)
├── models/                 # SQLModel database models
├── api/                    # API route handlers
│   └── v1/                 # API version 1
├── migrations/             # Alembic migrations
└── tests/                  # Test files
```

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- PostgreSQL database (Neon recommended)

### Installation

1. **Create and activate a virtual environment:**

```bash
cd src/core/backend
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate

# macOS/Linux
source .venv/bin/activate
```

2. **Install dependencies:**

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

3. **Configure environment variables:**

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
# .env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
FRONTEND_URL=http://localhost:3000
DEBUG=True
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `FRONTEND_URL` | No | Frontend base URL — backend fetches JWKS public keys from here to verify JWT tokens (default: `http://localhost:3000`) |
| `DEBUG` | No | Enable debug logging (default: `False`) |

> **Note:** There is no `JWT_SECRET` in the backend. JWT tokens are verified using the public key fetched from the frontend's JWKS endpoint (`/api/auth/jwks`). The secret lives only in the frontend (`BETTER_AUTH_SECRET`).

4. **Run database migrations:**

```bash
# Must be run from inside src/core/backend/
alembic upgrade head
```

## Development

### Run the development server

**Must be run from inside `src/core/backend/`** so that Python resolves local imports correctly:

```bash
cd src/core/backend
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Run tests

```bash
cd src/core/backend
pytest
```

### Lint and format

```bash
ruff check .
ruff format .
```

## Deployment

### How imports work

The backend uses **flat local imports** (e.g. `from config import settings`). These work when:
- The working directory is `src/core/backend/`, **or**
- `PYTHONPATH` includes `src/core/backend/`

### Option A — Set root directory to `src/core/backend/` (simplest)

On Railway, Render, or similar platforms, set the **root directory** to `src/core/backend/` in the service settings. The platform then installs from `requirements.txt` and runs uvicorn from that folder — identical to local dev.

Start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Option B — Deploy from repo root using `Procfile`

A `Procfile` at the repo root sets `PYTHONPATH` automatically:

```
# Procfile (repo root)
web: PYTHONPATH=src/core/backend uvicorn src.core.backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

This is already committed at the repo root. No extra configuration needed for platforms that read `Procfile` (Heroku, Railway, Render).

### Environment variables in production

Set these in your deployment platform's environment settings:

```bash
DATABASE_URL=postgresql://...      # Neon connection string
FRONTEND_URL=https://your-app.com  # Your deployed frontend URL
DEBUG=False
```

## API Endpoints

### Health Check
- `GET /` - Root
- `GET /health` - Server health status

### Tasks (requires JWT)
- `GET /api/v1/tasks` - List all user tasks
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task (soft delete)

## Authentication

The backend validates JWT tokens issued by Better Auth (frontend) using **EdDSA asymmetric verification**:

1. Request arrives with `Authorization: Bearer <token>`
2. Backend fetches JWKS public keys from `FRONTEND_URL/api/auth/jwks` (cached 1 hour)
3. Token signature is verified using the matching Ed25519 public key
4. `user_id` is extracted from the `sub` claim

All `/api/v1/*` endpoints require:
```
Authorization: Bearer <jwt-token>
```

## Database

### Models

**Task:**
| Field | Type | Description |
|---|---|---|
| `id` | int | Primary key |
| `user_id` | str | User identifier (from JWT `sub` claim) |
| `title` | str | Task title (max 200 chars) |
| `description` | str? | Optional description |
| `completed` | bool | Completion status |
| `deleted_at` | datetime? | Soft delete timestamp |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Security Features

- JWT token validation via EdDSA/JWKS (no shared secret)
- User isolation (all queries filtered by `user_id`)
- Soft deletes (data preservation)
- SQL injection prevention (parameterized queries via SQLModel)
- CORS configured for frontend origin only
- Input validation via Pydantic schemas

## Key Principles

1. **User Isolation:** All database queries MUST filter by `user_id` from JWT
2. **Soft Deletes:** Use `deleted_at` timestamp, never hard delete
3. **No user_id in URLs:** User ID extracted from JWT token only
4. **404 for unauthorized:** Return 404 (not 403) to prevent user enumeration

## Troubleshooting

### Import errors on startup
Make sure you are running uvicorn from inside `src/core/backend/`:
```bash
cd src/core/backend
uvicorn main:app --reload --port 8000
```

### `DATABASE_URL` missing error
Ensure `.env` exists in `src/core/backend/` and contains `DATABASE_URL`. Copy from `.env.example`.

### JWT validation errors
- Confirm the frontend is running and accessible at `FRONTEND_URL`
- The backend fetches JWKS from `FRONTEND_URL/api/auth/jwks` — if the frontend is down, token verification fails
- Check that `BETTER_AUTH_SECRET` is set in the frontend `.env.local`

### Database connection issues
- Verify `DATABASE_URL` is correct
- Neon requires `sslmode=require` in the connection string
- Check if your IP is allowed in Neon's connection settings

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [Better Auth JWKS](https://www.better-auth.com/docs/plugins/jwt)
