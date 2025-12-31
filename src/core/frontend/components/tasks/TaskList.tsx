/**
 * TaskList Component
 *
 * Displays a list of tasks with loading, empty, and error states.
 */

import { Task } from "@/types/task";
import { TaskCard } from "./TaskCard";

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

export function TaskList({
  tasks,
  loading,
  error,
  onEdit,
  onDelete,
}: TaskListProps) {
  // Loading state
  if (loading) {
    return (
      <div data-testid="task-list-skeleton" className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-white rounded-lg border border-sepia p-6 animate-pulse"
          >
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <svg
          className="w-12 h-12 mx-auto mb-4 text-red-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <p className="text-red-800 font-medium mb-2">{error}</p>
        <p className="text-red-600 text-sm">
          {error.includes("Authentication")
            ? "Redirecting to login..."
            : "Please try refreshing the page."}
        </p>
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-sepia p-12 text-center">
        <div className="max-w-md mx-auto">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-sepia/50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h3 className="text-xl font-serif font-medium text-ink mb-2">
            No tasks yet
          </h3>
          <p className="text-ink/60">
            Get started by creating your first task. Click the &ldquo;Create Task&rdquo;
            button above to begin.
          </p>
        </div>
      </div>
    );
  }

  // Task list
  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
