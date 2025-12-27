/**
 * Login Page
 *
 * Server Component that renders the login form.
 * Public route accessible to unauthenticated users.
 */

import LoginForm from "@/components/auth/LoginForm";
import Link from "next/link";

/**
 * Login page component
 *
 * @returns JSX.Element
 */
export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-paper px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-ink font-heading mb-2">
          Sign in
          </h1>
          <p className="text-ink/70">Welcome back to your list</p>
        </div>

        {/* Login Form */}
        <div className="bg-paper-light border border-sepia rounded-lg shadow-md p-8">
          <LoginForm />

          {/* Register Link */}
          <div className="mt-6 text-center text-sm text-ink/70">
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              className="text-vintage hover:underline font-medium"
            >
              Create one
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
