# Authentication Flow Debugging Guide

## Current Issue
Getting "Authentication required" error when navigating to `/tasks` page.

## Debugging Steps

### Step 1: Check Browser Console
Open your browser's Developer Tools (F12) and go to the Console tab. You should see logs from:
- `[useAuthInit]` - Auth initialization in root layout
- `[TasksPageClient]` - Tasks page loading
- `[API]` - API requests to backend

### Step 2: Check localStorage for JWT Token

1. Open Developer Tools (F12)
2. Go to Application/Storage > Local Storage
3. Look for `jwt_token` key
4. Check if it exists and preview the value

**Expected token format:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
The algorithm should be `HS256` (not `EdDSA`)

### Step 3: Decode the JWT Token

Go to https://jwt.io and paste your token to check:
- **Algorithm**: Should be `HS256` (NOT `EdDSA`)
- **Payload**: Should have `sub` claim with user ID
- **Expiration**: Check if token has expired

### Step 4: Clear Old Tokens (IMPORTANT)

If you have an old EdDSA token from before the algorithm fix, you need to clear it:

1. Open Developer Tools (F12)
2. Go to Console
3. Run this command:
   ```javascript
   localStorage.clear()
   ```
4. Refresh the page
5. Log out and log back in

### Step 5: Monitor the Auth Flow

After clearing and logging back in, navigate to `/tasks` and watch the console logs in this order:

**Expected sequence:**
```
[useAuthInit] ===== Starting auth initialization =====
[useAuthInit] Step 1: Checking Better Auth session...
[useAuthInit] Session status: EXISTS
[useAuthInit] JWT token in localStorage: NOT FOUND
[useAuthInit] Step 2: Session exists but JWT missing - retrieving token
[useAuthInit] JWT token retrieved and stored
[useAuthInit] Token preview: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
[useAuthInit] Step 4: Auth state SYNCHRONIZED (session + JWT both exist)
[useAuthInit] ===== Auth initialization COMPLETE =====

[TasksPageClient] Component mounted, calling loadTasks
[TasksPageClient] Starting loadTasks...
[TasksPageClient] Checking localStorage for JWT token...
[TasksPageClient] JWT token exists: true
[TasksPageClient] Token preview: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
[TasksPageClient] Calling api.getTasks()...
[API] Making request to: /api/v1/tasks with token
[TasksPageClient] Successfully loaded tasks: 0 (or number of tasks)
```

## Common Issues

### Issue 1: Race Condition
**Symptoms:**
```
[TasksPageClient] Component mounted, calling loadTasks
[TasksPageClient] JWT token exists: false
[API] No JWT token found for request to: /api/v1/tasks
```

**Cause:** TasksPageClient loaded before AuthInitializer completed

**Solution:** Wait for auth initialization or add retry logic

### Issue 2: Old EdDSA Token
**Symptoms:**
```
[useAuthInit] Token preview: eyJhbGciOiJFZERTQSI...
Backend: JWT validation failed: Invalid signature
```

**Cause:** Token signed with EdDSA algorithm instead of HS256

**Solution:** Clear localStorage and get new token (see Step 4)

### Issue 3: Token Expired
**Symptoms:**
```
Backend: JWT validation failed: token has expired
```

**Cause:** JWT token expired (24 hour expiration)

**Solution:** Log out and log back in to get fresh token

### Issue 4: No Session
**Symptoms:**
```
[useAuthInit] Session status: NOT FOUND
[useAuthInit] JWT token in localStorage: NOT FOUND
[useAuthInit] Step 4: No auth (session + JWT both missing) - user needs to login
```

**Cause:** User not logged in

**Solution:** Navigate to `/login` and log in

## Backend Logs to Check

If backend is running, check for these logs:

```bash
INFO - Attempting to decode JWT token (preview): eyJhbGci...
INFO - JWT decoded successfully. Payload: {'sub': 'user_id', ...}
INFO - JWT validation successful for user_id: user_id
```

**Or errors:**
```bash
ERROR - JWT validation failed: JWTError - Invalid signature
ERROR - JWT_SECRET being used: <secret>...
ERROR - JWT_ALGORITHM: HS256
```

## Quick Fix Commands

### Clear localStorage (in browser console):
```javascript
localStorage.clear()
location.reload()
```

### Check JWT token (in browser console):
```javascript
const token = localStorage.getItem('jwt_token')
console.log('Token exists:', !!token)
if (token) {
  console.log('Token preview:', token.substring(0, 100))
  // Decode header
  const header = JSON.parse(atob(token.split('.')[0]))
  console.log('Algorithm:', header.alg)
}
```

### Restart Backend with Logs:
```bash
cd src/core/backend
uvicorn main:app --reload --log-level info
```

## Next Steps

1. Follow Step 4 to clear localStorage
2. Log out completely
3. Log back in
4. Navigate to `/tasks`
5. Share the console logs if issue persists
