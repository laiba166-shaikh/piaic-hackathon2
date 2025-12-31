# JWT Authentication Fix - EdDSA with JWKS Verification

## Problem

Better Auth's JWT plugin **only supports asymmetric algorithms** (EdDSA, ES256, RS256, etc.) and does NOT support HS256 (symmetric algorithm). This was causing a mismatch between:
- **Frontend**: Generating EdDSA tokens
- **Backend**: Expecting HS256 tokens

## Solution

Changed the entire authentication flow to use **EdDSA with JWKS (JSON Web Key Set) verification**:
- Frontend generates EdDSA tokens (Better Auth default)
- Backend verifies tokens using public keys from JWKS endpoint

---

## Changes Made

### Frontend Changes

#### 1. `src/core/frontend/lib/auth.ts`
- Removed HS256 configuration
- Using Better Auth's default EdDSA algorithm
- Public keys available at `/api/auth/jwks`

```typescript
plugins: [
  jwt(),  // Uses EdDSA (default)
],
```

#### 2. `src/core/frontend/lib/auth-client.ts`
- Removed HS256 configuration from client
- Using default EdDSA

```typescript
plugins: [
  jwtClient(),  // Uses EdDSA (default)
],
```

### Backend Changes

#### 1. `src/core/backend/dependencies.py`
**Complete rewrite** to use JWKS verification:

- Added `fetch_jwks()` - Fetches public keys from Better Auth
- Added `get_signing_key()` - Finds correct public key for token
- Updated `get_current_user()` - Verifies EdDSA tokens using public key
- **JWKS is cached for 1 hour** to avoid excessive requests

Flow:
```
1. Receive JWT token from request
2. Fetch JWKS from http://localhost:3000/api/auth/jwks
3. Extract key ID (kid) from token header
4. Find matching public key in JWKS
5. Verify token signature using EdDSA algorithm
6. Extract user_id from 'sub' claim
```

#### 2. `src/core/backend/config.py`
- Removed `JWT_SECRET` (no longer needed)
- Removed `JWT_ALGORITHM` (no longer needed)
- Added `FRONTEND_URL` - Location of Better Auth JWKS endpoint

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    FRONTEND_URL: str = "http://localhost:3000"
    DEBUG: bool = False
```

---

## How It Works

### Token Generation (Frontend)

1. User logs in via Better Auth
2. Frontend calls `authClient.token()` to get JWT
3. Better Auth generates EdDSA token signed with **private key**
4. Token stored in localStorage as `jwt_token`

**Token Header:**
```json
{
  "alg": "EdDSA",
  "kid": "unique-key-id",
  "typ": "JWT"
}
```

### Token Verification (Backend)

1. Backend receives request with `Authorization: Bearer <token>`
2. Backend fetches JWKS from `http://localhost:3000/api/auth/jwks`
3. Backend finds public key matching token's `kid`
4. Backend verifies token signature using **public key**
5. Backend extracts `user_id` from token's `sub` claim

**JWKS Response:**
```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "base64url-encoded-public-key",
      "kid": "unique-key-id"
    }
  ]
}
```

---

## Testing Steps

### 1. Restart Both Servers

**Frontend:**
```bash
cd src/core/frontend
npm run dev
```

**Backend:**
```bash
cd src/core/backend
uvicorn main:app --reload
```

### 2. Clear Browser Storage

```javascript
// In browser console (F12)
localStorage.clear()
sessionStorage.clear()
document.cookie.split(";").forEach(c => {
  document.cookie = c.trim().split("=")[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';
});
location.reload()
```

### 3. Log In

Navigate to `/login` and log in with your credentials

### 4. Verify Token Algorithm

```javascript
// In browser console
const token = localStorage.getItem('jwt_token')
if (token) {
  const header = JSON.parse(atob(token.split('.')[0]))
  console.log('Algorithm:', header.alg)  // Should be "EdDSA"
  console.log('Key ID:', header.kid)     // Should have a kid
}
```

### 5. Test API Request

Navigate to `/tasks` and check:
- ✅ No authentication errors
- ✅ Backend logs show successful JWKS fetch
- ✅ Backend logs show successful token verification
- ✅ Tasks load successfully

---

## Expected Logs

### Frontend Console
```
[useAuthInit] ===== Starting auth initialization =====
[useAuthInit] Step 1: Checking Better Auth session...
[useAuthInit] Session status: EXISTS
[useAuthInit] JWT token in localStorage: NOT FOUND
[useAuthInit] Step 2: Session exists but JWT missing - retrieving token
[useAuthInit] JWT token retrieved and stored
[useAuthInit] Token preview: eyJhbGciOiJFZERTQSI...
[useAuthInit] ===== Auth initialization COMPLETE =====

[TasksPageClient] Component mounted, calling loadTasks
[TasksPageClient] JWT token exists: true
[TasksPageClient] Token preview: eyJhbGciOiJFZERTQSI...
[API] Making request to: /api/v1/tasks with token
[TasksPageClient] Successfully loaded tasks: 0
```

