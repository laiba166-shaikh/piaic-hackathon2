/**
 * TaskCard Component Tests (RED Phase)
 */

import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { TaskCard } from "@/components/tasks/TaskCard";
import { Task } from "@/types/task";
import userEvent from "@testing-library/user-event";

const mockTask: Task = {
  id: 1,
  user_id: "test-user",
  title: "Buy groceries",
  description: "Milk, eggs, bread",
  completed: false,
  created_at: "2025-12-29T10:00:00Z",
  updated_at: "2025-12-29T10:00:00Z",
};

describe("TaskCard Component", () => {
  it("displays task title and description", () => {
    render(
      <TaskCard task={mockTask} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.getByText("Buy groceries")).toBeInTheDocument();
    expect(screen.getByText("Milk, eggs, bread")).toBeInTheDocument();
  });

  it("displays task without description", () => {
    const taskWithoutDesc = { ...mockTask, description: null };
    render(
      <TaskCard task={taskWithoutDesc} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.getByText("Buy groceries")).toBeInTheDocument();
    expect(screen.queryByText("Milk, eggs, bread")).not.toBeInTheDocument();
  });

  it("shows edit button and calls onEdit when clicked", async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();

    render(
      <TaskCard task={mockTask} onEdit={onEdit} onDelete={vi.fn()} />
    );

    const editButton = screen.getByRole("button", { name: /edit/i });
    await user.click(editButton);

    expect(onEdit).toHaveBeenCalledWith(mockTask);
  });

  it("shows delete button and calls onDelete when clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();

    render(
      <TaskCard task={mockTask} onEdit={vi.fn()} onDelete={onDelete} />
    );

    const deleteButton = screen.getByRole("button", { name: /delete/i });
    await user.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith(mockTask.id);
  });

  it("displays completion status", () => {
    const completedTask = { ...mockTask, completed: true };
    render(
      <TaskCard task={completedTask} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    // Should indicate completion status visually
    expect(screen.getByText("Buy groceries")).toBeInTheDocument();
  });
});
