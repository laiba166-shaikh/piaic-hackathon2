"use client";

import PasswordToggle from "@/components/auth/PasswordToggle";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { authClient } from "@/lib/auth-client";
import { setJwtToken } from "@/lib/jwt-storage";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

export default function RegisterForm() {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    setError(null);

    if (!firstName.trim()) {
      setError("First name is required");
      return;
    }
    if (!email.trim()) {
      setError("Email is required");
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

    setIsLoading(true);
    try {
      const name = [firstName.trim(), lastName.trim()].filter(Boolean).join(" ");
      const result = await authClient.signUp.email({
        email: email.trim(),
        password: password.trim(),
        name,
      });

      if (result.error) {
        setError(result.error.message || "Registration failed. Please try again.");
        setIsLoading(false);
        return;
      }

      const tokenResult = await authClient.token();
      if (tokenResult.error || !tokenResult.data) {
        setError("Registration succeeded but failed to retrieve access token. Please log in.");
        setIsLoading(false);
        return;
      }

      setJwtToken(tokenResult.data.token);
      router.push("/");
    } catch {
      setError("Unable to connect. Please try again.");
      setIsLoading(false);
    }
  }

  const inputClass =
    "w-full px-4 py-3 border border-border bg-card text-foreground rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent placeholder:text-muted-foreground transition-colors";
  const labelClass = "block text-xs font-semibold uppercase tracking-wide text-foreground mb-1.5";

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <ErrorMessage message={error} />

      {/* First + Last Name */}
      <div className="flex gap-4">
        <div className="flex-1">
          <label htmlFor="firstName" className={labelClass}>First Name</label>
          <input
            id="firstName"
            type="text"
            required
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder="Alexica"
            disabled={isLoading}
            className={inputClass}
          />
        </div>
        <div className="flex-1">
          <label htmlFor="lastName" className={labelClass}>Last Name</label>
          <input
            id="lastName"
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            placeholder="Smith"
            disabled={isLoading}
            className={inputClass}
          />
        </div>
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className={labelClass}>Email Address</label>
        <input
          id="email"
          name="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          disabled={isLoading}
          className={inputClass}
        />
      </div>

      {/* Password */}
      <div>
        <label htmlFor="password" className={labelClass}>Password</label>
        <div className="relative">
          <input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Create a strong password"
            disabled={isLoading}
            minLength={8}
            className={`${inputClass} pr-10`}
          />
          <PasswordToggle isVisible={showPassword} onToggle={() => setShowPassword((p) => !p)} />
        </div>
      </div>

      {/* Confirm Password */}
      <div>
        <label htmlFor="confirmPassword" className={labelClass}>Confirm Password</label>
        <div className="relative">
          <input
            id="confirmPassword"
            name="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Repeat your password"
            disabled={isLoading}
            className={`${inputClass} pr-10`}
          />
          <PasswordToggle isVisible={showConfirmPassword} onToggle={() => setShowConfirmPassword((p) => !p)} />
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-card border border-border text-foreground font-bold py-3 px-4 rounded-lg hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
      >
        {isLoading ? "Creating account..." : "Create my account"}
      </button>
    </form>
  );
}
