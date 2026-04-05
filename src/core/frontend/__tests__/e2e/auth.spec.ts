/**
 * End-to-End Authentication Flow Tests
 *
 * Tests the complete user authentication flow using Playwright:
 * - User registration
 * - User login
 * - Protected route access
 * - User logout
 *
 * These tests run against a live Next.js application with Better Auth.
 */

import { expect, test, type Page } from '@playwright/test';

/**
 * Test utilities
 */

/**
 * Generate a unique email for testing to avoid conflicts
 *
 * @returns string - Unique email address
 */
function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `test-${timestamp}-${random}@example.com`;
}

const TEST_PASSWORD = 'testpassword123';
const TEST_NAME = 'Test User';

/**
 * Clear all cookies and local storage before each test
 *
 * @param page - Playwright page object
 * @returns Promise<void>
 */
async function clearAuth(page: Page): Promise<void> {
  // Clear cookies
  await page.context().clearCookies();

  // Navigate to the app first to ensure we have access to localStorage
  // Then clear it safely with error handling
  try {
    await page.goto('/');
    await page.evaluate(() => {
      try {
        localStorage.clear();
        sessionStorage.clear();
      } catch (e) {
        // Ignore errors if localStorage is not accessible
        console.log(e);
      }
    });
  } catch (e) {
    // If navigation or evaluation fails, just continue
    // Clearing cookies is usually sufficient for auth tests
    console.log('Error during clearAuth:', e);
  }
}

/**
 * Test Suite: Authentication Flow
 */
