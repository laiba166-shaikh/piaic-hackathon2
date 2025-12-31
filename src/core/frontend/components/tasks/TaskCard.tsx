/**
 * TaskCard Component
 *
 * Displays a single task with a paper-like journal aesthetic.
 */

import { Task } from "@/types/task";

interface TaskCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

export function TaskCard({ task, onEdit, onDelete }: TaskCardProps) {
  const formattedDate = new Date(task.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <div
      className={`bg-white rounded-lg border border-sepia p-6 shadow-sm hover:shadow-md transition-shadow ${
        task.completed ? "opacity-75" : ""
      }`}
    >
      <div className="flex justify-between items-start mb-3">
        <h3
          className={`text-xl font-serif font-medium text-ink ${
            task.completed ? "line-through text-ink/60" : ""
          }`}
        >
          {task.title}
        </h3>

        <div className="flex gap-2 ml-4">
          {onEdit && (
            <button
              onClick={() => onEdit(task)}
              className="text-vintage hover:text-vintage/80 transition-colors"
              aria-label="Edit"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
          )}

          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              className="text-red-600 hover:text-red-700 transition-colors"
              aria-label="Delete"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {task.description && (
        <p className="text-ink/80 leading-relaxed mb-4">{task.description}</p>
      )}

      <div className="flex justify-between items-center pt-3 border-t border-sepia/30">
        <span className="text-sm text-ink/50 font-mono">{formattedDate}</span>

        {task.completed && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <svg
              className="w-3 h-3 mr-1"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            Completed
          </span>
        )}
      </div>
    </div>
  );
}
