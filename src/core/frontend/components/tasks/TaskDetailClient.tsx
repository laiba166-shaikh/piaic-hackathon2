"use client";

/**
 * TaskDetailClient Component
 *
 * Client component for displaying and managing a single task.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Task, TaskUpdate } from "@/types/task";
import { TaskForm } from "./TaskForm";
import { Modal } from "../ui/Modal";

interface TaskDetailClientProps {
  taskId: number;
}

export function TaskDetailClient({ taskId }: TaskDetailClientProps) {
  const router = useRouter();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  useEffect(() => {
    loadTask();
  }, [taskId]);

  async function loadTask() {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getTask(taskId);
      setTask(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load task"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleUpdateTask(taskData: TaskUpdate) {
    try {
      const updatedTask = await api.updateTask(taskId, taskData);
      setTask(updatedTask);
      setIsEditModalOpen(false);
    } catch (err) {
      throw err; // Let form handle the error
    }
  }

  async function handleDeleteTask() {
    try {
      await api.deleteTask(taskId);
      router.push("/tasks");
    } catch (err) {
      alert(
        err instanceof Error ? err.message : "Failed to delete task"
      );
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-sepia p-8 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>
    );
  }

  // Error state
  if (error || !task) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-8">
        <h2 className="text-xl font-serif font-bold text-red-900 mb-2">
          Error Loading Task
        </h2>
        <p className="text-red-700 mb-4">
          {error || "Task not found"}
        </p>
        <button
          onClick={() => router.push("/tasks")}
          className="px-4 py-2 bg-vintage text-white rounded-lg hover:bg-vintage/90 transition-colors"
        >
          Back to Tasks
        </button>
      </div>
    );
  }

  const formattedDate = new Date(task.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const updatedDate = new Date(task.updated_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <>
      {/* Back button */}
      <button
        onClick={() => router.push("/tasks")}
        className="flex items-center text-vintage hover:text-vintage/80 transition-colors mb-6"
      >
        <svg
          className="w-5 h-5 mr-2"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        Back to Tasks
      </button>

      {/* Task content */}
      <div className="bg-white rounded-lg border border-sepia shadow-md overflow-hidden">
        {/* Header */}
        <div className="p-8 border-b border-sepia/30">
          <div className="flex justify-between items-start mb-4">
            <h1
              className={`text-3xl font-serif font-bold text-ink ${
                task.completed ? "line-through text-ink/60" : ""
              }`}
            >
              {task.title}
            </h1>

            {task.completed && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <svg
                  className="w-4 h-4 mr-1"
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

          <div className="flex gap-3">
            <button
              onClick={() => setIsEditModalOpen(true)}
              className="px-4 py-2 bg-vintage text-white rounded-lg hover:bg-vintage/90 transition-colors"
            >
              Edit Task
            </button>
            <button
              onClick={() => setIsDeleteModalOpen(true)}
              className="px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              Delete Task
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-8">
          {task.description ? (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-ink/60 uppercase tracking-wider mb-2">
                Description
              </h2>
              <p className="text-ink/80 leading-relaxed whitespace-pre-wrap">
                {task.description}
              </p>
            </div>
          ) : (
            <p className="text-ink/50 italic mb-6">
              No description provided.
            </p>
          )}

          <div className="grid grid-cols-2 gap-6 pt-6 border-t border-sepia/30">
            <div>
              <h3 className="text-sm font-medium text-ink/60 uppercase tracking-wider mb-1">
                Created
              </h3>
              <p className="text-ink font-mono text-sm">{formattedDate}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-ink/60 uppercase tracking-wider mb-1">
                Last Updated
              </h3>
              <p className="text-ink font-mono text-sm">{updatedDate}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Task"
      >
        <TaskForm
          onSubmit={handleUpdateTask}
          onCancel={() => setIsEditModalOpen(false)}
          initialData={{
            title: task.title,
            description: task.description || "",
          }}
          mode="edit"
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Task"
      >
        <div className="space-y-4">
          <p className="text-ink/80">
            Are you sure you want to delete this task? This action cannot be
            undone.
          </p>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setIsDeleteModalOpen(false)}
              className="px-4 py-2 border border-sepia text-ink rounded-lg hover:bg-paper-dark transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteTask}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
