"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Sidebar() {
  const pathname = usePathname();
  const isTasksActive = pathname === "/" || pathname.startsWith("/tasks");

  return (
    <aside className="w-[260px] bg-sidebar-background flex flex-col h-screen shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 p-5 pb-4">
        <div className="w-10 h-10 shrink-0">
          <svg width="40" height="40" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
            <rect width="96" height="96" rx="22" fill="hsl(var(--sidebar-accent))"/>
            <circle cx="48" cy="45" r="26" fill="none" stroke="hsl(var(--sidebar-foreground) / 0.4)" strokeWidth="3"/>
            <circle cx="48" cy="45" r="26" fill="none" stroke="hsl(var(--sidebar-foreground))" strokeWidth="3"
              strokeDasharray="40 123" strokeDashoffset="20" strokeLinecap="round"/>
            <polyline points="40,45 46,52 58,38" fill="none" stroke="hsl(var(--sidebar-foreground))"
              strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <span className="text-sidebar-foreground font-semibold text-xl">Task Mate</span>
      </div>

      {/* Nav */}
      <nav className="mt-4 px-3 space-y-1">
        {/* Tasks — active link */}
        <Link
          href="/"
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            isTasksActive
              ? "bg-sidebar-accent text-sidebar-foreground font-medium"
              : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50"
          }`}
        >
          <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
          </svg>
          <span>Tasks</span>
        </Link>

        {/* Task Mate AI — disabled */}
        <div
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-sidebar-foreground/30 cursor-not-allowed select-none"
          aria-disabled="true"
        >
          <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
          </svg>
          <span>Task Mate AI</span>
        </div>
      </nav>

      <div className="flex-1" />
    </aside>
  );
}
