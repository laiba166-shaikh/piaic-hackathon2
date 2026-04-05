---
name: frontend-composer
description: Build Next.js components following App Router patterns and project conventions. Use when (1) creating new React components, (2) building pages in the App Router, (3) implementing UI features, or (4) user asks about frontend implementation.
license: Complete terms in LICENSE.txt
---

# Frontend Composer

Design and implement Next.js components using App Router, TypeScript, and Tailwind CSS following Phase 2 frontend patterns.

## Workflow

Follow these steps when building frontend features:

1. **Create Next.js App Router pages and layouts**
   - Determine page route structure
   - Choose Server vs Client Component
   - Plan data fetching strategy
   - Design component hierarchy

2. **Build React components with TypeScript**
   - Type-safe props and state
   - Import shared types from `@/types`
   - Use strict TypeScript mode
   - Proper error boundaries

3. **Apply Tailwind CSS styling**
   - Utility-first approach
   - Responsive design classes
   - Consistent spacing/colors
   - No custom CSS files

4. **Implement client/server component patterns**
   - Server Components by default
   - Add "use client" only when needed
   - Proper data fetching boundaries
   - Streaming and Suspense

5. **Connect to API through centralized client**
   - Use `@/lib/api` for all requests
   - Never direct fetch in components
   - Type-safe API responses
   - Proper error handling

## Output Format

Present frontend architecture using this structure:

```
🎨 Frontend Component: [component-name]

Component Type: Server Component | Client Component
Location: src/core/frontend/app/[path]/page.tsx

Props:
- tasks: Task[] (from @/types/task)
- onDelete?: (id: number) => void

State (if Client Component):
- isLoading: boolean
- error: string | null

API Calls:
- api.getTasks() → Task[]
- api.deleteTask(id) → void

Styling:
- Tailwind utility classes
- Responsive: mobile-first design
```

## Required Project Structure

```
frontend/
├── app/                      # App Router (Next.js 13+)
│   ├── layout.tsx            # Root layout with providers
│   ├── page.tsx              # Home page (Server Component)
│   ├── loading.tsx           # Loading UI
│   ├── error.tsx             # Error UI
│   │
│   ├── tasks/
│   │   ├── page.tsx          # Tasks list page
│   │   ├── [id]/
│   │   │   └── page.tsx      # Task detail page
│   │   └── new/
│   │       └── page.tsx      # Create task page
│   │
│   └── api/                  # API routes (if needed)
│       └── auth/
│           └── [...all]/route.ts
│
├── components/               # Reusable components
│   ├── ui/                   # Generic UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── card.tsx
│   │
│   └── tasks/                # Feature-specific components
│       ├── TaskList.tsx
│       ├── TaskCard.tsx
│       └── TaskForm.tsx
│
├── lib/                      # Utilities and shared code
│   ├── api.ts                # Centralized API client
│   ├── auth.ts               # Better Auth config
│   └── utils.ts              # Helper functions
│
├── types/                    # TypeScript types
│   ├── task.ts               # Task interfaces
│   └── api.ts                # API request/response types
│
└── middleware.ts             # Route protection
```

## Server Component Pattern (Default)

```typescript
// app/tasks/page.tsx
import { api } from '@/lib/api';
import { TaskList } from '@/components/tasks/TaskList';
import type { Task } from '@/types/task';

// Server Component (default in app directory)
export default async function TasksPage() {
  // Direct API call in Server Component
  const tasks: Task[] = await api.getTasks();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        My Tasks
      </h1>
      <TaskList tasks={tasks} />
    </div>
  );
}
```

## Client Component Pattern (Interactive)

```typescript
// components/tasks/TaskForm.tsx
'use client';  // Required for interactivity

import { useState } from 'react';
import { api } from '@/lib/api';
import type { TaskCreate } from '@/types/task';

interface TaskFormProps {
  onSuccess?: () => void;
}

export function TaskForm({ onSuccess }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const taskData: TaskCreate = {
        title,
        description: description || undefined,
      };

      await api.createTask(taskData);

      // Reset form
      setTitle('');
      setDescription('');
      onSuccess?.();

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">
          Title
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
          required
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
          rows={3}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}
```

## Centralized API Client

```typescript
// lib/api.ts
import type { Task, TaskCreate, TaskUpdate } from '@/types/task';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',  // Include cookies (JWT)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Request failed'
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Tasks
  getTasks: () =>
    fetchWithAuth<Task[]>('/api/v1/tasks'),

  getTask: (id: number) =>
    fetchWithAuth<Task>(`/api/v1/tasks/${id}`),

  createTask: (data: TaskCreate) =>
    fetchWithAuth<Task>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: TaskUpdate) =>
    fetchWithAuth<Task>(`/api/v1/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTask: (id: number) =>
    fetchWithAuth<void>(`/api/v1/tasks/${id}`, {
      method: 'DELETE',
    }),
};
```

## TypeScript Types

```typescript
// types/task.ts
export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: number | null;
  tags: string[];
  created_at: string;  // ISO 8601
  updated_at: string;  // ISO 8601
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: number;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: number;
  tags?: string[];
}
```

## When to Use Server vs Client Components

**Use Server Components (default) when:**
- No interactivity needed
- Fetching data from API
- Accessing backend resources
- Rendering static content
- SEO is important

**Use Client Components ("use client") when:**
- Using React hooks (useState, useEffect, etc.)
- Event handlers (onClick, onChange, etc.)
- Browser APIs (localStorage, etc.)
- Third-party client libraries
- Real-time updates

## Key Rules

- **Server Components by default** - Only add "use client" when needed
- **All API calls through lib/api.ts** - Never direct fetch in components
- **TypeScript strict mode** - Import types from @/types
- **Tailwind for all styling** - No CSS modules or custom CSS files
- **Type-safe props** - Define interfaces for all component props
- **Error boundaries** - Handle errors gracefully with error.tsx
- **Loading states** - Use loading.tsx and Suspense
- **Responsive design** - Mobile-first Tailwind classes
- **Accessibility** - Semantic HTML, ARIA labels
- **Import from @/ aliases** - Use path aliases, not relative paths
