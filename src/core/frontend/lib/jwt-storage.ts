/**
 * JWT Token Storage Utility
 *
 * This utility manages JWT token storage for FastAPI authentication.
 *
 * Security Considerations:
 * - localStorage: Persists across page refreshes (REQUIRED for UX), vulnerable to XSS attacks
 * - Mitigation: Short-lived tokens (24 hours), Content Security Policy (CSP) headers
 *
 * Implementation Decision (from ADR-006):
 * Uses localStorage to persist JWT tokens across page refreshes.
 * This is necessary because Better Auth session cookie handles frontend routing,
 * but the JWT token is needed for backend API authentication.
 *
 * XSS Risk Accepted:
 * - Trade-off for persistent authentication
 * - Mitigated by 24-hour token expiration
 * - Mitigated by CSP headers
 * - Better UX than re-authentication on every page load
 */

/**
 * localStorage key for JWT token
 */
const JWT_STORAGE_KEY = 'jwt_token';

/**
 * Check if we're in a browser environment (not SSR)
 *
 * @returns True if window.localStorage is available
 */
function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

/**
 * Retrieve the current JWT token from localStorage
 *
 * @returns The JWT token string or null if not authenticated
 */
export function getJwtToken(): string | null {
  if (!isBrowser()) {
    return null;
  }

  try {
    return localStorage.getItem(JWT_STORAGE_KEY);
  } catch (error) {
    console.error('Error reading JWT token from localStorage:', error);
    return null;
  }
}

/**
 * Store a JWT token in localStorage
 *
 * @param token - The JWT token string to store
 */
export function setJwtToken(token: string): void {
  if (!isBrowser()) {
    console.warn('Cannot set JWT token: not in browser environment');
    return;
  }

  try {
    localStorage.setItem(JWT_STORAGE_KEY, token);
  } catch (error) {
    console.error('Error storing JWT token in localStorage:', error);
  }
}

/**
 * Clear the stored JWT token from localStorage (logout)
 */
export function clearJwtToken(): void {
  if (!isBrowser()) {
    return;
  }

  try {
    alert('clearing JWT');
    localStorage.removeItem(JWT_STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing JWT token from localStorage:', error);
  }
}

/**
 * Check if a JWT token is currently stored in localStorage
 *
 * @returns True if a token is stored, false otherwise
 */
export function hasJwtToken(): boolean {
  return getJwtToken() !== null;
}
