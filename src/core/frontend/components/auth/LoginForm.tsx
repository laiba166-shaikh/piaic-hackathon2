/**
 * LoginForm Component (GREEN Phase - TDD)
 *
 * This component implements the login form to satisfy all test cases from T024.
 * It provides email/password authentication with Better Auth.
 *
 * Features:
 * - Client-side validation (email and password required)
 * - Password visibility toggle
 * - Loading states during API calls
 * - Error handling with user-friendly messages
 * - Redirect to home page on successful login
 */

"use client";

import PasswordToggle from "@/components/auth/PasswordToggle";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

/**
 * LoginForm component for user authentication
 */
export default function LoginForm() {
  // Form state
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);

  // UI state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Router for navigation
  const router = useRouter();

  /**
   * Handle form submission
   *
   * Validates inputs, calls Better Auth sign in, and redirects on success.
   *
   * @param e - Form event
   * @returns Promise<void>
   */
  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();

    // Prevent browser's built-in validation from interfering
    e.stopPropagation();

    setError(null);

    // Client-side validation (must happen even if HTML5 validation is bypassed)
    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!password.trim()) {
      setError("Password is required");
      return;
    }

    // Call Better Auth sign in
    setIsLoading(true);

    try {
      const result = await authClient.signIn.email({
        email: email.trim(),
        password: password.trim(),
      });

      // Check for errors from Better Auth
      if (result.error) {
        setError(result.error.message || "Invalid email or password");
        setIsLoading(false);
        return;
      }

      // Success: redirect to home page
      router.push("/");
    } catch (err) {
      // Handle network errors or unexpected errors
      setError("Unable to connect. Please try again.");
      setIsLoading(false);
    }
  }

  /**
   * Toggle password visibility
   *
   * @returns void
   */
  function togglePasswordVisibility(): void {
    setShowPassword((prev) => !prev);
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="space-y-4 w-full max-w-md"
    >
      {/* Error Message */}
      <ErrorMessage message={error} />

      {/* Email Field */}
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-ink mb-1"
        >
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          value={email}
          onChange={(e): void => setEmail(e.target.value)}
          className="w-full px-3 py-2 border border-sepia rounded-md bg-paper text-ink focus:outline-none focus:ring-2 focus:ring-vintage"
          placeholder="you@example.com"
          disabled={isLoading}
        />
      </div>

      {/* Password Field */}
      <div>
        <label
          htmlFor="password"
          className="block text-sm font-medium text-ink mb-1"
        >
          Password
        </label>
        <div className="relative">
          <input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            required
            value={password}
            onChange={(e): void => setPassword(e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-sepia rounded-md bg-paper text-ink focus:outline-none focus:ring-2 focus:ring-vintage"
            placeholder="Enter your password"
            disabled={isLoading}
          />
          <PasswordToggle
            isVisible={showPassword}
            onToggle={togglePasswordVisibility}
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-vintage text-paper py-2 px-4 rounded-md font-medium hover:bg-vintage/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? "Signing in..." : "Log in"}
      </button>
    </form>
  );
}
