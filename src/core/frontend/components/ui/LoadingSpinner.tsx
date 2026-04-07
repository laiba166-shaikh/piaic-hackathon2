/**
 * LoadingSpinner Component
 *
 * Displays a loading spinner for async operations.
 * Used in forms during API calls and page loading states.
 */

import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

/**
 * Display a loading spinner
 *
 * @param size - Size of the spinner (sm: 16px, md: 24px, lg: 32px)
 * @param className - Optional additional CSS classes
 * @returns JSX.Element
 */
export default function LoadingSpinner({
  size = "md",
  className = "",
}: LoadingSpinnerProps): React.JSX.Element {
  const sizeClasses = {
    sm: "w-4 h-4 border-2",
    md: "w-6 h-6 border-2",
    lg: "w-8 h-8 border-3",
  };

  return (
    <div
      className={`inline-block animate-spin rounded-full border-solid border-vintage border-t-transparent ${sizeClasses[size]} ${className}`}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}
