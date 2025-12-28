/**
 * JWT Token Storage Utility
 *
 * This utility manages JWT token storage for FastAPI authentication.
 *
 * Security Considerations:
 * - In-memory storage: Most secure, lost on page refresh
 * - localStorage: Survives refresh, vulnerable to XSS attacks
 *
 * Current implementation uses in-memory storage for maximum security.
 * For production with persistent login, consider using refresh tokens
 * stored in httpOnly cookies with short-lived access tokens in memory.
 */

/**
 * In-memory JWT token storage
 * This is cleared when the page is refreshed or closed
 */
let jwtToken: string | null = null;

/**
 * Retrieve the current JWT token
 *
 * @returns The JWT token string or null if not authenticated
 */
export function getJwtToken(): string | null {
  return jwtToken;
}

/**
 * Store a JWT token
 *
 * @param token - The JWT token string to store, or null to clear
 */
export function setJwtToken(token: string | null): void {
  jwtToken = token;
}

/**
 * Clear the stored JWT token (logout)
 */
export function clearJwtToken(): void {
  jwtToken = null;
}

/**
 * Check if a JWT token is currently stored
 *
 * @returns True if a token is stored, false otherwise
 */
export function hasJwtToken(): boolean {
  return jwtToken !== null;
}
