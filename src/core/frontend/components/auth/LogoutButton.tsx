/**
 * LogoutButton Component
 *
 * Button to sign out the current user and redirect to login page.
 * Uses Better Auth client to handle logout and clears JWT token.
 */

"use client";

import { authClient } from "@/lib/auth-client";
import { clearJwtToken } from "@/lib/jwt-storage";
import { useRouter } from "next/navigation";
import { useState } from "react";

/**
 * Logout button component
 *
 * @returns JSX.Element
 */
export default function LogoutButton() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const router = useRouter();

  /**
   * Handle logout action
   *
   * Signs out the user, clears JWT token, and redirects to login page.
   *
   * @returns Promise<void>
   */
  async function handleLogout(): Promise<void> {
    setIsLoading(true);

    try {
      // Sign out with Better Auth (clears session cookie)
      await authClient.signOut();

      // Clear JWT token from memory
      clearJwtToken();

      // Redirect to login page after successful logout
      router.push("/login");
    } catch (error) {
      // If logout fails, still clear token and redirect to login
      // (Better Auth clears cookies on client side)
      console.error("Logout error:", error);
      clearJwtToken();
      router.push("/login");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="px-4 py-2 text-sm font-medium text-ink hover:text-vintage transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      aria-label="Sign out"
    >
      {isLoading ? "Signing out..." : "Sign Out"}
    </button>
  );
}
