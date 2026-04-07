"""FastAPI dependencies for authentication and database access."""

import base64
import logging
from functools import lru_cache
from typing import Any

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from db import get_session

# Configure logger
logger = logging.getLogger(__name__)

security = HTTPBearer()

# Cache JWKS for 1 hour to avoid frequent requests
@lru_cache(maxsize=1)
def get_jwks_cache_key() -> str:
    """Return a cache key that changes every hour."""
    import time
    return str(int(time.time() / 3600))


async def fetch_jwks() -> dict[str, Any]:
    """
    Fetch JWKS (JSON Web Key Set) from Better Auth endpoint.

    The JWKS contains public keys used to verify JWT signatures.
    Results are cached for 1 hour.

    Returns:
        Dict containing JWKS data with public keys

    Raises:
        HTTPException: If JWKS cannot be fetched
    """
    # Force cache refresh every hour by using time-based cache key
    cache_key = get_jwks_cache_key()

    jwks_url = f"{settings.FRONTEND_URL}/api/auth/jwks"
    logger.info(f"Fetching JWKS from: {jwks_url} (cache_key: {cache_key})")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=5.0)
            if not response.is_success:
                logger.error(
                    f"JWKS endpoint returned {response.status_code}: {response.text[:200]}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to verify authentication token"
                )
            jwks_data = response.json()
            logger.info(f"Successfully fetched JWKS with {len(jwks_data.get('keys', []))} keys")
            return jwks_data
    except HTTPException:
        raise
    except httpx.ConnectError:
        logger.error(f"Cannot reach frontend at {jwks_url} — is the frontend running?")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to verify authentication token"
        )
    except Exception as e:
        logger.error(f"Failed to fetch JWKS from {jwks_url}: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to verify authentication token"
        )


def get_signing_key(token: str, jwks_data: dict[str, Any]) -> Ed25519PublicKey:
    """
    Extract and convert the EdDSA public key from JWKS.

    Args:
        token: JWT token string
        jwks_data: JWKS data containing public keys

    Returns:
        Ed25519PublicKey object for verification

    Raises:
        HTTPException: If signing key cannot be found or converted
    """
    # Decode token header to get key ID (kid)
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')

        if not kid:
            logger.error("JWT token missing 'kid' (key ID) in header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token format"
            )

        # Find matching key in JWKS
        jwk_key = None
        for key in jwks_data.get('keys', []):
            if key.get('kid') == kid:
                jwk_key = key
                logger.info(f"Found matching signing key with kid: {kid}")
                break

        if not jwk_key:
            logger.error(f"No matching key found for kid: {kid}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # Convert JWKS EdDSA key to Ed25519PublicKey
        # For EdDSA/Ed25519, the public key is in the 'x' parameter (base64url encoded)
        if jwk_key.get('kty') != 'OKP' or jwk_key.get('crv') != 'Ed25519':
            logger.error(f"Unexpected key type: {jwk_key.get('kty')}/{jwk_key.get('crv')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unsupported key type"
            )

        # Decode the base64url-encoded public key
        x_param = jwk_key.get('x')
        if not x_param:
            logger.error("JWKS key missing 'x' parameter")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid key format"
            )

        # Add padding if needed for base64 decoding
        x_param += '=' * (4 - len(x_param) % 4)
        public_key_bytes = base64.urlsafe_b64decode(x_param)

        # Create Ed25519PublicKey from bytes
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        logger.info("Successfully converted JWKS key to Ed25519PublicKey")

        return public_key

    except jwt.DecodeError as e:
        logger.error(f"Failed to decode JWT header: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Failed to process signing key: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate JWT token using JWKS public key verification.

    This function:
    1. Fetches the JWKS (public keys) from Better Auth
    2. Finds the correct public key using the token's key ID
    3. Verifies the token signature using EdDSA algorithm
    4. Extracts and returns the user_id from the token

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        str: The user_id from the JWT token's 'sub' claim

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    try:
        token = credentials.credentials
        logger.info(f"Attempting to verify JWT token (preview): {token[:50]}...")

        # Fetch JWKS (cached for 1 hour)
        jwks_data = await fetch_jwks()

        # Get the EdDSA public key for this token
        public_key = get_signing_key(token, jwks_data)

        # Log unverified claims to help debug issuer/audience mismatches
        unverified = jwt.decode(token, options={"verify_signature": False})
        logger.info(f"""Token claims — iss: {unverified.get('iss')},
                    aud: {unverified.get('aud')},
                    expected: {settings.FRONTEND_URL}"""
                )

        # Verify and decode the token using PyJWT with EdDSA
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['EdDSA'],
            audience=settings.FRONTEND_URL,
            issuer=settings.FRONTEND_URL,
            options={
                'verify_signature': True,
                'verify_exp': True,
                'verify_aud': True,
                'verify_iss': True,
            }
        )
        logger.info(f"JWT decoded successfully. Payload: {payload}")

        user_id: str = payload.get("sub")

        if user_id is None:
            logger.warning(f"JWT validation failed: missing 'sub' claim. Payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        logger.info(f"JWT validation successful for user_id: {user_id}")
        return user_id

    except jwt.ExpiredSignatureError as e:
        logger.warning(f"JWT validation failed: token has expired - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again."
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT validation failed: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    except HTTPException:
        # Re-raise HTTP exceptions from helper functions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during JWT validation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication verification failed"
        )


def get_db():
    """
    Database session dependency.

    Usage:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_db)):
            ...

    Yields:
        Session: SQLModel database session
    """
    yield from get_session()
