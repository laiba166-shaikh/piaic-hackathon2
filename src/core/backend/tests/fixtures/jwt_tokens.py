"""JWT token generation utilities for testing."""

from datetime import datetime, timedelta

from jose import jwt

from config import settings


def create_test_jwt(
    user_id: str = "test-user-123",
    expired: bool = False,
    include_sub: bool = True
) -> str:
    """
    Generate a test JWT token.

    Args:
        user_id: The user ID to include in the 'sub' claim
        expired: Whether to create an expired token
        include_sub: Whether to include the 'sub' claim

    Returns:
        str: Encoded JWT token
    """
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=-1 if expired else 24),
        "iat": datetime.utcnow(),
    }

    if include_sub:
        payload["sub"] = user_id

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_invalid_jwt() -> str:
    """
    Generate JWT with wrong secret (invalid signature).

    Returns:
        str: JWT token with invalid signature
    """
    payload = {
        "sub": "test-user-123",
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
