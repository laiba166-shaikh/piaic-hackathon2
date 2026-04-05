"""
JWT token generation utilities for testing (EdDSA/Ed25519).

Generates tokens that match the actual get_current_user() verification flow:
- Signed with Ed25519 private key
- JWKS endpoint mocked via get_test_jwks()
- Tokens include iss/aud claims matching FRONTEND_URL
"""

import base64
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# ---------------------------------------------------------------------------
# Static test keypair — generated once per process, reused across all tests.
# ---------------------------------------------------------------------------
TEST_KEY_ID = "test-key-id-1"
TEST_FRONTEND_URL = "http://localhost:3000"

_PRIVATE_KEY: Ed25519PrivateKey = Ed25519PrivateKey.generate()
_PUBLIC_KEY = _PRIVATE_KEY.public_key()


def get_test_jwks() -> dict:
    """
    Return a JWKS dict containing the test Ed25519 public key.

    Use this to mock fetch_jwks() in tests so get_current_user()
    verifies tokens against the test keypair instead of calling
    the real frontend JWKS endpoint.

    Returns:
        dict: JWKS with one Ed25519 key entry
    """
    pub_bytes = _PUBLIC_KEY.public_bytes_raw()
    x = base64.urlsafe_b64encode(pub_bytes).rstrip(b"=").decode()
    return {
        "keys": [
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "kid": TEST_KEY_ID,
                "x": x,
            }
        ]
    }


def create_test_jwt(
    user_id: str = "test-user-123",
    expired: bool = False,
    include_sub: bool = True,
) -> str:
    """
    Generate a test JWT token signed with the test Ed25519 private key.

    The token matches what Better Auth's JWT plugin produces:
    - EdDSA algorithm (Ed25519)
    - iss and aud set to FRONTEND_URL
    - kid in header matches TEST_KEY_ID

    Args:
        user_id: Value for the 'sub' claim
        expired: If True, sets exp to 1 hour in the past
        include_sub: If False, omits the 'sub' claim (tests missing-sub path)

    Returns:
        str: Signed JWT string
    """
    now = datetime.now(tz=UTC)
    payload: dict = {
        "iat": now,
        "exp": now + timedelta(hours=-1 if expired else 24),
        "iss": TEST_FRONTEND_URL,
        "aud": TEST_FRONTEND_URL,
    }

    if include_sub:
        payload["sub"] = user_id

    return jwt.encode(
        payload,
        _PRIVATE_KEY,
        algorithm="EdDSA",
        headers={"kid": TEST_KEY_ID},
    )


def create_invalid_jwt() -> str:
    """
    Generate a JWT signed with a different Ed25519 key (invalid signature).

    The token header has the correct kid so the backend will find the
    matching public key — but signature verification will fail because
    the token was signed with a different private key.

    Returns:
        str: JWT token that will fail signature verification
    """
    wrong_key = Ed25519PrivateKey.generate()
    now = datetime.now(tz=UTC)
    payload = {
        "sub": "test-user-123",
        "exp": now + timedelta(hours=24),
        "iat": now,
        "iss": TEST_FRONTEND_URL,
        "aud": TEST_FRONTEND_URL,
    }
    return jwt.encode(
        payload,
        wrong_key,
        algorithm="EdDSA",
        headers={"kid": TEST_KEY_ID},
    )
