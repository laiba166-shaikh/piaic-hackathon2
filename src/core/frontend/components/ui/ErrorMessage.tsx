/**
 * ErrorMessage Component
 *
 * Displays user-friendly error messages with journal theme styling.
 * Used across authentication forms and other UI components.
 */

interface ErrorMessageProps {
  message: string | null | undefined;
  className?: string;
}

/**
 * Display an error message with consistent styling
 *
 * @param message - The error message to display (null/undefined = hidden)
 * @param className - Optional additional CSS classes
 * @returns JSX.Element or null if no message
 */
export default function ErrorMessage({
  message,
  className = "",
}: ErrorMessageProps): JSX.Element | null {
  if (!message) return null;

  return (
    <div
      role="alert"
      className={`bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md text-sm ${className}`}
    >
      {message}
    </div>
  );
}
