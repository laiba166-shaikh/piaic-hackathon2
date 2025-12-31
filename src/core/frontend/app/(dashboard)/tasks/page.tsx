/**
 * Tasks Page
 *
 * Displays all tasks for the authenticated user with options to create, edit, and delete.
 * Renders within the dashboard layout with sidebar and header.
 */

import { TasksPageClient } from "@/components/tasks/TasksPageClient";

export default function TasksPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-serif font-bold text-ink mb-2">
          Want todos
        </h1>
        <p className="text-ink/70">
          Organize your thoughts and tasks in your personal journal
        </p>
      </div>

      <TasksPageClient />
    </div>
  );
}
