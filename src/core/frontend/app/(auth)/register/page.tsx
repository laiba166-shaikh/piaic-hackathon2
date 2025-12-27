/**
 * Register Page
 *
 * Server Component that renders the registration form.
 * Public route accessible to unauthenticated users.
 */

import RegisterForm from "@/components/auth/RegisterForm";
import Link from "next/link";

/**
 * Register page component
 *
 * @returns JSX.Element
 */
export default function RegisterPage(){
  return (
    <div className="min-h-screen flex items-center justify-center bg-paper px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-ink font-heading mb-2">
            Create Account
          </h1>
          <p className="text-ink/70">Write it down. Get it done.</p>
        </div>

        {/* Registration Form */}
        <div className="bg-paper-light border border-sepia rounded-lg shadow-md p-8">
          <RegisterForm />

          {/* Login Link */}
          <div className="mt-6 text-center text-sm text-ink/70">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-vintage hover:underline font-medium"
            >
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
