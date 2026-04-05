/**
 * AuthInitializer Component
 *
 * Client component wrapper for useAuthInit hook.
 * This component initializes authentication state on app load
 * and ensures JWT token is synchronized with Better Auth session.
 *
 * Usage:
 * ```tsx
 * // In root layout.tsx
 * import AuthInitializer from '@/components/auth/AuthInitializer';
 *
 * export default function RootLayout({ children }) {
 *   return (
 *     <html>
 *       <body>
 *         <AuthInitializer />
 *         {children}
 *       </body>
 *     </html>
 *   );
 * }
 * ```
 */

"use client";

import { useAuthInit } from "@/hooks/useAuthInit";

/**
 * AuthInitializer component
 * Runs auth initialization on mount (invisible to user)
 *
 * @returns null (no visual output)
 */
export default function AuthInitializer(): null {
  useAuthInit();
  return null;
}
