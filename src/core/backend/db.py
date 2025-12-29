"""Database connection and session management."""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from src.core.backend.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.DEBUG else False,
    connect_args={"sslmode": "require"}
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for database sessions.

    Usage:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
