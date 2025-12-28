# API Contract: Backend JWT Validation Dependency

**Feature:** User Authentication
**Component:** Backend JWT Validation
**Date:** 2025-12-21
**Status:** Contract Approved
**Type:** Internal Dependency (FastAPI Depends)

## Summary

This contract defines the `get_current_user()` dependency function that validates JWT tokens and extracts the authenticated user's ID from the 'sub' claim. This dependency is used by ALL protected backend endpoints to enforce user authentication and isolation. It accepts JWT tokens from either the Authorization header or HTTP-only cookies, validates the signature and expiration, and returns the user_id for use in database queries.

---

## Function Signature

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> str:
    """
    Validate JWT token and extract user_id from 'sub' claim.

    Args:
        credentials: JWT token from Authorization header (Bearer format)

    Returns:
        str: User ID from JWT 'sub' claim

    Raises:
        HTTPException: 401 Unauthorized for invalid, expired, or missing tokens
    """
```

**Location:** `src/core/backend/dependencies.py`
**Import:** `from src.core.backend.dependencies import get_current_user`

---

## Input Specification

### **MANDATED INPUT METHOD: Authorization Header**

**Header Name:** `Authorization`
**Format:** `Bearer <JWT_TOKEN>`

**Example:**
```http
GET /api/v1/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImV4cCI6MTczNDc5MjAwMH0.signature
```

**Frontend Responsibility:**
- Extract JWT from localStorage: `const token = localStorage.getItem('jwt_token')`
- Include in every backend API request:
  ```typescript
  fetch('/api/v1/tasks', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  ```

**Backend Implementation:**
```python
# dependencies.py
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract user_id from Authorization header JWT token."""
    token = credentials.credentials  # From "Bearer <token>"
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(401, detail="Invalid token: missing user_id")
    return user_id
```

**Validation:**
- Header MUST start with "Bearer " (case-sensitive)
- Token MUST be a valid JWT string (three base64-encoded parts separated by dots)
- If header is present but malformed, return 401 Unauthorized
- If header is missing, return 401 Unauthorized (no fallback)

**Cookie Fallback: REMOVED**

**Rationale:**
- Better Auth JWT plugin **does NOT set JWT in HTTP-only cookie**
- JWT must be **manually retrieved** via `authClient.token()`
- Frontend stores JWT in localStorage
- Backend **only** checks Authorization header

**Migration from Spec v1.0:**
- ~~Input Method 2: HTTP-Only Cookie~~ **DEPRECATED**
- Only Authorization header supported
- Simplifies implementation (one method, not two)

---

## JWT Token Structure

### JWT Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Requirements:**
- Algorithm MUST be "HS256" (HMAC SHA-256)
- Type MUST be "JWT"

### JWT Payload (Claims)

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "iat": 1734705600,
  "exp": 1734792000
}
```

**Required Claims:**
- **sub** (Subject): User ID (UUID string) - REQUIRED
- **exp** (Expiration): Unix timestamp - REQUIRED
- **iat** (Issued At): Unix timestamp - OPTIONAL

**Optional Claims:**
- **iss** (Issuer): "better-auth" (not validated by backend)
- **aud** (Audience): "task-api" (not validated in Phase 2)

**Validation Rules:**
- `sub` claim MUST be present and non-empty string
- `exp` claim MUST be present and in the future (UTC)
- If `sub` is missing or null, return 401 "Invalid token: missing user_id"
- If `exp` is in the past, return 401 "Token has expired"

### JWT Signature

**Algorithm:** HS256 (HMAC SHA-256)
**Secret Key:** Shared between frontend (issues tokens) and backend (validates tokens)
**Environment Variable:** `JWT_SECRET`

**Validation:**
- Backend MUST validate signature using `JWT_SECRET`
- If signature is invalid, return 401 "Invalid token"
- If token is malformed (not 3 parts), return 401 "Invalid token"

---

## Output Specification

### Success Response

**Type:** `str` (Python string)
**Value:** User ID extracted from JWT 'sub' claim
**Format:** UUID string (e.g., "550e8400-e29b-41d4-a716-446655440000")

**Example:**
```python
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),  # Returns "550e8400-..."
    session: Session = Depends(get_db)
):
    # user_id is available as a string
    print(user_id)  # "550e8400-e29b-41d4-a716-446655440000"
    # ...
```

**Guarantees:**
- `user_id` is NEVER null or empty (function raises HTTPException if invalid)
- `user_id` is always a string (type-safe with Python type hints)
- `user_id` comes from a validated JWT token (signature and expiration checked)

---

## Error Responses

### Error 1: Missing Token

**Scenario:** No Authorization header and no auth-token cookie
**HTTP Status:** 401 Unauthorized
**Headers:** `WWW-Authenticate: Bearer`

**Response Body:**
```json
{
  "detail": "Authorization required"
}
```

**When Raised:**
- Both `credentials` and `auth_token` parameters are None
- Client did not provide any authentication

**Recovery:**
- Frontend should redirect user to /login
- Client should obtain a valid JWT token and retry request

---

### Error 2: Expired Token

**Scenario:** JWT token `exp` claim is in the past
**HTTP Status:** 401 Unauthorized
**Headers:** `WWW-Authenticate: Bearer`

**Response Body:**
```json
{
  "detail": "Token has expired"
}
```

**When Raised:**
- `jwt.decode()` raises `jwt.ExpiredSignatureError`
- Token was valid but has passed its expiration time

**Recovery:**
- Frontend should redirect user to /login with message "Your session has expired"
- User must re-authenticate to get a new token

---

### Error 3: Invalid Signature

**Scenario:** JWT signature verification fails
**HTTP Status:** 401 Unauthorized
**Headers:** `WWW-Authenticate: Bearer`

**Response Body:**
```json
{
  "detail": "Invalid token"
}
```

**When Raised:**
- Token was signed with wrong secret key (JWT_SECRET mismatch)
- Token was tampered with (payload modified after signing)
- Token is malformed (not 3 base64-encoded parts)

**Recovery:**
- Frontend should redirect user to /login
- Ops team should verify JWT_SECRET is same on frontend and backend

---

### Error 4: Missing 'sub' Claim

**Scenario:** JWT token does not contain 'sub' claim or 'sub' is null/empty
**HTTP Status:** 401 Unauthorized

**Response Body:**
```json
{
  "detail": "Invalid token: missing user_id"
}
```

**When Raised:**
- JWT payload does not have `sub` field: `{}`
- JWT payload has `sub: null` or `sub: ""`
- Malformed token issued by frontend (bug)

**Recovery:**
- Frontend should redirect user to /login
- Developer should investigate why JWT token lacks 'sub' claim

---

## Implementation Example

### Dependency Function (Backend)

```python
# src/core/backend/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from .config import settings

# HTTP Bearer security scheme (extracts Authorization header)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validate JWT token and extract user_id from 'sub' claim.

    Token must be provided in Authorization header: Bearer <token>

    Returns:
        user_id (str): User identifier from JWT 'sub' claim

    Raises:
        HTTPException 401: Invalid, expired, or missing token
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials  # From "Bearer <token>"

        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            settings.jwt_secret,  # Shared secret with frontend
            algorithms=[settings.jwt_algorithm]  # HS256
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        # Token exp claim is in the past
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        # Invalid signature, malformed token, or other JWT errors
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### Usage in Protected Route

```python
# src/core/backend/api/v1/tasks.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from src.core.backend.dependencies import get_current_user, get_db
from src.core.backend.models import Task

router = APIRouter(prefix="/api/v1", tags=["tasks"])

@router.get("/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),  # Automatically validates JWT
    session: Session = Depends(get_db)
):
    """
    Get all tasks for authenticated user.

    Requires valid JWT token in Authorization header or auth-token cookie.
    """
    # user_id is automatically available from JWT 'sub' claim
    # No need to validate - dependency already did that

    # Filter tasks by authenticated user (user isolation)
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()
    return tasks
```

---

## Configuration

### Environment Variables

**Required:**
- `JWT_SECRET`: Shared secret key for JWT validation (minimum 32 characters)
- `JWT_ALGORITHM`: "HS256" (default, can be omitted)

**Example `.env`:**
```bash
JWT_SECRET=your-super-secret-key-at-least-256-bits-long-random-string
JWT_ALGORITHM=HS256
```

### Settings Class

```python
# src/core/backend/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")

settings = Settings()
```

**Validation:**
- Application MUST NOT start if `JWT_SECRET` is missing
- Fail fast with clear error message: "JWT_SECRET environment variable is required"

---

## Testing Contract

### Test Cases

#### Test 1: Valid Token (Header)
**Input:**
```python
credentials = HTTPAuthorizationCredentials(
    scheme="Bearer",
    credentials=create_test_jwt(user_id="user-123")
)
```
**Expected Output:** `"user-123"`
**Assertion:** `assert user_id == "user-123"`

#### Test 2: Valid Token (Cookie)
**Input:**
```python
auth_token = create_test_jwt(user_id="user-456")
```
**Expected Output:** `"user-456"`
**Assertion:** `assert user_id == "user-456"`

#### Test 3: Expired Token
**Input:** Token with `exp` in the past
**Expected Error:** HTTPException 401 "Token has expired"
**Assertion:**
```python
with pytest.raises(HTTPException) as exc_info:
    await get_current_user(credentials=credentials)
assert exc_info.value.status_code == 401
assert "expired" in exc_info.value.detail.lower()
```

#### Test 4: Invalid Signature
**Input:** Token signed with wrong secret
**Expected Error:** HTTPException 401 "Invalid token"
**Assertion:**
```python
with pytest.raises(HTTPException) as exc_info:
    await get_current_user(credentials=credentials)
assert exc_info.value.status_code == 401
assert "invalid" in exc_info.value.detail.lower()
```

#### Test 5: Missing Token
**Input:** No credentials, no cookie
**Expected Error:** HTTPException 401 "Authorization required"
**Assertion:**
```python
with pytest.raises(HTTPException) as exc_info:
    await get_current_user(credentials=None, auth_token=None)
assert exc_info.value.status_code == 401
assert "required" in exc_info.value.detail.lower()
```

#### Test 6: Missing 'sub' Claim
**Input:** Token with `{ "exp": ... }` but no `sub`
**Expected Error:** HTTPException 401 "Invalid token: missing user_id"
**Assertion:**
```python
with pytest.raises(HTTPException) as exc_info:
    await get_current_user(credentials=credentials)
assert exc_info.value.status_code == 401
assert "missing user_id" in exc_info.value.detail.lower()
```

### Test Fixtures

```python
# src/core/backend/tests/fixtures/jwt_tokens.py
import jwt
from datetime import datetime, timedelta
from src.core.backend.config import settings

def create_test_jwt(
    user_id: str = "test-user-123",
    expired: bool = False,
    include_sub: bool = True
) -> str:
    """Generate a test JWT token for testing."""
    payload = {}

    if include_sub:
        payload["sub"] = user_id

    payload["exp"] = datetime.utcnow() + timedelta(hours=-1 if expired else 24)
    payload["iat"] = datetime.utcnow()

    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def create_invalid_jwt(user_id: str = "test-user-123") -> str:
    """Generate JWT with wrong secret (invalid signature)."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
```

---

## Security Considerations

### JWT Secret Management

**Critical:** JWT_SECRET must be kept secure and shared between frontend and backend.

**Best Practices:**
- Generate secret with high entropy (e.g., `openssl rand -base64 32`)
- Store in `.env` file (NEVER commit to git)
- Use environment variables in production (AWS Secrets Manager, Kubernetes Secrets)
- Rotate secret periodically (invalidates all tokens, requires re-authentication)

**Example Secret Generation:**
```bash
# Generate 256-bit random secret
openssl rand -base64 32
# Output: 8xVq9P2nL4mK7jH5gF3dS1aZ0wY9xC8vB7nM6kJ5hG4fE3dD2cB1a=
```

### Attack Scenarios

#### Scenario 1: Token Forgery
**Attack:** Attacker creates fake JWT token with arbitrary user_id
**Mitigation:** Signature validation fails (attacker doesn't have JWT_SECRET)
**Result:** 401 Unauthorized "Invalid token"

#### Scenario 2: Token Replay (After Expiration)
**Attack:** Attacker reuses captured token after expiration
**Mitigation:** Expiration check fails
**Result:** 401 Unauthorized "Token has expired"

#### Scenario 3: Token Tampering
**Attack:** Attacker modifies user_id in JWT payload
**Mitigation:** Signature validation fails (signature no longer matches payload)
**Result:** 401 Unauthorized "Invalid token"

#### Scenario 4: JWT Secret Leakage
**Attack:** Attacker obtains JWT_SECRET and forges tokens
**Mitigation:** SECRET ROTATION - change JWT_SECRET immediately
**Result:** All existing tokens invalidated, users must re-authenticate

---

## Performance Considerations

**JWT Validation Time:** <10ms per request (PyJWT is fast)
**Caching:** Not needed (validation is stateless and fast)
**Database Queries:** ZERO (no user lookup required, trusts JWT)

**Optimization:**
- JWT validation runs on every protected route call (unavoidable)
- Use dependency injection to avoid duplicated validation logic
- No need to cache validation results (requests are stateless)

---

## Contract Versioning

**Version:** 1.0.0
**Last Updated:** 2025-12-21
**Status:** Stable (Phase 2)

**Breaking Changes Policy:**
- Changes to error response format require major version bump
- Changes to JWT claims require coordination with frontend
- Changes to JWT algorithm require full re-authentication

**Future Enhancements (Phase 3+):**
- Support RS256 (asymmetric signing)
- Support refresh tokens (long-lived sessions)
- Support token revocation (blacklist)

---

## Related Contracts

- [Better Auth Flow Contract](./better-auth-flow.md) - Frontend authentication flow
- [Task CRUD API Contract](../../02-task-crud.md#api-contract) - Uses get_current_user dependency

---

## Summary

**Contract Guarantees:**
- ✅ Returns user_id string if JWT token is valid
- ✅ Raises 401 HTTPException if token is invalid, expired, or missing
- ✅ Validates JWT signature using shared JWT_SECRET
- ✅ Checks token expiration (exp claim)
- ✅ Extracts user_id from 'sub' claim
- ✅ Supports both Authorization header and HTTP-only cookies
- ✅ Zero database queries (stateless validation)
- ✅ Fast performance (<10ms)

**Usage:**
```python
# Dependency injection in route
@router.get("/api/v1/tasks")
async def get_tasks(user_id: str = Depends(get_current_user)):
    # user_id is guaranteed to be valid string from JWT
    # No need for additional validation
    pass
```

This contract is the foundation of user isolation and authentication for all Phase 2 backend APIs.