### Backend Logs
```
INFO - Attempting to verify JWT token (preview): eyJhbGciOiJFZERTQSI...
INFO - Fetching JWKS from: http://localhost:3000/api/auth/jwks
INFO - Successfully fetched JWKS with 1 keys
INFO - Found matching signing key with kid: abc123...
INFO - JWT decoded successfully. Payload: {'sub': 'user_id', ...}
INFO - JWT validation successful for user_id: user_id
```

---

## Benefits of This Approach

1. **Secure**: Asymmetric cryptography (private key never leaves Better Auth)
2. **Standard**: Follows OAuth 2.0 / OIDC best practices
3. **Scalable**: Public keys can be cached, reducing verification overhead
4. **Flexible**: Supports key rotation (Better Auth can rotate keys automatically)
5. **No Shared Secrets**: Backend doesn't need JWT_SECRET

---

## Troubleshooting

### Issue: 401 Unauthorized

**Check:**
1. Token algorithm is EdDSA (not HS256)
2. Backend can reach `http://localhost:3000/api/auth/jwks`
3. Token has `kid` in header
4. JWKS contains a key matching the token's `kid`

**Test JWKS endpoint:**
```bash
curl http://localhost:3000/api/auth/jwks
```

### Issue: "Unable to verify authentication token"

**Cause:** Backend cannot fetch JWKS from frontend

**Solution:**
- Ensure frontend is running on `http://localhost:3000`
- Check `FRONTEND_URL` in backend `.env`
- Verify no CORS or network issues

### Issue: Token has EdDSA but still fails

**Cause:** JWKS caching issue or key mismatch

**Solution:**
1. Restart backend to clear JWKS cache
2. Log out and log in again to get fresh token
3. Check backend logs for JWKS fetch errors

---

## Environment Variables

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here
DATABASE_URL=postgresql://...
```

### Backend `.env`
```bash
DATABASE_URL=postgresql://...
FRONTEND_URL=http://localhost:3000
DEBUG=True
```

**Note:** `JWT_SECRET` and `JWT_ALGORITHM` are **no longer used** and can be removed.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       User Browser                          │
│                                                             │
│  1. Login  ──────────────────────────────────────────────┐  │
│                                                          │  │
│  2. Get JWT Token (EdDSA)                                │  │
│     ├─ authClient.token()                                │  │
│     └─ Store in localStorage                             │  │
│                                                          │  │
│  3. API Request                                          │  │
│     └─ Authorization: Bearer <EdDSA-token>               │  │
└──────────────────────────────────────────────────────────┼──┘
                                                           │
                                      │                    │
                                      ▼                    │
┌─────────────────────────────────────────────────────┐    │
│              Next.js Frontend                       │    │
│           (http://localhost:3000)                   │    │
│                                                     │    │
│  Better Auth Server                                 │    │
│  ├─ /api/auth/sign-in   (login)                     │◄───┘
│  ├─ /api/auth/token     (get JWT) ──────────────────┼───────┐
│  └─ /api/auth/jwks      (public keys)               │       │
│                                                     │       │
│  EdDSA Token Generation:                            │       │
│  ├─ Sign with private key                           │       │
│  ├─ Include kid (key ID)                            │       │
│  └─ Store private key in database                   │       │
└─────────────────────────────────────────────────────┘       │
                                                              │
                                      │                       │
                                      ▼                       │
┌─────────────────────────────────────────────────────┐       │
│             FastAPI Backend                         │       │
│          (http://localhost:8000)                    │       │
│                                                     │       │
│  API Request Handler                                │       │
│  └─ /api/v1/tasks                                   │       │
│                                                     │       │
│  JWT Verification (dependencies.py):                │       │
│  1. Fetch JWKS from frontend ──────────────────────►│       │
│       http://localhost:3000/api/auth/jwks           │       │
│       (Cached for 1 hour)                           │       │
│                                                     │       │
│  2. Extract kid from token header                   │       │
│                                                     │       │
│  3. Find matching public key in JWKS                │       │
│                                                     │       │
│  4. Verify signature with EdDSA algorithm           │       │
│                                                     │       │
│  5. Extract user_id from 'sub' claim  ◄─────────────┼───────┘
│                                                     │
│  6. Execute request with user_id                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

**Implementation Date:** 2025-12-29
**Status:** Ready for Testing
