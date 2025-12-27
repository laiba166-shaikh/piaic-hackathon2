/**
 * Shared TypeScript types for Task domain.
 *
 * These types are used across frontend and backend to ensure
 * type consistency and contract compliance.
 */

/**
 * Base Task entity as stored in database and returned from API
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

/**
 * Schema for creating a new task
 */
export interface TaskCreate {
  title: string;
  description?: string;
}

/**
 * Schema for updating an existing task
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
}

/**
 * Task response schema (same as Task for Phase 1)
 */
export type TaskResponse = Task;

/**
 * Filters for querying tasks
 */
export interface TaskFilters {
  completed?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}
