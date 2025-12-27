# Backend - Phase 2 Todo App

FastAPI backend with JWT authentication and PostgreSQL database.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM (SQLAlchemy + Pydantic)
- **PostgreSQL** - Database (via Neon serverless)
- **Alembic** - Database migrations
- **PyJWT** - JWT token validation
- **Ruff** - Linting and formatting
- **uv** - Fast Python package installer

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration (Pydantic Settings)
├── db.py                   # Database connection
├── dependencies.py         # Shared dependencies (JWT validation)
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

1. **Install uv (if not already installed):**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Install dependencies:**

```bash
cd backend

# Using uv (recommended - faster)
uv pip install -e .

# Or using regular pip
pip install -r requirements.txt
```

3. **Configure environment variables:**

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Authentication
JWT_SECRET=your-secret-key-here
```

4. **Run database migrations:**

```bash
alembic upgrade head
```

## Development

### Run the development server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Run tests:

```bash
pytest
```

### Run linter:

```bash
ruff check .
```

### Format code:

```bash
ruff format .
```

## API Endpoints

### Health Check
- `GET /health` - Server health status

### Tasks (requires authentication)
- `GET /api/v1/tasks` - List all user tasks
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task (soft delete)
- `PATCH /api/v1/tasks/{id}/toggle` - Toggle task completion

## Authentication

The backend validates JWT tokens issued by Better Auth (frontend).

### JWT Structure:
- **Algorithm:** HS256
- **Secret:** Shared with frontend (JWT_SECRET)
- **User ID:** Extracted from `sub` claim

### Protected Endpoints:
All `/api/v1/*` endpoints require:
```
Authorization: Bearer <jwt-token>
```

## Database

### Models

**Task:**
- `id` - Primary key
- `user_id` - User identifier (from JWT)
- `title` - Task title (max 200 chars)
- `description` - Task description (optional)
- `completed` - Completion status
- `deleted_at` - Soft delete timestamp
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Security Features

- ✅ JWT token validation on all protected endpoints
- ✅ User isolation (queries filtered by user_id)
- ✅ Soft deletes (data preservation)
- ✅ SQL injection prevention (parameterized queries)
- ✅ CORS configured for frontend origin
- ✅ Input validation via Pydantic schemas

## Key Principles

1. **User Isolation:** All database queries MUST filter by `user_id` from JWT
2. **Soft Deletes:** Use `deleted_at` timestamp, never hard delete
3. **No user_id in URLs:** User ID extracted from JWT token only
4. **404 for unauthorized:** Return 404 (not 403) to prevent user enumeration

## Testing

Tests use pytest with test database fixtures.

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_tasks.py
```

## Configuration

Environment variables are managed via `config.py` using Pydantic Settings:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Shared secret for JWT validation
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `DEBUG` - Debug mode (default: False)

## Why uv?

**uv** is a blazingly fast Python package installer and resolver:
- 10-100x faster than pip
- Compatible with pip and requirements.txt
- Built in Rust for maximum performance
- Works seamlessly with existing Python tooling

## Troubleshooting

### Database connection issues:
- Verify DATABASE_URL is correct
- Check if database allows connections from your IP
- Ensure SSL mode is set correctly

### JWT validation errors:
- Verify JWT_SECRET matches frontend configuration
- Check token expiration
- Ensure token includes 'sub' claim with user_id

### Migration errors:
- Check database connectivity
- Verify Alembic is properly configured
- Review migration files for conflicts

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [PyJWT Documentation](https://pyjwt.readthedocs.io)
- [uv Documentation](https://github.com/astral-sh/uv)

## Contributing

See main project [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

Part of Phase 2 Todo App project.
