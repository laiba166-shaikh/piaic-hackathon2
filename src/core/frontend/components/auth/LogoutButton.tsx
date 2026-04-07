/**
 * LogoutButton Component
 *
 * Button to sign out the current user and redirect to login page.
 * Uses Better Auth client to handle logout and clears JWT token.
 */

"use client";

import { authClient } from "@/lib/auth-client";
import { clearJwtToken } from "@/lib/jwt-storage";
import { useState } from "react";

/**
 * Logout button component
 *
 * @returns JSX.Element
 */
export default function LogoutButton() {
  const [isLoading, setIsLoading] = useState<boolean>(false);

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
      await authClient.signOut();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      clearJwtToken();
      setIsLoading(false);
      window.location.href = "/login";
    }
  }

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      aria-label="Sign out"
    >
      {isLoading ? "Signing out..." : "Sign Out"}
    </button>
  );
}
