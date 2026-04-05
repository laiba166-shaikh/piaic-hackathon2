"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import { clearJwtToken } from "@/lib/jwt-storage";
import { ThemeToggle } from "@/components/layout/ThemeToggle";

export function Header() {
  const { data: session } = authClient.useSession();
  const userName = session?.user?.name ?? "";
  const userEmail = session?.user?.email ?? "";
  const initial = userName.charAt(0).toUpperCase() || userEmail.charAt(0).toUpperCase() || "U";
  const title = userName ? `${userName}'s Task Mate` : "Task Mate";

  const [open, setOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await authClient.signOut();
      clearJwtToken();
    } catch {
      clearJwtToken();
    } finally {
      router.push("/login");
    }
  }

  return (
    <header className="bg-background border-b border-border px-6 py-4 flex items-center justify-between">
      <span className="text-foreground font-semibold text-lg">{title}</span>

      <div className="flex items-center gap-2">
        <ThemeToggle />

        {/* Avatar + dropdown */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setOpen((p) => !p)}
            className="w-9 h-9 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-sm hover:opacity-90 transition-opacity focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            aria-label="User menu"
            aria-expanded={open}
          >
            {initial}
          </button>

          {open && (
            <div className="absolute right-0 mt-2 w-56 rounded-xl border border-border bg-card shadow-lg z-50 overflow-hidden">
              {/* User info */}
              <div className="px-4 py-3 border-b border-border">
                {userName && (
                  <p className="text-sm font-semibold text-foreground truncate">{userName}</p>
                )}
                <p className="text-xs text-muted-foreground truncate">{userEmail}</p>
              </div>

              {/* Logout */}
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm text-foreground hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                {isLoggingOut ? "Signing out..." : "Sign out"}
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
