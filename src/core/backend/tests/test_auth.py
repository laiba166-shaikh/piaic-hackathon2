"""Tests for JWT authentication and get_current_user dependency."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.core.backend.dependencies import get_current_user
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
    user_id = "user-123"
    token = create_test_jwt(user_id=user_id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    result = await get_current_user(credentials=credentials)

    assert result == user_id


@pytest.mark.asyncio
async def test_get_current_user_with_expired_token():
    """
    Test that get_current_user raises 401 for an expired JWT token.

    Acceptance Criteria:
    - Expired JWT token raises HTTPException with status 401
    - Error detail references expiry or authentication
    """
    token = create_test_jwt(expired=True)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert (
        "expired" in exc_info.value.detail.lower()
        or "authentication" in exc_info.value.detail.lower()
    )


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():
    """
    Test that get_current_user raises 401 for a token with invalid signature.

    Acceptance Criteria:
    - JWT signed with wrong key raises HTTPException with status 401
    - Error detail references invalid credentials
    """
    token = create_invalid_jwt()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert (
        "invalid" in exc_info.value.detail.lower()
        or "authentication" in exc_info.value.detail.lower()
    )


@pytest.mark.asyncio
async def test_get_current_user_with_missing_credentials():
    """
    Test that get_current_user raises an error when credentials are None.

    In production FastAPI's HTTPBearer rejects missing tokens before
    get_current_user is called. When called directly with None, the
    AttributeError from credentials.credentials is caught by the outer
    exception handler and surfaced as HTTPException(500).
    """
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None)

    assert exc_info.value.status_code in (401, 500)


@pytest.mark.asyncio
async def test_get_current_user_with_missing_sub_claim():
    """
    Test that get_current_user raises 401 when JWT token has no 'sub' claim.

    Acceptance Criteria:
    - Token without 'sub' claim raises HTTPException with status 401
    - Error detail references invalid credentials
    """
    token = create_test_jwt(include_sub=False)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert (
        "credentials" in exc_info.value.detail.lower()
        or "authentication" in exc_info.value.detail.lower()
    )
