"use client";

import { useState } from "react";
import { TaskCreate } from "@/types/task";

interface TaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>;
  onCancel: () => void;
  initialData?: {
    title: string;
    description?: string;
  };
  mode?: "create" | "edit";
}

export function TaskForm({
  onSubmit,
  onCancel,
  initialData,
  mode = "create",
}: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [errors, setErrors] = useState<{ title?: string; form?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validateForm(): boolean {
    const newErrors: { title?: string } = {};
    if (!title.trim()) {
      newErrors.title = "Title is required";
    } else if (title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    setErrors({});

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      });
    } catch (err) {
      setErrors({
        form: err instanceof Error ? err.message : "Failed to save task. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errors.form && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive p-3 rounded-lg text-sm">
          {errors.form}
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="task-title" className="block text-sm font-medium text-foreground mb-1">
          Title <span className="text-destructive">*</span>
        </label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            if (errors.title) setErrors((prev) => ({ ...prev, title: undefined }));
          }}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent transition-colors ${
            errors.title
              ? "border-destructive bg-destructive/10 text-foreground"
              : "border-input bg-background text-foreground"
          }`}
          placeholder="Enter task title..."
          maxLength={201}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? "title-error" : undefined}
        />
        {errors.title && (
          <p id="title-error" className="text-destructive text-sm mt-1">{errors.title}</p>
        )}
        <p className="text-muted-foreground text-xs mt-1">{title.length}/200 characters</p>
      </div>

      {/* Description */}
      <div>
        <label htmlFor="task-description" className="block text-sm font-medium text-foreground mb-1">
          Description <span className="text-muted-foreground">(optional)</span>
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent bg-background text-foreground resize-none transition-colors"
          placeholder="Add more details about this task..."
        />
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 border border-border text-foreground rounded-lg hover:bg-muted transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? "Saving..." : mode === "edit" ? "Update" : "Create"}
        </button>
      </div>
    </form>
  );
}
