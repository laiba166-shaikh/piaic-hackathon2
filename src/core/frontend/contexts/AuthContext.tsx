/**
 * AuthContext
 *
 * Provides authentication state and initialization status to the application.
 * This context wraps protected routes to ensure auth is initialized before
 * rendering page content.
 *
 * Features:
 * - Manages auth initialization lifecycle
 * - Exposes isInitialized state for conditional rendering
 * - Synchronizes JWT token with Better Auth session
 *
 * Usage:
 * ```tsx
 * // In dashboard layout
 * import { AuthProvider, useAuth } from '@/contexts/AuthContext';
 *
 * export default function DashboardLayout({ children }) {
 *   return (
 *     <AuthProvider>
 *       {children}
 *     </AuthProvider>
 *   );
 * }
 *
 * // In any child component
 * function MyComponent() {
 *   const { isInitialized } = useAuth();
 *   // ... use auth state
 * }
 * ```
 */

"use client";

import { useAuthInit } from "@/hooks/useAuthInit";
import { createContext, useContext, ReactNode } from "react";

/**
 * Auth context value type
 */
interface AuthContextValue {
  /**
   * Whether auth initialization has completed
   * (session check + JWT token sync)
   */
  isInitialized: boolean;
}

/**
 * Auth context
 */
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * AuthProvider Props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider Component
 *
 * Initializes authentication state and provides it to child components.
 * Must be used as a wrapper for protected routes.
 *
 * @param props - Component props
 * @returns AuthProvider component
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const { isInitialized } = useAuthInit();

  return (
    <AuthContext.Provider value={{ isInitialized }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * useAuth Hook
 *
 * Hook to access auth context state.
 * Must be used within an AuthProvider.
 *
 * @returns Auth context value
 * @throws Error if used outside AuthProvider
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { isInitialized } = useAuth();
 *
 *   if (!isInitialized) {
 *     return <LoadingSpinner />;
 *   }
 *
 *   return <div>Content</div>;
 * }
 * ```
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
