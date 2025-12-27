"""Tests for JWT authentication and get_current_user dependency."""

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dependencies import get_current_user
from tests.fixtures.jwt_tokens import create_invalid_jwt, create_test_jwt


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token():
    """
    Test that get_current_user successfully extracts user_id from a valid JWT token.

    Acceptance Criteria:
    - Valid JWT token with 'sub' claim returns user_id
    - No exception is raised
    - Returned user_id matches the 'sub' claim in the token
    """
    # Arrange: Create a valid JWT token
    user_id = "user-123"
    token = create_test_jwt(user_id=user_id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    # Act: Call get_current_user with valid token
    result = await get_current_user(credentials=credentials)

    # Assert: user_id is extracted correctly
    assert result == user_id


@pytest.mark.asyncio
async def test_get_current_user_with_expired_token():
    """
    Test that get_current_user raises 401 error for expired JWT token.

    Acceptance Criteria:
    - Expired JWT token raises HTTPException
    - Status code is 401 Unauthorized
    - Error detail contains meaningful message
    """
    # Arrange: Create an expired JWT token
    token = create_test_jwt(expired=True)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    # Act & Assert: Expired token raises 401 error
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert (
        "authentication" in exc_info.value.detail.lower()
        or "expired" in exc_info.value.detail.lower()
    )


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():
    """
    Test that get_current_user raises 401 error for token with invalid signature.

    Acceptance Criteria:
    - JWT token with wrong signature raises HTTPException
    - Status code is 401 Unauthorized
    - Error detail contains meaningful message
    """
    # Arrange: Create a JWT token with invalid signature
    token = create_invalid_jwt()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    # Act & Assert: Invalid token raises 401 error
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert (
        "authentication" in exc_info.value.detail.lower()
        or "invalid" in exc_info.value.detail.lower()
    )


@pytest.mark.asyncio
async def test_get_current_user_with_missing_token():
    """
    Test that get_current_user raises error when credentials are None.

    Acceptance Criteria:
    - Missing/None credentials raises an error
    - This tests the security dependency behavior

    Note: FastAPI's HTTPBearer dependency will handle missing tokens before
    get_current_user is called, but we test the function behavior.
    """
    # Arrange: No credentials provided
    credentials = None

    # Act & Assert: Missing token should raise error
    # Since HTTPBearer requires credentials, we expect TypeError or AttributeError
    with pytest.raises((TypeError, AttributeError)):
        await get_current_user(credentials=credentials)


@pytest.mark.asyncio
async def test_get_current_user_with_missing_sub_claim():
    """
    Test that get_current_user raises 401 error when JWT token is missing 'sub' claim.

    Acceptance Criteria:
    - JWT token without 'sub' claim raises HTTPException
    - Status code is 401 Unauthorized
    - Error detail indicates invalid credentials
    """
    # Arrange: Create a JWT token without 'sub' claim
    token = create_test_jwt(include_sub=False)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    # Act & Assert: Token without 'sub' claim raises 401 error
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert (
        "authentication" in exc_info.value.detail.lower()
        or "credentials" in exc_info.value.detail.lower()
    )
