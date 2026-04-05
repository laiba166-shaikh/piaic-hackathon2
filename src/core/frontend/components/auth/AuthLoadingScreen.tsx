/**
 * AuthLoadingScreen Component
 *
 * Displays a loading screen while authentication is being initialized.
 * Used by the dashboard layout to show feedback during JWT token sync.
 *
 * Design:
 * - Centered full-screen layout
 * - Animated spinner with journal theme colors
 * - Clear loading message
 */

"use client";

export function AuthLoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="text-center">
        {/* Animated Spinner */}
        <div className="relative w-16 h-16 mx-auto mb-6">
          <div className="absolute inset-0 border-4 border-border rounded-full"></div>
          <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>

        {/* Loading Text */}
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Verifying authentication...
        </h2>
        <p className="text-muted-foreground text-sm">
          Please wait while we secure your session
        </p>
      </div>
    </div>
  );
}
