"use client";

/**
 * TaskForm Component
 *
 * Form for creating and editing tasks with client-side validation.
 */

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
  const [description, setDescription] = useState(
    initialData?.description || ""
  );
  const [errors, setErrors] = useState<{ title?: string; form?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validateForm(): boolean {
    const newErrors: { title?: string } = {};

    // Title validation
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

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      });
      // Form will be closed by parent component on success
    } catch (err) {
      setErrors({
        form:
          err instanceof Error
            ? err.message
            : "Failed to save task. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Form-level error */}
      {errors.form && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded-lg text-sm">
          {errors.form}
        </div>
      )}

      {/* Title field */}
      <div>
        <label
          htmlFor="task-title"
          className="block text-sm font-medium text-ink mb-1"
        >
          Title <span className="text-red-600">*</span>
        </label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            if (errors.title) {
              setErrors((prev) => ({ ...prev, title: undefined }));
            }
          }}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-vintage focus:border-transparent ${
            errors.title
              ? "border-red-300 bg-red-50"
              : "border-sepia/30 bg-white"
          }`}
          placeholder="Enter task title..."
          maxLength={201} // Allow 201 to show validation error
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? "title-error" : undefined}
        />
        {errors.title && (
          <p id="title-error" className="text-red-600 text-sm mt-1">
            {errors.title}
          </p>
        )}
        <p className="text-ink/50 text-xs mt-1">
          {title.length}/200 characters
        </p>
      </div>

      {/* Description field */}
      <div>
        <label
          htmlFor="task-description"
          className="block text-sm font-medium text-ink mb-1"
        >
          Description <span className="text-ink/50">(optional)</span>
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-sepia/30 rounded-lg focus:ring-2 focus:ring-vintage focus:border-transparent bg-white resize-none"
          placeholder="Add more details about this task..."
        />
      </div>

      {/* Action buttons */}
      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-sepia text-ink rounded-lg hover:bg-paper-dark transition-colors"
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-vintage-dark text-white rounded-lg hover:bg-ink-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isSubmitting}
        >
          {isSubmitting
            ? "Saving..."
            : mode === "edit"
            ? "Update"
            : "Create"}
        </button>
      </div>
    </form>
  );
}
