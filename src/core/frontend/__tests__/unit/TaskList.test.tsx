/**
 * TaskList Component Tests (RED Phase)
 *
 * These tests should FAIL initially since components are not implemented yet.
 */

import { TaskList } from "@/components/tasks/TaskList";
import { Task } from "@/types/task";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

const mockTasks: Task[] = [
  {
    id: 1,
    user_id: "test-user",
    title: "Buy groceries",
    description: "Milk, eggs, bread",
    completed: false,
    created_at: "2025-12-29T10:00:00Z",
    updated_at: "2025-12-29T10:00:00Z",
  },
  {
    id: 2,
    user_id: "test-user",
    title: "Complete assignment",
    description: null,
    completed: true,
    created_at: "2025-12-29T09:00:00Z",
    updated_at: "2025-12-29T11:00:00Z",
  },
];

describe("TaskList Component", () => {
  it("displays tasks correctly", () => {
    render(<TaskList tasks={mockTasks} loading={false} error={null} />);

    expect(screen.getByText("Buy groceries")).toBeInTheDocument();
    expect(screen.getByText("Milk, eggs, bread")).toBeInTheDocument();
    expect(screen.getByText("Complete assignment")).toBeInTheDocument();
  });

  it("shows empty state when no tasks", () => {
    render(<TaskList tasks={[]} loading={false} error={null} />);

    expect(
      screen.getByText(/no tasks yet/i) || screen.getByText(/get started/i)
    ).toBeInTheDocument();
  });

  it("shows loading state with skeleton", () => {
    render(<TaskList tasks={[]} loading={true} error={null} />);

    // Should show loading skeleton
    expect(
      screen.getByTestId("task-list-skeleton") ||
        screen.getByText(/loading/i)
    ).toBeInTheDocument();
  });

  it("shows error state with error message", () => {
    const errorMessage = "Failed to load tasks";
    render(<TaskList tasks={[]} loading={false} error={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("renders task list without create button (button is in parent)", () => {
    render(<TaskList tasks={mockTasks} loading={false} error={null} />);

    // TaskList component doesn't have a create button (it's in TasksPageClient)
    // Just verify that tasks are rendered
    expect(screen.getByText("Buy groceries")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /create/i })).not.toBeInTheDocument();
  });
});
