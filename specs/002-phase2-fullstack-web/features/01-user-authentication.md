# Feature: User Authentication

## Overview

User Authentication provides secure access control for the multi-user task management application through integration with Better Auth library. This feature enables users to register new accounts, log in with email/password credentials, receive JWT tokens for session management, and log out securely. The frontend manages all authentication operations and issues JWT tokens containing user_id claims, while the backend validates these tokens to enforce user isolation. This is a foundational feature that enables all other Phase 2 features by establishing secure user identity and session management.

## Priority

**Level:** Critical

**Rationale:** User authentication is a blocking dependency for all other Phase 2 features. Without authentication, the application cannot enforce user isolation, protect user data, or provide personalized task management. This feature must be implemented first as it establishes the security foundation for the entire application. All subsequent features (Task CRUD, tagging, filtering, etc.) depend on the user_id extracted from JWT tokens for data ownership and access control.

## Dependencies

**Required Before Implementation:**
- Frontend Next.js 16+ application setup with App Router
- Backend FastAPI application setup with basic server configuration
- PostgreSQL database connection (for Better Auth user storage on frontend side)
- Better Auth library installed and configured in frontend
- Shared TypeScript types for authentication contracts

**Optional/Nice-to-Have:**
- None - this is the foundational feature

**External Dependencies:**
- Better Auth library (manages user credentials, issues JWT tokens)
- JWT library (backend validates tokens - PyJWT for Python)
- PostgreSQL database (Better Auth stores user credentials)
- HTTP-only cookies (secure token storage in browser)

**Important Note:** Backend does NOT have a users table. Better Auth manages users entirely on the frontend side, and the backend trusts the JWT token's user_id claim.

## User Stories

### Story 1: User Registration
**As a** new user
**I want** to create an account with my email and password
**So that** I can access the task management application and keep my tasks private

### Story 2: User Login
**As a** registered user
**I want** to log in with my email and password
**So that** I can access my tasks securely

### Story 3: Automatic Session Management
**As a** logged-in user
**I want** my session to persist across browser refreshes
**So that** I don't have to log in repeatedly during my work session

### Story 4: User Logout
**As a** logged-in user
**I want** to log out of my account
**So that** I can secure my account when using a shared device

### Story 5: Protected Route Access
**As a** system
**I want** to redirect unauthenticated users to the login page
**So that** only authenticated users can access task management features

### Story 6: Backend Token Validation
**As a** backend service
**I want** to validate JWT tokens and extract user_id
**So that** I can enforce user isolation and data ownership

## Acceptance Criteria

### AC1: User Registration Success
**Given** I am on the registration page
**When** I enter a valid email (user@example.com) and password (minimum 8 characters)
**Then** Better Auth creates a new user account
**And** I am automatically logged in with a JWT token stored in an HTTP-only cookie
**And** I am redirected to the dashboard page (/)

### AC2: User Registration Validation
**Given** I am on the registration page
**When** I attempt to register with an invalid email or password shorter than 8 characters
**Then** I receive a validation error message before submission
**And** the registration form does not submit
**And** no API request is made to Better Auth

### AC3: Duplicate Email Prevention
**Given** I am on the registration page
**When** I attempt to register with an email that already exists
**Then** Better Auth returns an error "Email already registered"
**And** I receive a user-friendly message "This email is already in use"
**And** I remain on the registration page

### AC4: User Login Success
**Given** I am on the login page
**When** I enter valid credentials (registered email and correct password)
**Then** Better Auth validates my credentials
**And** Better Auth issues a JWT token with my user_id in the 'sub' claim
**And** the token is stored in an HTTP-only cookie named 'auth-token'
**And** I am redirected to the dashboard page (/)

### AC5: User Login Failure
**Given** I am on the login page
**When** I enter incorrect credentials (wrong password or non-existent email)
**Then** I receive an error message "Invalid email or password"
**And** I remain on the login page
**And** no JWT token is issued or stored

