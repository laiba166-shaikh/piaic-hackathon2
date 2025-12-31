"use client";

/**
 * TasksPageClient Component
 *
 * Client-side component that handles task data fetching, state management,
 * and user interactions for the tasks page.
 */

import { api } from "@/lib/api";
import { Task, TaskCreate, TaskUpdate } from "@/types/task";
import { useEffect, useState } from "react";
import { Modal } from "../ui/Modal";
import { TaskForm } from "./TaskForm";
import { TaskList } from "./TaskList";

export function TasksPageClient() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<number | null>(null);

  // Fetch tasks on mount
  // Note: Auth is guaranteed to be initialized because dashboard layout
  // waits for AuthProvider.isInitialized before rendering this component
  // Note: In development, React Strict Mode will call this effect twice.
  // This is expected behavior and only happens in development, not production.
  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    try {
      setLoading(true);
      setError(null);

      const data = await api.getTasks();
      setTasks(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load tasks";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTask(taskData: TaskCreate) {
    try {
      const newTask = await api.createTask(taskData);
      setTasks((prev) => [newTask, ...prev]);
      setIsCreateModalOpen(false);
    } catch (err) {
      throw err; // Let form handle the error
    }
  }

  async function handleUpdateTask(taskData: TaskUpdate) {
    if (!selectedTask) return;

    try {
      const updatedTask = await api.updateTask(selectedTask.id, taskData);
      setTasks((prev) =>
        prev.map((t) => (t.id === selectedTask.id ? updatedTask : t))
      );
      setIsEditModalOpen(false);
      setSelectedTask(null);
    } catch (err) {
      throw err; // Let form handle the error
    }
  }

  async function handleDeleteTask() {
    if (!taskToDelete) return;

    try {
      await api.deleteTask(taskToDelete);
      setTasks((prev) => prev.filter((t) => t.id !== taskToDelete));
      setIsDeleteModalOpen(false);
      setTaskToDelete(null);
    } catch (err) {
      alert(
        err instanceof Error ? err.message : "Failed to delete task"
      );
    }
  }

  function openEditModal(task: Task) {
    setSelectedTask(task);
    setIsEditModalOpen(true);
  }

  function openDeleteModal(taskId: number) {
    setTaskToDelete(taskId);
    setIsDeleteModalOpen(true);
  }

  return (
    <>
      <div className="mb-6">
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-vintage-blue text-white px-6 py-3 rounded-lg font-medium hover:bg-vintage-dark transition-colors shadow-md"
        >
          Create Task
        </button>
      </div>

      <TaskList
        tasks={tasks}
        loading={loading}
        error={error}
        onEdit={openEditModal}
        onDelete={openDeleteModal}
      />

      {/* Create Task Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Task"
      >
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      </Modal>

      {/* Edit Task Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedTask(null);
        }}
        title="Edit Task"
      >
        <TaskForm
          onSubmit={handleUpdateTask}
          onCancel={() => {
            setIsEditModalOpen(false);
            setSelectedTask(null);
          }}
          initialData={{
            title: selectedTask?.title || "",
            description: selectedTask?.description || "",
          }}
          mode="edit"
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setTaskToDelete(null);
        }}
        title="Delete Task"
      >
        <div className="space-y-4">
          <p className="text-ink/80">
            Are you sure you want to delete this task? This action cannot be
            undone.
          </p>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => {
                setIsDeleteModalOpen(false);
                setTaskToDelete(null);
              }}
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
