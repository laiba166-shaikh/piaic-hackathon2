"use client";

import PasswordToggle from "@/components/auth/PasswordToggle";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { authClient } from "@/lib/auth-client";
import { setJwtToken } from "@/lib/jwt-storage";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

export default function LoginForm() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    e.stopPropagation();
    setError(null);

    if (!email.trim()) {
      setError("Email is required");
      return;
    }
    if (!password.trim()) {
      setError("Password is required");
      return;
    }

    setIsLoading(true);
    try {
      const result = await authClient.signIn.email({
        email: email.trim(),
        password: password.trim(),
      });

      if (result.error) {
        setError(result.error.message || "Invalid email or password");
        setIsLoading(false);
        return;
      }

      const tokenResult = await authClient.token();
      if (tokenResult.error || !tokenResult.data) {
        setError("Authentication succeeded but failed to retrieve access token. Please try again.");
        setIsLoading(false);
        return;
      }

      setJwtToken(tokenResult.data.token);
      setIsLoading(false);
      router.push("/");
    } catch {
      setError("Unable to connect. Please try again.");
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-5">
      <ErrorMessage message={error} />

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-wide text-foreground mb-1.5">
          Email Address
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          disabled={isLoading}
          className="w-full px-4 py-3 border border-border bg-card text-foreground rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent placeholder:text-muted-foreground transition-colors"
        />
      </div>

      {/* Password */}
      <div>
        <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wide text-foreground mb-1.5">
          Password
        </label>
        <div className="relative">
          <input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            disabled={isLoading}
            className="w-full px-4 py-3 pr-10 border border-border bg-card text-foreground rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent placeholder:text-muted-foreground transition-colors"
          />
          <PasswordToggle isVisible={showPassword} onToggle={() => setShowPassword((p) => !p)} />
        </div>
        <div className="text-right mt-1">
          <span className="text-sm text-muted-foreground cursor-default">Forgot password?</span>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-card border border-border text-foreground font-bold py-3 px-4 rounded-lg hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
      >
        {isLoading ? "Signing in..." : "Sign in to Task Mate"}
      </button>
    </form>
  );
}
