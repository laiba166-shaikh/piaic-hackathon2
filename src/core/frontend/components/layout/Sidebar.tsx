"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Sidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <aside className="w-60 bg-paper-white border-r border-sepia-brown shadow-journal h-screen">
      <div className="p-6">
        <h2 className="text-2xl font-serif text-ink-black mb-8">
          Todo
        </h2>

        <nav className="space-y-2">
          <Link
            href="/"
            className={`block px-4 py-2 rounded-lg transition-colors ${
              isActive("/")
                ? "bg-vintage-blue text-paper-white"
                : "text-ink-black hover:bg-sepia-brown/10"
            }`}
          >
            Dashboard
          </Link>

          <Link
            href="/tasks"
            className={`block px-4 py-2 rounded-lg transition-colors ${
              isActive("/tasks")
                ? "bg-vintage-blue text-paper-white"
                : "text-ink-black hover:bg-sepia-brown/10"
            }`}
          >
            All Tasks
          </Link>
        </nav>
      </div>
    </aside>
  );
}
