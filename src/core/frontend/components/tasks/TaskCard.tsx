"use client";

import { useState } from "react";
import { Task } from "@/types/task";

interface TaskCardProps {
  task: Task;
  onToggle?: (taskId: number) => Promise<void>;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

export function TaskCard({ task, onToggle, onEdit, onDelete }: TaskCardProps) {
  const [toggling, setToggling] = useState(false);

  const formattedDate = new Date(task.created_at).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  async function handleToggle() {
    if (!onToggle || toggling) return;
    setToggling(true);
    try {
      await onToggle(task.id);
    } finally {
      setToggling(false);
    }
  }


  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      {/* Main row */}
      <div className="flex items-center gap-4 p-4">
        {/* Toggle circle */}
        <button
          onClick={handleToggle}
          disabled={toggling || !onToggle}
          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
          className={`w-8 h-8 rounded-full border-2 flex items-center justify-center shrink-0 transition-all
            ${task.completed
              ? "bg-accent/20 border-accent"
              : "border-border hover:border-accent"
            }
            ${toggling ? "opacity-50 cursor-wait" : onToggle ? "cursor-pointer" : "cursor-default"}
          `}
        >
          {task.completed && (
            <svg
              className="w-4 h-4 text-accent"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
          {toggling && !task.completed && (
            <div className="w-3 h-3 rounded-full border-2 border-accent border-t-transparent animate-spin" />
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p
            className={`text-base ${
              task.completed
                ? "line-through text-muted-foreground"
                : "text-foreground font-medium"
            }`}
          >
            {task.title}
          </p>
          <p className="text-sm text-muted-foreground mt-0.5">{formattedDate}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 shrink-0">
          {onEdit && (
            <button
              onClick={() => onEdit(task)}
              aria-label="Edit task"
              className="p-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:border-primary transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              aria-label="Delete task"
              className="p-2 rounded-lg border border-border text-muted-foreground hover:text-destructive hover:border-destructive transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Completed tag — bottom strip, only visible when done */}
      {task.completed && (
        <div className="px-4 py-2 border-t border-border bg-accent/5 flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5 text-accent shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-xs font-medium text-accent">Completed</span>
        </div>
      )}
    </div>
  );
}