test.describe('Authentication Flow', () => {
  /**
   * Test 1: Complete Registration Flow
   *
   * Acceptance Criteria:
   * - User can navigate to registration page
   * - Form validates required fields
   * - User can register with valid credentials
   * - After registration, user is redirected to dashboard
   * - User session is established (auth cookie exists)
   */
  test('should complete registration flow successfully', async ({ page }) => {
    // Arrange: Clear any existing auth state
    await clearAuth(page);

    // Generate unique email for this test
    const testEmail = generateTestEmail();

    // Act: Navigate to registration page
    await page.goto('/register');

    // Assert: Registration page loads correctly
    await expect(page).toHaveURL('/register');
    await expect(page.getByRole('heading', { name: /create account|register/i })).toBeVisible();

    // Act: Fill in registration form
    await page.getByLabel(/name/i).fill(TEST_NAME);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);
    await page.getByLabel(/confirm password/i).fill(TEST_PASSWORD);

    // Act: Submit the form
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Assert: User is redirected to dashboard after successful registration
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Assert: Dashboard content is visible (sidebar, header, or welcome message)
    // Adjust selector based on your dashboard layout
    await expect(page.locator('text=Task').or(page.locator('text=Dashboard'))).toBeVisible({
      timeout: 5000,
    });

    // Assert: Auth cookie is set
    const cookies = await page.context().cookies();
    const authCookie = cookies.find((cookie) => cookie.name.includes('better-auth.session_token'));
    expect(authCookie).toBeDefined();
    expect(authCookie?.value).toBeTruthy();
  });

  /**
   * Test 2: Registration Form Validation
   *
   * Acceptance Criteria:
   * - Form shows error when email is missing
   * - Form shows error when password is too short
   * - Form shows error when passwords don't match
   */
  test('should validate registration form fields', async ({ page }) => {
    // Arrange
    await clearAuth(page);
    await page.goto('/register');

    // Test Case 1: Submit with missing fields
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Assert: Validation errors appear (browser validation or custom)
    // This will trigger HTML5 validation since fields are required
    await expect(page.getByLabel(/name/i)).toBeFocused();

    // Test Case 2: Password too short
    await page.getByLabel(/name/i).fill(TEST_NAME);
    await page.getByLabel(/email/i).fill(generateTestEmail());
    await page.getByLabel(/^password$/i).fill('short');
    await page.getByLabel(/confirm password/i).fill('short');
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Assert: Error message about password length
    await expect(page.locator('text=/password must be at least 8 characters/i')).toBeVisible({
      timeout: 3000,
    });

    // Test Case 3: Passwords don't match
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);
    await page.getByLabel(/confirm password/i).fill('different123');
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Assert: Error message about password mismatch
    await expect(page.locator('text=/passwords do not match/i')).toBeVisible({ timeout: 3000 });
  });

  /**
   * Test 3: Complete Login Flow
   *
   * Acceptance Criteria:
   * - User can navigate to login page
   * - User can log in with valid credentials
   * - After login, user is redirected to dashboard
   * - User session is established
   */
  test('should complete login flow successfully', async ({ page }) => {
    // Arrange: First register a user
    await clearAuth(page);
    const testEmail = generateTestEmail();

    // Register user
    await page.goto('/register');
    await page.getByLabel(/name/i).fill(TEST_NAME);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);
    await page.getByLabel(/confirm password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Wait for registration to complete
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Act: Log out (click logout button)
    const logoutButton = page.getByRole('button', { name: /log out|logout/i });
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await expect(page).toHaveURL('/login', { timeout: 5000 });
    } else {
      // Manually clear cookies if logout button not found
      await clearAuth(page);
      await page.goto('/login');
    }

    // Act: Navigate to login page
    await page.goto('/login');
    await expect(page).toHaveURL('/login');

    // Assert: Login page loads correctly
    await expect(page.getByRole('heading', { name: /log in|sign in|login/i })).toBeVisible();

    // Act: Fill in login form
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);

    // Act: Submit the form
    await page.getByRole('button', { name: /log in|sign in|login/i }).click();

    // Assert: User is redirected to dashboard after successful login
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Assert: Auth cookie is set
    const cookies = await page.context().cookies();
    const authCookie = cookies.find((cookie) => cookie.name.includes('better-auth.session_token'));
    expect(authCookie).toBeDefined();
  });

  /**
   * Test 4: Login Form Validation
   *
   * Acceptance Criteria:
   * - Form shows error when credentials are invalid
   * - Form validates required fields
   */
  test('should validate login form and handle errors', async ({ page }) => {
    // Arrange
    await clearAuth(page);
    await page.goto('/login');

    // Test Case 1: Submit with invalid credentials
    await page.getByLabel(/email/i).fill('wrong@example.com');
    await page.getByLabel(/^password$/i).fill('wrongpassword');
    await page.getByRole('button', { name: /log in|sign in|login/i }).click();

    // Assert: Error message appears
    await expect(page.locator('text=/invalid|incorrect|failed/i')).toBeVisible({ timeout: 5000 });

    // Test Case 2: Submit with empty fields
    await page.getByLabel(/email/i).clear();
    await page.getByLabel(/^password$/i).clear();
    await page.getByRole('button', { name: /log in|sign in|login/i }).click();

    // Assert: Validation error or focus on email field
    await expect(page.getByLabel(/email/i)).toBeFocused();
  });

  /**
   * Test 5: Protected Route Access
   *
   * Acceptance Criteria:
   * - Unauthenticated users are redirected to /login when accessing /
   * - Authenticated users can access /
   * - Login page redirects authenticated users to /
   */
  test('should protect routes based on authentication', async ({ page }) => {
    // Test Case 1: Unauthenticated user accessing protected route
    await clearAuth(page);
    await page.goto('/');

    // Assert: Redirected to login page
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });

    // Test Case 2: Authenticated user accessing login page
    // First, register and login
    const testEmail = generateTestEmail();
    await page.goto('/register');
    await page.getByLabel(/name/i).fill(TEST_NAME);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);
    await page.getByLabel(/confirm password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Wait for redirect to dashboard
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Act: Try to access login page while authenticated
    await page.goto('/login');

    // Assert: Redirected back to dashboard
    await expect(page).toHaveURL('/', { timeout: 5000 });

    // Test Case 3: Authenticated user can access protected route
    await page.goto('/');
    await expect(page).toHaveURL('/');
    // Dashboard content should be visible
    await expect(page.locator('text=Task').or(page.locator('text=Dashboard'))).toBeVisible();
  });

  /**
   * Test 6: Complete Logout Flow
   *
   * Acceptance Criteria:
   * - User can log out
   * - After logout, user is redirected to /login
   * - Auth cookie is cleared
   * - User cannot access protected routes after logout
   */
  test('should complete logout flow successfully', async ({ page }) => {
    // Arrange: Register and login a user
    await clearAuth(page);
    const testEmail = generateTestEmail();

    await page.goto('/register');
    await page.getByLabel(/name/i).fill(TEST_NAME);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);
    await page.getByLabel(/confirm password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Wait for successful login
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Assert: User is logged in (auth cookie exists)
    let cookies = await page.context().cookies();
    let authCookie = cookies.find((cookie) => cookie.name.includes('better-auth.session_token'));
    expect(authCookie).toBeDefined();

    // Act: Click logout button
    const logoutButton = page.getByRole('button', { name: /log out|logout/i });
    await expect(logoutButton).toBeVisible();
    await logoutButton.click();

    // Assert: Redirected to login page
    await expect(page).toHaveURL('/login', { timeout: 5000 });

    // Assert: Auth cookie is cleared or expired
    cookies = await page.context().cookies();
    authCookie = cookies.find((cookie) => cookie.name.includes('better-auth.session_token'));
    // Cookie should be removed or have empty value
    expect(!authCookie || !authCookie.value).toBeTruthy();

    // Assert: Cannot access protected routes
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
  });

  /**
   * Test 7: Password Visibility Toggle
   *
   * Acceptance Criteria:
   * - Password field is hidden by default
   * - Clicking toggle shows password
   * - Clicking toggle again hides password
   */
  test('should toggle password visibility on login form', async ({ page }) => {
    // Arrange
    await clearAuth(page);
    await page.goto('/login');

    const passwordInput = page.getByLabel(/^password$/i);
    const toggleButton = page.getByRole('button', {
      name: /show password|hide password|toggle/i,
    });

    // Assert: Password is hidden by default
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Act: Click toggle to show password
    await toggleButton.click();

    // Assert: Password is now visible
    await expect(passwordInput).toHaveAttribute('type', 'text');

    // Act: Click toggle to hide password again
    await toggleButton.click();

    // Assert: Password is hidden again
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  /**
   * Test 8: JWT Token Persistence After Page Refresh
   *
   * Acceptance Criteria (from T032A):
   * - JWT token is stored in localStorage after login
   * - JWT token persists across page refreshes
   * - User remains authenticated after page refresh
   * - JWT token is automatically refreshed if missing but session exists
   *
   * This test validates the fix from the forensic audit:
   * - JWT must be stored in localStorage (NOT in-memory)
   * - JWT must survive page refresh
   * - useAuthInit hook must refresh JWT on page load if missing
   */
  test('should persist JWT token across page refresh', async ({ page }) => {
    // Arrange: Register and login a user
    await clearAuth(page);
    const testEmail = generateTestEmail();

    await page.goto('/register');
    await page.getByLabel(/name/i).fill(TEST_NAME);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(TEST_PASSWORD);
    await page.getByLabel(/confirm password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /register|sign up/i }).click();

    // Wait for successful registration and redirect to dashboard
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Assert: JWT token exists in localStorage
    const jwtBefore = await page.evaluate(() => {
      return localStorage.getItem('jwt_token');
    });
    expect(jwtBefore).toBeTruthy();
    expect(jwtBefore).not.toBe('null');
    expect(jwtBefore).not.toBe('undefined');

    // Assert: Better Auth session cookie exists
    let cookies = await page.context().cookies();
    let authCookie = cookies.find((cookie) => cookie.name.includes('better-auth.session_token'));
    expect(authCookie).toBeDefined();
    expect(authCookie?.value).toBeTruthy();

    // Act: Reload the page (simulates user hitting F5 or closing/reopening tab)
    await page.reload();

    // Wait for page to load completely
    await expect(page).toHaveURL('/', { timeout: 10000 });

    // Assert: JWT token STILL exists in localStorage after refresh
    const jwtAfter = await page.evaluate(() => {
      return localStorage.getItem('jwt_token');
    });
    expect(jwtAfter).toBeTruthy();
    expect(jwtAfter).toBe(jwtBefore); // Should be the same token
    expect(jwtAfter).not.toBe('null');
    expect(jwtAfter).not.toBe('undefined');

    // Assert: User is still authenticated (can see dashboard content)
    await expect(page.locator('text=Task').or(page.locator('text=Dashboard'))).toBeVisible({
      timeout: 5000,
    });

    // Assert: Session cookie still exists
    cookies = await page.context().cookies();
    authCookie = cookies.find((cookie) => cookie.name.includes('better-auth.session_token'));
    expect(authCookie).toBeDefined();
    expect(authCookie?.value).toBeTruthy();

    // Test Case 2: JWT refresh when missing but session exists
    // This tests the useAuthInit hook functionality

    // Act: Manually clear JWT from localStorage but keep session cookie
    await page.evaluate(() => {
      localStorage.removeItem('jwt_token');
    });

    // Verify JWT is gone
    const jwtCleared = await page.evaluate(() => {
      return localStorage.getItem('jwt_token');
    });
    expect(jwtCleared).toBeNull();

    // Act: Reload the page (useAuthInit should restore JWT from session)
    await page.reload();

    // Wait for page to load and useAuthInit to run
    await expect(page).toHaveURL('/', { timeout: 10000 });
    await page.waitForTimeout(1000); // Give useAuthInit time to run

    // Assert: JWT token is automatically restored by useAuthInit hook
    const jwtRestored = await page.evaluate(() => {
      return localStorage.getItem('jwt_token');
    });
    expect(jwtRestored).toBeTruthy();
    expect(jwtRestored).not.toBe('null');
    expect(jwtRestored).not.toBe('undefined');

    // Assert: User can still access protected content
    await expect(page.locator('text=Task').or(page.locator('text=Dashboard'))).toBeVisible({
      timeout: 5000,
    });
  });
});
