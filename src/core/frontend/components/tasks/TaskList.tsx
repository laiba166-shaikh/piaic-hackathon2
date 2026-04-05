import { Task } from "@/types/task";
import { TaskCard } from "./TaskCard";

type FilterType = "all" | "today" | "todo" | "done";

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  filter?: FilterType;
  onToggle?: (taskId: number) => Promise<void>;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

const emptyStateContent: Record<FilterType, { heading: string; subtext: string; cta?: string }> = {
  all: {
    heading: "No tasks yet",
    subtext: "Your journey starts with a single task.",
    cta: "Click \"Create Task\" to add your first task.",
  },
  today: {
    heading: "Nothing scheduled for today",
    subtext: "A clear day is a fresh start — add something you want to accomplish today.",
  },
  todo: {
    heading: "All caught up!",
    subtext: "You have no pending tasks. Great work — enjoy the breathing room or plan what's next.",
  },
  done: {
    heading: "No completed tasks yet",
    subtext: "Every finished task is a win. Start checking things off — you've got this!",
  },
};

export function TaskList({ tasks, loading, error,filter, onToggle, onEdit, onDelete }: TaskListProps) {
  if (loading) {
    return (
      <div data-testid="task-list-skeleton" className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card rounded-xl border border-border p-4 animate-pulse">
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 rounded-full bg-muted" />
              <div className="flex-1">
                <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                <div className="h-3 bg-muted rounded w-1/3" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/30 rounded-xl p-6 text-center">
        <p className="text-destructive font-medium mb-1">{error}</p>
        <p className="text-destructive/70 text-sm">
          {error.includes("Authentication")
            ? "Redirecting to login..."
            : "Please try refreshing the page."}
        </p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-card rounded-xl border border-border p-12 text-center">
        <svg
          className="w-12 h-12 mx-auto mb-4 text-muted-foreground/40"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 className="text-foreground font-medium text-lg mb-1">{filter ? emptyStateContent[filter].heading : "No tasks yet"}</h3>
        <p className="text-muted-foreground text-sm">
          {filter ? emptyStateContent[filter].subtext : "Your tasks will appear here."}           
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} onToggle={onToggle} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );
}
