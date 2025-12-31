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

'use client';

import { authClient } from '@/lib/auth-client';
import { clearJwtToken, getJwtToken, setJwtToken } from '@/lib/jwt-storage';
import { useEffect, useState } from 'react';

/**
 * Hook to initialize and synchronize JWT token with Better Auth session
 *
 * @returns Object with loading state
 */
export function useAuthInit() {
  const [isInitialized, setIsInitialized] = useState(false);
  async function initializeAuth() {
    console.log('[useAuthInit] ===== Starting auth initialization =====');
    try {
      // Step 1: Check Better Auth session status
      console.log('[useAuthInit] Step 1: Checking Better Auth session...');
      const session = await authClient.getSession();
      console.log('[useAuthInit] Session status:', session.data ? 'EXISTS' : 'NOT FOUND');

      const jwt = getJwtToken();
      console.log('[useAuthInit] JWT token in localStorage:', jwt ? 'EXISTS' : 'NOT FOUND');

      // Step 2: Session exists but no JWT → retrieve JWT
      if (session.data && !jwt) {
        console.log('[useAuthInit] Step 2: Session exists but JWT missing - retrieving token');
        const tokenResult = await authClient.token();

        if (tokenResult.data && tokenResult.data.token) {
          setJwtToken(tokenResult.data.token);
          console.log('[useAuthInit] JWT token retrieved and stored');
          console.log(
            '[useAuthInit] Token preview:',
            tokenResult.data.token.substring(0, 50) + '...'
          );
        } else {
          console.warn('[useAuthInit] Failed to retrieve JWT token despite active session');
          console.warn('[useAuthInit] Token result:', tokenResult);
        }
      }

      // Step 3: No session but JWT exists → clear stale JWT
      if (!session.data && jwt) {
        console.log('[useAuthInit] Step 3: No session but JWT exists - clearing stale token');
        clearJwtToken();
      }

      // Step 4: Both exist or both don't exist → normal state
      if (session.data && jwt) {
        console.log('[useAuthInit] Step 4: Auth state SYNCHRONIZED (session + JWT both exist)');
      } else if (!session.data && !jwt) {
        console.log('[useAuthInit] Step 4: No auth (session + JWT both missing) - user needs to login');
      }

      setIsInitialized(true);
      console.log('[useAuthInit] ===== Auth initialization COMPLETE =====');
    } catch (error) {
      console.error('[useAuthInit] ===== Auth initialization FAILED =====');
      console.error('[useAuthInit] Error:', error);
      setIsInitialized(true); // Set initialized even on error to prevent blocking
    }
  }

  useEffect(() => {
    initializeAuth();
  }, []); // Run once on mount

  return { isInitialized };
}
