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
}: ErrorMessageProps): React.JSX.Element | null {
  if (!message) return null;

  return (
    <div
      role="alert"
      className={`bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-lg text-sm ${className}`}
    >
      {message}
    </div>
  );
}
