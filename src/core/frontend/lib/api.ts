/**
 * Centralized API client for backend communication with JWT authentication.
 *
 * All backend API calls MUST go through this client.
 * DO NOT use direct fetch() calls in components.
 *
 * This client automatically includes JWT tokens in the Authorization header
 * for authentication with the FastAPI backend.
 */

import { getJwtToken, clearJwtToken } from "./jwt-storage";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with JWT authentication and error handling.
 *
 * @param endpoint - API endpoint (e.g., "/api/v1/tasks")
 * @param options - Fetch options
 * @returns Promise with JSON response
 * @throws Error if request fails
 */
async function fetchWithAuth(endpoint: string, options?: RequestInit) {
  try {
    // Get JWT token from storage
    const token = getJwtToken();

    // Build headers with JWT token
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    // Add Authorization header if token is available
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // Handle specific error codes
      if (response.status === 401) {
        // Clear expired or invalid JWT token
        clearJwtToken();

        // Don't automatically redirect - let the component handle it
        // This prevents redirect loops during auth initialization
        throw new Error("Authentication required. Please log in.");
      }

      if (response.status === 404) {
        throw new Error("Resource not found");
      }

      // Try to parse error message from response
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `API Error: ${response.statusText}`
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    return response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Network error. Please check your connection.");
  }
}

/**
 * API client with typed methods for backend endpoints.
 */
export const api = {
  /**
   * Health check endpoint
   */
  health: () => fetchWithAuth("/health"),

  /**
   * Get all tasks for the authenticated user
   */
  getTasks: () => fetchWithAuth("/api/v1/tasks"),

  /**
   * Get a single task by ID
   */
  getTask: (id: number) => fetchWithAuth(`/api/v1/tasks/${id}`),

  /**
   * Create a new task
   */
  createTask: (task: { title: string; description?: string }) =>
    fetchWithAuth("/api/v1/tasks", {
      method: "POST",
      body: JSON.stringify(task),
    }),

  /**
   * Update a task
   */
  updateTask: (
    id: number,
    task: { title?: string; description?: string; completed?: boolean }
  ) =>
    fetchWithAuth(`/api/v1/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(task),
    }),

  /**
   * Delete a task (soft delete)
   */
  deleteTask: (id: number) =>
    fetchWithAuth(`/api/v1/tasks/${id}`, {
      method: "DELETE",
    }),

  /**
   * Toggle task completion status
   */
  toggleTask: (id: number) =>
    fetchWithAuth(`/api/v1/tasks/${id}/toggle`, {
      method: "PATCH",
    }),
};
