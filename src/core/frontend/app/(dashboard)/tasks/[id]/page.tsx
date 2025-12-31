/**
 * Single Task Detail Page
 *
 * Displays details for a single task with edit and delete options.
 * Dynamic route: /tasks/[id]
 */

import Link from "next/link";
import { TaskDetailClient } from "@/components/tasks/TaskDetailClient";

interface TaskDetailPageProps {
  params: {
    id: string;
  };
}

export default function TaskDetailPage({ params }: TaskDetailPageProps) {
  const taskId = parseInt(params.id, 10);

  // Validate task ID
  if (isNaN(taskId) || taskId <= 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8">
          <h2 className="text-xl font-serif font-bold text-red-900 mb-2">
            Invalid Task ID
          </h2>
          <p className="text-red-700 mb-4">
            The task ID provided is not valid.
          </p>
          <Link
            href="/tasks"
            className="inline-block px-4 py-2 bg-vintage text-white rounded-lg hover:bg-vintage/90 transition-colors"
          >
            Back to Tasks
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <TaskDetailClient taskId={taskId} />
    </div>
  );
}
