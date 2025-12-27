/**
 * PasswordToggle Component
 *
 * Button to toggle password visibility in password input fields.
 * Provides accessible show/hide functionality.
 */

"use client";

interface PasswordToggleProps {
  isVisible: boolean;
  onToggle: () => void;
  className?: string;
}

/**
 * Toggle button for password visibility
 *
 * @param isVisible - Whether password is currently visible
 * @param onToggle - Callback to toggle visibility
 * @param className - Optional additional CSS classes
 * @returns JSX.Element
 */
export default function PasswordToggle({
  isVisible,
  onToggle,
  className = "",
}: PasswordToggleProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={`absolute right-3 top-1/2 -translate-y-1/2 text-ink/60 hover:text-ink transition-colors ${className}`}
      aria-label={isVisible ? "Hide password" : "Show password"}
    >
      {isVisible ? (
        // Eye slash icon (hide)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-5 h-5"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
          />
        </svg>
      ) : (
        // Eye icon (show)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-5 h-5"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      )}
    </button>
  );
}