### AC6: Session Persistence
**Given** I am logged in with a valid JWT token
**When** I refresh the browser page
**Then** my session persists (token remains valid)
**And** I remain on the current page without being redirected to login
**And** all subsequent API requests include my JWT token automatically

### AC7: User Logout
**Given** I am logged in
**When** I click the logout button
**Then** Better Auth clears the JWT cookie from my browser
**And** I am redirected to the login page (/login)
**And** subsequent requests to protected routes redirect me to login

### AC8: Protected Route Middleware
**Given** I am NOT logged in (no valid JWT token)
**When** I attempt to access a protected route (/, /tasks, /tasks/[id])
**Then** Next.js middleware detects the missing token
**And** I am redirected to the login page (/login)
**And** the protected page does not render

### AC9: Authenticated User Redirect
**Given** I am logged in with a valid JWT token
**When** I attempt to access the login or register page
**Then** Next.js middleware detects the existing token
**And** I am redirected to the dashboard page (/)
**And** the login/register page does not render

### AC10: Backend JWT Validation
**Given** the frontend sends a request to the backend with a JWT token
**When** the backend receives the request at any /api/v1/* endpoint
**Then** the backend extracts the JWT from the Authorization header or cookie
**And** the backend validates the JWT signature using the shared secret key
**And** the backend extracts user_id from the 'sub' claim
**And** the backend uses user_id to filter database queries (user isolation)

### AC11: Backend Token Expiration Handling
**Given** the frontend sends a request with an expired JWT token
**When** the backend attempts to validate the token
**Then** the backend returns 401 Unauthorized with error "Token has expired"
**And** the frontend detects the 401 error
**And** the frontend redirects the user to the login page

### AC12: Backend Invalid Token Handling
**Given** the frontend sends a request with an invalid or forged JWT token
**When** the backend attempts to validate the token
**Then** the backend returns 401 Unauthorized with error "Invalid token"
**And** the frontend detects the 401 error
**And** the frontend redirects the user to the login page

## Edge Cases

### Edge Case 1: Empty Email or Password
**Scenario:** User submits login/register form with empty email or password fields
**Expected Behavior:** Frontend validation displays error "Email and password are required" before form submission, preventing API call
**Validation:** Form does not submit, no network request made, error message visible

### Edge Case 2: Whitespace-Only Password
**Scenario:** User attempts to register with a password containing only whitespace characters
**Expected Behavior:** Frontend validation trims input and rejects password, displaying "Password cannot be empty or whitespace only"
**Validation:** Registration fails, error message shown, no account created

### Edge Case 3: Very Long Email (>254 characters)
**Scenario:** User enters an email address exceeding 254 characters (max email length per RFC 5321)
**Expected Behavior:** Frontend validation rejects email, displaying "Email address is too long (max 254 characters)"
**Validation:** Form does not submit, validation error visible

### Edge Case 4: SQL Injection Attempt in Email
**Scenario:** User enters email like `admin'--@example.com` or `test@example.com'; DROP TABLE users;--`
**Expected Behavior:** Better Auth safely handles input with parameterized queries, treating it as a literal string, not SQL
**Validation:** No SQL injection occurs, input treated as normal email string

### Edge Case 5: JWT Token Missing 'sub' Claim
**Scenario:** Backend receives a malformed JWT token missing the 'sub' claim (user_id)
**Expected Behavior:** Backend returns 401 Unauthorized with error "Invalid token: missing user_id"
**Validation:** Request rejected, no database query executed

### Edge Case 6: JWT Token with Null or Empty 'sub' Claim
**Scenario:** JWT token contains `"sub": ""` or `"sub": null`
**Expected Behavior:** Backend validates and rejects token, returning 401 Unauthorized "Invalid token: missing user_id"
**Validation:** Request rejected, error logged, no database access

### Edge Case 7: Concurrent Login from Multiple Devices
**Scenario:** User logs in from two different browsers/devices simultaneously
**Expected Behavior:** Both sessions are valid and independent; logging out on one device does not affect the other (stateless JWT)
**Validation:** Both devices can access protected routes independently until their respective tokens expire

### Edge Case 8: Logout Without Active Session
**Scenario:** User clicks logout button when already logged out (no token present)
**Expected Behavior:** Logout function handles gracefully, redirects to login page without error
**Validation:** No errors thrown, clean redirect to /login

### Edge Case 9: Token Expiration During Active Session
**Scenario:** User is actively using the application when their JWT token expires (e.g., after 24 hours)
**Expected Behavior:** Next API request to backend returns 401 Unauthorized, frontend detects this and redirects to login
**Validation:** User redirected to login with message "Your session has expired. Please log in again."

### Edge Case 10: Cookie Disabled in Browser
**Scenario:** User has cookies disabled in browser settings
**Expected Behavior:** Better Auth cannot store JWT cookie, login fails with error "Cookies must be enabled to use this application"
**Validation:** Clear error message displayed, user informed of requirement

### Edge Case 11: Cross-Site Request Forgery (CSRF) Attempt
**Scenario:** Malicious site attempts to use user's JWT cookie to make requests
**Expected Behavior:** HTTP-only cookie prevents JavaScript access, SameSite=Strict prevents cross-origin cookie transmission
**Validation:** CSRF attack fails, cookie not sent with cross-origin requests

### Edge Case 12: Backend Environment Missing JWT Secret
**Scenario:** Backend starts without JWT_SECRET environment variable configured
**Expected Behavior:** Backend fails to start with clear error "JWT_SECRET environment variable is required"
**Validation:** Application does not start, error logged, prevents insecure deployment

## Error Handling

### Error 1: Registration - Email Already Exists
**Scenario:** User attempts to register with an email that already exists in Better Auth's user database
**HTTP Status:** 400 Bad Request (from Better Auth)
**Error Response:**
```json
{
  "detail": "Email already registered"
}
```
**User-Facing Message:** "This email address is already in use. Please log in or use a different email."
**Recovery:** User can navigate to login page or try a different email address

### Error 2: Login - Invalid Credentials
**Scenario:** User provides incorrect email or password
**HTTP Status:** 401 Unauthorized (from Better Auth)
**Error Response:**
```json
{
  "detail": "Invalid email or password"
}
```
**User-Facing Message:** "Invalid email or password. Please try again."
**Recovery:** User can retry with correct credentials or reset password (Phase 3+ feature)

### Error 3: Backend - Missing Authorization Header
**Scenario:** Frontend sends request to backend without JWT token (configuration error)
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Authorization required"
}
```
**User-Facing Message:** "Authentication required. Please log in again."
**Recovery:** Frontend redirects to /login, user re-authenticates

### Error 4: Backend - Invalid JWT Signature
**Scenario:** JWT token has been tampered with or signed with wrong secret key
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid token"
}
```
**User-Facing Message:** "Your session is invalid. Please log in again."
**Recovery:** Frontend redirects to /login, user re-authenticates

### Error 5: Backend - Expired JWT Token
**Scenario:** User's JWT token has passed its expiration time (exp claim)
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Token has expired"
}
```
**User-Facing Message:** "Your session has expired. Please log in again."
**Recovery:** Frontend redirects to /login, user re-authenticates

### Error 6: Backend - Malformed JWT Token
**Scenario:** JWT token is not properly formatted (e.g., missing parts, invalid base64)
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid token format"
}
```
**User-Facing Message:** "Your session is invalid. Please log in again."
**Recovery:** Frontend redirects to /login, user re-authenticates

### Error 7: Network Error During Login
**Scenario:** Network connection fails while attempting to log in
**HTTP Status:** N/A (network timeout)
**Error Response:** Browser network error
**User-Facing Message:** "Network error. Please check your connection and try again."
**Recovery:** User can retry login when connection is restored

### Error 8: Better Auth Service Unavailable
**Scenario:** Better Auth service or PostgreSQL database is down during authentication attempt
**HTTP Status:** 500 Internal Server Error (from Better Auth)
**Error Response:**
```json
{
  "detail": "Authentication service temporarily unavailable"
}
```
**User-Facing Message:** "Authentication service is temporarily unavailable. Please try again in a moment."
**Recovery:** User waits and retries, error logged for ops team investigation

### Error 9: Frontend - Middleware Configuration Error
**Scenario:** Middleware fails to check authentication status (code bug)
**HTTP Status:** N/A (client-side error)
**Error Response:** JavaScript error in console
**User-Facing Message:** "An unexpected error occurred. Please refresh the page."
**Recovery:** User refreshes page, error logged for debugging

### Error 10: Backend - JWT Secret Mismatch
**Scenario:** Backend is configured with a different JWT secret than frontend (deployment error)
**HTTP Status:** 401 Unauthorized
**Error Response:**
```json
{
  "detail": "Invalid token"
}
```
**User-Facing Message:** "Authentication configuration error. Please contact support."
**Recovery:** Ops team must align JWT secrets between frontend and backend environments

## Non-Goals

This feature specifically does NOT include:

- **Password Reset/Recovery:** Forgot password functionality is deferred to Phase 3+. Users must remember their passwords or create a new account in Phase 2.
  (Reason: Adds complexity with email service integration, password reset tokens, and expiration logic)

- **Email Verification:** New accounts are immediately active without email confirmation. No verification email is sent.
  (Reason: Requires email service integration, verification tokens, and handling unverified user states)

- **Social Login (OAuth):** No login via Google, GitHub, Facebook, etc. Only email/password authentication is supported.
  (Reason: OAuth integration adds complexity with provider SDKs, callback handling, and token exchange)

- **Multi-Factor Authentication (MFA):** No 2FA, TOTP, SMS codes, or authenticator apps.
  (Reason: Requires additional infrastructure for SMS/authenticator integration and backup codes management)

- **User Profile Management:** Users cannot update their email, password, or profile information in Phase 2.
  (Reason: Out of scope for authentication feature; belongs to separate User Profile feature in Phase 3+)

- **Session Management UI:** No interface to view active sessions or revoke tokens from other devices.
  (Reason: Requires session storage, active session tracking, and token revocation mechanism)

- **Remember Me / Extended Sessions:** All JWT tokens have the same expiration time (24 hours). No option for longer sessions.
  (Reason: Adds complexity with refresh tokens and sliding expiration logic)

- **Account Deletion:** Users cannot delete their accounts or associated data.
  (Reason: Belongs to separate User Management feature; requires data cleanup and GDPR compliance handling)

- **Rate Limiting on Auth Endpoints:** No protection against brute force login attempts (e.g., account lockout after N failed attempts).
  (Reason: Requires distributed state management; deferred to Phase 4 security enhancements)

- **User Roles and Permissions:** All users have the same access level. No admin, moderator, or custom roles.
  (Reason: Role-based access control is a Phase 4+ feature for team collaboration)

- **Backend User Management:** Backend does NOT store, query, or manage user records. No users table exists in the backend database.
  (Reason: Better Auth manages users entirely on frontend side; backend only validates JWT tokens)

- **Token Refresh:** JWT tokens cannot be refreshed. When a token expires, user must log in again.
  (Reason: Refresh tokens add complexity with secure storage and rotation; deferred to Phase 3+ if needed)

## API Contract

### Important Note on API Endpoints

**This feature has NO dedicated authentication endpoints in the backend.** Better Auth handles all authentication operations (registration, login, logout) entirely on the frontend. The backend's only role is to validate JWT tokens that the frontend has already issued.

**Frontend Authentication (Better Auth):**
- Better Auth provides its own API routes on the frontend (handled by Next.js API routes)
- Frontend calls Better Auth methods: `signIn()`, `signUp()`, `signOut()`
- Better Auth manages user credentials and issues JWT tokens
- No custom backend authentication endpoints needed

**Backend Role:**
- Backend ONLY validates JWT tokens received in API requests
- Backend uses `Depends(get_current_user)` dependency to extract user_id from JWT
- Backend has NO authentication endpoints (no /api/v1/auth/*)

### Backend Dependency: JWT Validation

**Function:** `get_current_user()`

**Purpose:** Validate JWT token and extract user_id from 'sub' claim

**Location:** Dependency injection in all protected backend endpoints

**Input:**
- **Headers:**
  - Authorization: Bearer {JWT_TOKEN} (Required)
  - OR Cookie: auth-token={JWT_TOKEN} (Fallback)

**Process:**
1. Extract JWT token from Authorization header or auth-token cookie
2. Decode and validate JWT signature using shared JWT_SECRET
3. Check token expiration (exp claim)
4. Extract user_id from 'sub' claim
5. Return user_id to route handler

**Output (Success):**
- Returns: user_id (string) - Used for database query filtering

**Errors:**
- **401 Unauthorized:** Missing token, invalid signature, expired token, or missing 'sub' claim
  ```json
  {
    "detail": "Authorization required"
  }
  ```
  ```json
  {
    "detail": "Invalid token"
  }
  ```
  ```json
  {
    "detail": "Token has expired"
  }
  ```
  ```json
  {
    "detail": "Invalid token: missing user_id"
  }
  ```

**Example Usage in Route:**
```python
@router.get("/api/v1/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user),  # Extracts user_id from JWT
    session: Session = Depends(get_db)
):
    # user_id is automatically available from JWT token
    # All queries MUST filter by user_id
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    )
    tasks = session.exec(statement).all()
    return tasks
```

### Frontend Authentication Flow (Better Auth)

**Better Auth manages authentication entirely on the frontend:**

1. **Registration:** Frontend calls `signUp({ email, password })`
2. **Login:** Frontend calls `signIn({ email, password })`
3. **Logout:** Frontend calls `signOut()`
4. **Session Check:** Frontend calls `getSession()` to check auth status

**Better Auth automatically:**
- Stores JWT in HTTP-only cookie named 'auth-token'
- Includes cookie in all requests (credentials: 'include')
- Handles token expiration and validation errors
- Provides session state to React components

**No custom API contracts needed** - Better Auth handles everything on frontend side.

## Data Model

### Important: NO Users Table in Backend

**The backend database does NOT include a users table.** User credentials and account information are stored entirely by Better Auth in its own PostgreSQL database (separate from the backend task database).

**Backend Data Model:**
- Backend database stores task data only (tasks table)
- Backend trusts the user_id claim from JWT tokens
- Backend NEVER queries or stores user account information
- user_id is treated as an opaque string identifier

**Architecture:**
- **Frontend Database (Better Auth):** Stores users, credentials, sessions
- **Backend Database (Task Management):** Stores tasks, tags, etc. with user_id foreign reference
- **JWT Token:** Bridges the two systems by carrying user_id from frontend to backend

### User Identifier in Backend

**Field Used in Backend Tasks Table:**
- `user_id`: string (from JWT 'sub' claim) - Owner's user ID from Better Auth
  - Type: String (UUID format, but treated as opaque string)
  - Indexed: Yes (frequently queried)
  - Nullable: No (every task must have an owner)
  - Validation: Must be present in JWT token 'sub' claim

**Example Task Record:**
```json
{
  "id": 123,
  "user_id": "user-uuid-from-jwt",  // From JWT token, NOT from backend database
  "title": "My Task",
  "description": "Task details",
  "created_at": "2025-12-21T10:30:00Z",
  "updated_at": "2025-12-21T10:30:00Z"
}
```

**Backend Database Schema:**
```sql
-- NO users table in backend!

-- Tasks table only
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,  -- From JWT, no foreign key
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  deleted_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for user isolation queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

**Important:** `user_id` in the tasks table is NOT a foreign key. It's just a string value that comes from the JWT token. The backend does not validate user existence - it trusts the JWT.

### Frontend User Management (Better Auth)

**Better Auth manages users in its own database schema:**
- Users table (email, hashed password, etc.)
- Sessions table (if using session-based auth)
- Email verification tokens (Phase 3+)
- Password reset tokens (Phase 3+)

**Frontend does not expose user CRUD operations to the backend.** Better Auth handles all user management internally.

## UI/UX Requirements

### UI Element 1: Login Page
**Purpose:** Allow existing users to authenticate with email and password
**Location:** Route `/login`, public page (no authentication required to view)
**Behavior:**
- Display centered login form with email and password fields
- Email field: type="email", autocomplete="email", required
- Password field: type="password", autocomplete="current-password", required, show/hide password toggle
- "Log in" submit button (primary action)
- Link to registration page: "Don't have an account? Sign up"
- Display validation errors inline below each field
- Display authentication errors above the form (e.g., "Invalid email or password")
- Disable submit button and show loading spinner during submission
- Clear password field after failed login attempt (security best practice)

**States:**
- **Idle:** Form ready for input, submit button enabled
- **Validating:** Client-side validation on blur, show errors inline
- **Submitting:** Submit button disabled, loading spinner visible, "Logging in..." text
- **Error:** Error message displayed above form, fields retain values (except password), submit button re-enabled
- **Success:** Brief success indicator, then automatic redirect to dashboard (/)

### UI Element 2: Registration Page
**Purpose:** Allow new users to create an account with email and password
**Location:** Route `/register`, public page (no authentication required to view)
**Behavior:**
- Display centered registration form with email and password fields
- Email field: type="email", autocomplete="email", required
- Password field: type="password", autocomplete="new-password", required, minimum 8 characters, show/hide password toggle
- Password strength indicator (visual meter: weak/medium/strong)
- "Create Account" submit button (primary action)
- Link to login page: "Already have an account? Log in"
- Display validation errors inline below each field
- Display authentication errors above the form (e.g., "Email already registered")
- Disable submit button and show loading spinner during submission

**States:**
- **Idle:** Form ready for input, submit button enabled
- **Validating:** Client-side validation on blur, password strength indicator updates on input
- **Submitting:** Submit button disabled, loading spinner visible, "Creating account..." text
- **Error:** Error message displayed above form, fields retain values (except password), submit button re-enabled
- **Success:** Brief success indicator, automatic login, redirect to dashboard (/)

### UI Element 3: Logout Button
**Purpose:** Allow authenticated users to end their session securely
**Location:** Global navigation header (visible on all authenticated pages)
**Behavior:**
- Display as button or menu item in header (e.g., "Log out" or user avatar with dropdown)
- On click: call Better Auth signOut(), clear JWT cookie, redirect to /login
- Show brief loading indicator if logout takes time
- No confirmation dialog needed (logout is non-destructive)

**States:**
- **Idle:** Clickable button visible in header
- **Loading:** Brief spinner or disabled state during logout
- **Success:** Automatic redirect to login page

### UI Element 4: Protected Route Middleware (Invisible UX)
**Purpose:** Automatically redirect unauthenticated users to login page
**Location:** Next.js middleware applied to all routes except /login and /register
**Behavior:**
- Check for valid JWT token in auth-token cookie
- If token present: allow access to route
- If token missing: redirect to /login with original URL stored (optional: return to after login)
- If accessing /login or /register with valid token: redirect to dashboard (/)
- No visible UI - operates transparently in background

**States:**
- **Authenticated:** User proceeds to requested page
- **Unauthenticated:** User redirected to /login
- **Already Authenticated (on auth pages):** User redirected to /

### UI Element 5: Session Expired Message
**Purpose:** Inform user when their JWT token has expired and they need to re-authenticate
**Location:** Triggered on any page when backend returns 401 Unauthorized due to expired token
**Behavior:**
- Detect 401 error from backend API response
- Display toast notification or alert: "Your session has expired. Please log in again."
- Automatically redirect to /login after 2 seconds (or immediately)
- Clear any local state to prevent stale data display

**States:**
- **Detected:** 401 error received from backend
- **Message Displayed:** Toast or alert visible for 2 seconds
- **Redirected:** User sent to /login, message dismissed

### UI Element 6: Authentication Error Messages
**Purpose:** Provide clear, actionable feedback when authentication operations fail
**Location:** Login and registration forms, above form fields
**Behavior:**
- Display error message in red box with error icon
- Error persists until user edits a field or submits again
- Errors are user-friendly, not technical (e.g., "Invalid email or password" not "401 Unauthorized")
- Include retry guidance where applicable

**Example Messages:**
- "Invalid email or password. Please try again." (login failure)
- "This email is already in use. Please log in or use a different email." (registration conflict)
- "Password must be at least 8 characters." (validation error)
- "Network error. Please check your connection and try again." (network failure)
- "Authentication service is temporarily unavailable. Please try again in a moment." (server error)

**States:**
- **No Error:** Error box not visible
- **Error Displayed:** Red box with error icon and message
- **Error Dismissed:** User edits field or submits form, error clears

### UI Element 7: Loading States
**Purpose:** Provide feedback during asynchronous authentication operations
**Location:** Login and registration forms, logout button
**Behavior:**
- Display loading spinner or skeleton UI during API calls
- Disable form inputs and submit button to prevent double submission
- Update button text to indicate action (e.g., "Logging in...", "Creating account...")
- Prevent navigation during loading to avoid incomplete operations

**States:**
- **Loading Login:** "Logging in..." text, spinner on button, form disabled
- **Loading Registration:** "Creating account..." text, spinner on button, form disabled
- **Loading Logout:** Brief spinner on logout button or header

### UI Element 8: Password Visibility Toggle
**Purpose:** Allow users to show/hide password input for easier verification
**Location:** Password fields on login and registration forms
**Behavior:**
- Display eye icon button next to password field
- Default state: password hidden (type="password", characters shown as dots)
- On click: toggle between hidden and visible (type="text")
- Icon changes between open eye (visible) and closed eye (hidden)
- Accessible via keyboard (focusable button)

**States:**
- **Hidden (default):** Password shown as dots, closed eye icon
- **Visible:** Password shown as plain text, open eye icon

### UI Element 9: Responsive Layout
**Purpose:** Ensure authentication pages work well on all device sizes
**Location:** All authentication pages (/login, /register)
**Behavior:**
- Mobile (< 768px): Full-width form with padding, vertical layout
- Tablet (768px - 1024px): Centered form with max-width 480px
- Desktop (> 1024px): Centered form with max-width 480px
- All touch targets minimum 44x44px for mobile accessibility
- Form fields stack vertically on all screen sizes
- Adequate spacing between fields and buttons

**States:**
- **Mobile:** Full-width with padding
- **Tablet/Desktop:** Centered card with shadow

### UI Element 10: Accessibility Features
**Purpose:** Ensure authentication is accessible to all users including those using assistive technologies
**Location:** All authentication UI elements
**Behavior:**
- All form fields have associated `<label>` elements
- Error messages are announced to screen readers (aria-live regions)
- Focus management: after failed login, focus returns to first invalid field
- Keyboard navigation: all interactive elements focusable and usable via keyboard
- Focus indicators visible on all interactive elements
- Semantic HTML: `<form>`, `<button>`, `<input>` elements used correctly
- Alt text for any icons or images
- Color is not the only indicator of errors (also use icons and text)

**ARIA Attributes:**
- `aria-label` on password toggle button: "Show password" / "Hide password"
- `aria-required="true"` on required fields
- `aria-invalid="true"` on fields with validation errors
- `aria-describedby` linking fields to error messages
- `role="alert"` on authentication error messages for screen reader announcement
