/**
 * TaskForm Component Tests (RED Phase)
 */

import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { TaskForm } from "@/components/tasks/TaskForm";
import userEvent from "@testing-library/user-event";

describe("TaskForm Component", () => {
  it("renders form fields", () => {
    render(<TaskForm onSubmit={vi.fn()} onCancel={vi.fn()} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("validates required title field", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<TaskForm onSubmit={onSubmit} onCancel={vi.fn()} />);

    const submitButton = screen.getByRole("button", { name: /create/i });
    await user.click(submitButton);

    // Should show validation error for empty title
    expect(
      await screen.findByText(/title is required/i)
    ).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("validates title max length (200 characters)", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<TaskForm onSubmit={onSubmit} onCancel={vi.fn()} />);

    const titleInput = screen.getByLabelText(/title/i);
    const longTitle = "A".repeat(201);

    await user.type(titleInput, longTitle);
    await user.click(screen.getByRole("button", { name: /create/i }));

    // Should show validation error for title too long
    expect(
      await screen.findByText(/title must be 200 characters or less/i)
    ).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits form with valid data", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<TaskForm onSubmit={onSubmit} onCancel={vi.fn()} />);

    await user.type(screen.getByLabelText(/title/i), "Buy groceries");
    await user.type(screen.getByLabelText(/description/i), "Milk and eggs");
    await user.click(screen.getByRole("button", { name: /create/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        title: "Buy groceries",
        description: "Milk and eggs",
      });
    });
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();

    render(<TaskForm onSubmit={vi.fn()} onCancel={onCancel} />);

    await user.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });

  it("pre-populates form in edit mode", () => {
    const initialData = {
      title: "Existing task",
      description: "Existing description",
    };

    render(
      <TaskForm
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        initialData={initialData}
        mode="edit"
      />
    );

    expect(screen.getByLabelText(/title/i)).toHaveValue("Existing task");
    expect(screen.getByLabelText(/description/i)).toHaveValue(
      "Existing description"
    );
    expect(screen.getByRole("button", { name: /update/i })).toBeInTheDocument();
  });
});
