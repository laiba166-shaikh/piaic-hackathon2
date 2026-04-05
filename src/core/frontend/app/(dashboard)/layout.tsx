/**
 * Dashboard Layout
 *
 * This layout is used for authenticated pages (dashboard, tasks, etc.)
 * It includes the Sidebar and Header components.
 *
 * Authentication Flow:
 * 1. AuthProvider initializes auth (checks session + syncs JWT token)
 * 2. Shows AuthLoadingScreen while initializing
 * 3. Once initialized, renders the dashboard UI with children
 *
 * This prevents child components (e.g., TasksPageClient) from making
 * API calls before JWT token is available, avoiding race conditions.
 */

"use client";

import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { AuthLoadingScreen } from "@/components/auth/AuthLoadingScreen";

/**
 * Dashboard Content Component
 * Renders dashboard UI only after auth is initialized
 */
function DashboardContent({ children }: { children: React.ReactNode }) {
  const { isInitialized } = useAuth();

  // Show loading screen while auth is initializing
  if (!isInitialized) {
    return <AuthLoadingScreen />;
  }

  // Render dashboard UI once auth is ready
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-hidden p-6">{children}</main>
      </div>
    </div>
  );
}

/**
 * Dashboard Layout Component
 * Wraps dashboard content with AuthProvider
 */
export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AuthProvider>
      <DashboardContent>{children}</DashboardContent>
    </AuthProvider>
  );
}
