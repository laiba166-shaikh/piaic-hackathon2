"""FastAPI dependencies for authentication and database access."""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlmodel import Session

from src.core.backend.config import settings
from src.core.backend.db import get_session

# Configure logger
logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate JWT token, return user_id.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        str: The user_id from the JWT token's 'sub' claim

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            logger.warning("JWT validation failed: missing 'sub' claim in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        logger.info(f"JWT validation successful for user_id: {user_id}")
        return user_id

    except ExpiredSignatureError:
        logger.warning("JWT validation failed: token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    except JWTError as e:
        logger.warning(
            f"JWT validation failed: {type(e).__name__} - "
            "Invalid token signature or format"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def get_db() -> Session:
    """
    Database session dependency.

    Usage:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_db)):
            ...

    Yields:
        Session: SQLModel database session
    """
    return get_session()
