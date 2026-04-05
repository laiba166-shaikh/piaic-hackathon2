"use client";

import { api } from "@/lib/api";
import { Task, TaskCreate, TaskUpdate } from "@/types/task";
import { useEffect, useState } from "react";
import { Modal } from "../ui/Modal";
import { TaskForm } from "./TaskForm";
import { TaskList } from "./TaskList";

type FilterType = "all" | "today" | "todo" | "done";

function StatCard({
  label,
  value,
  total,
  barColor,
}: {
  label: string;
  value: number;
  total: number;
  barColor: string;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div className="bg-card rounded-xl p-5 border border-border">
      <p className="text-3xl font-bold text-foreground">{value}</p>
      <p className="text-muted-foreground text-sm mt-1">{label}</p>
      <div className="mt-3 h-1 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} rounded-full transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function TasksPageClient() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<number | null>(null);
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");

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
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleTask(taskId: number) {
    const current = tasks.find((t) => t.id === taskId);
    if (!current) return;
    const newCompleted = !current.completed;

    // Optimistic update — flip immediately, revert on error
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, completed: newCompleted } : t))
    );
    try {
      const updated = await api.updateTask(taskId, { completed: newCompleted });
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    } catch (err) {
      // Revert on failure
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, completed: current.completed } : t))
      );
      console.error("Failed to toggle task:", err);
    }
  }

  async function handleCreateTask(taskData: TaskCreate) {
    try {
      const newTask = await api.createTask(taskData);
      setTasks((prev) => [newTask, ...prev]);
      setIsCreateModalOpen(false);
    } catch (err) {
      throw err;
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
      throw err;
    }
  }

  async function handleDeleteTask() {
    if (!taskToDelete) return;
    setIsDeleting(true);
    try {
      await api.deleteTask(taskToDelete);
      setTasks((prev) => prev.filter((t) => t.id !== taskToDelete));
      setIsDeleteModalOpen(false);
      setTaskToDelete(null);
    } catch (err) {
      console.error("Failed to delete task:", err);
    } finally {
      setIsDeleting(false);
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

  // Stats
  const totalCount = tasks.length;
  const completedCount = tasks.filter((t) => t.completed).length;
  const remainingCount = totalCount - completedCount;

  // Filter logic
  const todayStr = new Date().toDateString();
  const filteredTasks = tasks.filter((t) => {
    if (activeFilter === "today")
      return new Date(t.created_at).toDateString() === todayStr;
    if (activeFilter === "todo") return !t.completed;
    if (activeFilter === "done") return t.completed;
    return true;
  });

  const filterLabels: Record<FilterType, string> = {
    all: "All",
    today: "Today",
    todo: "To Do",
    done: "Done",
  };

  const todayFormatted = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <>
      <div className="h-full flex flex-col">
        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <StatCard
            label="Total tasks"
            value={totalCount}
            total={totalCount}
            barColor="bg-primary"
          />
          <StatCard
            label="Completed"
            value={completedCount}
            total={totalCount}
            barColor="bg-accent"
          />
          <StatCard
            label="Remaining"
            value={remainingCount}
            total={totalCount}
            barColor="bg-primary"
          />
        </div>

        {/* Page header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Task Mate</h1>
            <p className="text-muted-foreground text-sm">
              Organise your thoughts and tasks
            </p>
            <p className="text-muted-foreground text-sm mt-0.5">{todayFormatted}</p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 border border-border rounded-lg text-foreground font-semibold hover:bg-muted transition-colors shrink-0"
          >
            <span className="text-lg leading-none">+</span> Create Task
          </button>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-4">
          {(["all", "today", "todo", "done"] as FilterType[]).map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors border ${
                activeFilter === f
                  ? "bg-foreground text-background border-foreground"
                  : "bg-transparent text-foreground border-border hover:bg-muted"
              }`}
            >
              {filterLabels[f]}
            </button>
          ))}
        </div>

        {/* Task list — scrollable area */}
        <div className="flex-1 overflow-y-auto task-list-scroll pr-1 pb-6">
          <TaskList
            tasks={filteredTasks}
            loading={loading}
            error={error}
            filter={activeFilter}
            onToggle={handleToggleTask}
            onEdit={openEditModal}
            onDelete={openDeleteModal}
          />
        </div>
      </div>

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
          <p className="text-muted-foreground">
            Are you sure you want to delete this task? This action cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => {
                setIsDeleteModalOpen(false);
                setTaskToDelete(null);
              }}
              disabled={isDeleting}
              className="px-4 py-2 border border-border text-foreground rounded-lg hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteTask}
              disabled={isDeleting}
              className="flex items-center gap-2 px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors disabled:opacity-70 disabled:cursor-wait"
            >
              {isDeleting && (
                <div className="w-4 h-4 rounded-full border-2 border-destructive-foreground/40 border-t-destructive-foreground animate-spin" />
              )}
              {isDeleting ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
