/**
 * useAuthInit Hook
 *
 * This hook handles JWT token initialization and refresh on page load.
 * It ensures that the JWT token is synchronized with the Better Auth session.
 *
 * Workflow:
 * 1. On component mount, check Better Auth session status
 * 2. If session exists but no JWT in localStorage → retrieve JWT from authClient.token()
 * 3. If no session but JWT exists in localStorage → clear stale JWT
 * 4. This prevents the state where user appears logged in (session cookie)
 *    but gets 401 errors from backend (missing JWT)
 *
 * Usage:
 * ```tsx
 * // In root layout or main app component
 * import { useAuthInit } from '@/hooks/useAuthInit';
 *
 * export default function RootLayout({ children }) {
 *   useAuthInit(); // Initialize auth on app load
 *   return <html>{children}</html>;
 * }
 * ```
 */

"use client";

import { authClient } from "@/lib/auth-client";
import { getJwtToken, setJwtToken, clearJwtToken } from "@/lib/jwt-storage";
import { useEffect, useState } from "react";

/**
 * Hook to initialize and synchronize JWT token with Better Auth session
 *
 * @returns Object with loading state
 */
export function useAuthInit() {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    async function initializeAuth() {
      try {
        // Step 1: Check Better Auth session status
        const session = await authClient.getSession();
        const jwt = getJwtToken();

        // Step 2: Session exists but no JWT → retrieve JWT
        if (session.data && !jwt) {
          console.log('[useAuthInit] Session exists but JWT missing - retrieving token');
          const tokenResult = await authClient.token();

          if (tokenResult.data && tokenResult.data.token) {
            setJwtToken(tokenResult.data.token);
            console.log('[useAuthInit] JWT token retrieved and stored');
          } else {
            console.warn('[useAuthInit] Failed to retrieve JWT token despite active session');
          }
        }

        // Step 3: No session but JWT exists → clear stale JWT
        if (!session.data && jwt) {
          console.log('[useAuthInit] No session but JWT exists - clearing stale token');
          clearJwtToken();
        }

        // Step 4: Both exist or both don't exist → normal state
        if ((session.data && jwt) || (!session.data && !jwt)) {
          console.log('[useAuthInit] Auth state synchronized');
        }

        setIsInitialized(true);
      } catch (error) {
        console.error('[useAuthInit] Error initializing auth:', error);
        setIsInitialized(true); // Set initialized even on error to prevent blocking
      }
    }

    initializeAuth();
  }, []); // Run once on mount

  return { isInitialized };
}
