/**
 * RegisterForm Component
 *
 * User registration form with email/password authentication.
 * Includes password strength validation and confirmation matching.
 *
 * Features:
 * - Email validation
 * - Password strength indicator
 * - Password confirmation matching
 * - Auto-login after successful registration
 * - Loading states and error handling
 */

"use client";

import PasswordToggle from "@/components/auth/PasswordToggle";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

/**
 * RegisterForm component for new user registration
 *
 * @returns JSX.Element
 */
export default function RegisterForm() {
  // Form state
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [name, setName] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState<boolean>(false);

  // UI state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Router for navigation
  const router = useRouter();

  /**
   * Calculate password strength
   *
   * @param pwd - Password to evaluate
   * @returns "weak" | "medium" | "strong"
   */
  function getPasswordStrength(pwd: string): "weak" | "medium" | "strong" {
    if (pwd.length < 8) return "weak";
    if (pwd.length < 12) return "medium";
    return "strong";
  }

  const passwordStrength = getPasswordStrength(password);

  /**
   * Handle form submission
   *
   * @param e - Form event
   * @returns Promise<void>
   */
  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    setError(null);

    // Client-side validation
    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!name.trim()) {
      setError("Name is required");
      return;
    }

    if (!password.trim()) {
      setError("Password is required");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Call Better Auth sign up
    setIsLoading(true);
    console.log("Registering user:", { email, name });
    try {
      const result = await authClient.signUp.email({
        email: email.trim(),
        password: password.trim(),
        name: name.trim(),
      });

      // Check for errors from Better Auth
      if (result.error) {
        setError(
          result.error.message || "Registration failed. Please try again."
        );
        setIsLoading(false);
        return;
      }

      // Success: Wait a moment for session cookie to be set, then redirect
      // This prevents middleware from redirecting to /login before session is ready
      setTimeout(() => {
        router.push("/");
      }, 100);
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

  /**
   * Toggle confirm password visibility
   *
   * @returns void
   */
  function toggleConfirmPasswordVisibility(): void {
    setShowConfirmPassword((prev) => !prev);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-md">
      {/* Error Message */}
      <ErrorMessage message={error} />

      {/* Name Field */}
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-medium text-ink mb-1"
        >
          Name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          value={name}
          onChange={(e): void => setName(e.target.value)}
          className="w-full px-3 py-2 border border-sepia rounded-md bg-paper text-ink focus:outline-none focus:ring-2 focus:ring-vintage"
          placeholder="Your name"
          disabled={isLoading}
        />
      </div>

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
            placeholder="At least 8 characters"
            disabled={isLoading}
            minLength={8}
          />
          <PasswordToggle
            isVisible={showPassword}
            onToggle={togglePasswordVisibility}
          />
        </div>

        {/* Password Strength Indicator */}
        {password && (
          <div className="mt-1">
            <div className="flex items-center gap-2">
              <div className="flex-1 h-1 bg-sepia/20 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    passwordStrength === "weak"
                      ? "w-1/3 bg-red-500"
                      : passwordStrength === "medium"
                        ? "w-2/3 bg-yellow-500"
                        : "w-full bg-green-500"
                  }`}
                />
              </div>
              <span className="text-xs text-ink/60 capitalize">
                {passwordStrength}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Confirm Password Field */}
      <div>
        <label
          htmlFor="confirmPassword"
          className="block text-sm font-medium text-ink mb-1"
        >
          Confirm Password
        </label>
        <div className="relative">
          <input
            id="confirmPassword"
            name="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            required
            value={confirmPassword}
            onChange={(e): void => setConfirmPassword(e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-sepia rounded-md bg-paper text-ink focus:outline-none focus:ring-2 focus:ring-vintage"
            placeholder="Re-enter your password"
            disabled={isLoading}
          />
          <PasswordToggle
            isVisible={showConfirmPassword}
            onToggle={toggleConfirmPasswordVisibility}
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-vintage text-paper py-2 px-4 rounded-md font-medium hover:bg-vintage/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? "Creating account..." : "Create Account"}
      </button>
    </form>
  );
}
