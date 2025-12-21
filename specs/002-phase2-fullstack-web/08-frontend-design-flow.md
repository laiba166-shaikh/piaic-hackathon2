# Frontend Architecture & Design Flow - Phase 2

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-12-21
**Type:** Architecture Reference Document

---

## Table of Contents

1. [Purpose](#purpose)
2. [Routing & Navigation](#routing--navigation)
3. [Authentication Flow](#authentication-flow)
4. [Data Flow](#data-flow)
5. [UI State Management](#ui-state-management)
6. [Component Boundaries](#component-boundaries)
7. [Design System Basics](#design-system-basics)
8. [Non-Goals](#non-goals)
9. [Code Examples](#code-examples)

---

## Purpose

### Role of Frontend in Phase 2

The frontend serves as the **user-facing interface** for the multi-user task management application, providing:

1. **Authentication Interface**
   - User login and registration
   - JWT token management (Better Auth)
   - Session persistence

2. **Task Management UI**
   - Create, read, update, delete tasks
   - View task lists and details
   - Interactive forms and feedback

3. **User Experience**
   - Responsive design (mobile + desktop)
   - Loading and error states
   - Client-side validation
   - Optimistic UI updates (where appropriate)

4. **API Communication**
   - Centralized API client
   - Request/response handling
   - Error handling and retry logic
   - Authentication header injection

### Technology Stack

| Technology | Purpose |
|------------|---------|
| **Next.js 15+** | React framework with App Router |
| **React 18+** | UI library with Server/Client Components |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |
| **Better Auth** | JWT authentication library |
| **Vitest** | Unit testing framework |
| **React Testing Library** | Component testing |

### Architecture Principles

1. **Server-First Rendering**
   - Use Server Components by default
   - Only use Client Components when needed (interactivity, hooks, browser APIs)

2. **Centralized Data Access**
   - All API calls through `lib/api.ts`
   - No direct `fetch()` calls in components

3. **Type Safety**
   - Use shared types from `shared/types/`
   - No duplicate type definitions

4. **User Isolation**
   - All data fetched with user's JWT token
   - No user_id in URLs or request bodies

---

## Routing & Navigation

### Next.js App Router Structure

```
frontend/app/
├── layout.tsx              # Root layout (wraps all pages)
├── page.tsx                # Home/Dashboard page (/)
├── login/
│   └── page.tsx            # Login page (/login)
├── register/
│   └── page.tsx            # Register page (/register)
├── tasks/
│   ├── page.tsx            # Task list page (/tasks) with create modal
│   └── [id]/
│       └── page.tsx        # Task detail page (/tasks/[id])
└── error.tsx               # Error boundary
```

**Note:** Task creation uses a modal dialog (not a separate page). The "Create Task" button on `/tasks` opens a modal with the form.

### Route Types

**1. Public Routes (No Auth Required)**
- `/login` - Login page
- `/register` - Registration page

**2. Protected Routes (Auth Required)**
- `/` - Dashboard (redirects to /login if not authenticated)
- `/tasks` - Task list with create modal
- `/tasks/[id]` - Task detail

### Access Control (Middleware)

**Middleware Pattern:** `middleware.ts` in root

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
                     request.nextUrl.pathname.startsWith('/register');

  // Redirect to login if accessing protected route without token
  if (!token && !isAuthPage) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Redirect to dashboard if accessing auth pages with valid token
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### Navigation Patterns

**Use Next.js Link for Client-Side Navigation:**

```typescript
import Link from 'next/link';

// ✅ CORRECT - Client-side navigation
<Link href="/tasks">View Tasks</Link>
<Link href={`/tasks/${task.id}`}>View Task</Link>

// ❌ WRONG - Full page reload
<a href="/tasks">View Tasks</a>
```

**Programmatic Navigation:**

```typescript
'use client';
import { useRouter } from 'next/navigation';

export function TaskForm() {
  const router = useRouter();

  const handleSubmit = async () => {
    // ... create task
    router.push('/tasks');  // Navigate after success
  };
}
```

### Layout Hierarchy

**Root Layout:** `app/layout.tsx`
- Wraps entire application
- Includes global styles, fonts
- Persistent across navigation

```typescript
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <nav>/* Global navigation */</nav>
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
```

---

## Authentication Flow

### Better Auth Integration

**Better Auth manages:**
- User registration
- User login/logout
- JWT token generation
- Token storage (HTTP-only cookie)
- Token refresh

### Authentication States

```typescript
// User authentication states
type AuthState =
  | 'loading'        // Checking auth status
  | 'authenticated'  // User logged in, valid token
  | 'unauthenticated' // User not logged in or token expired
```

### Login Flow

```
1. User visits /login
2. User enters credentials (email, password)
3. Frontend sends credentials to Better Auth
4. Better Auth validates credentials
5. Better Auth issues JWT token (includes user_id in 'sub' claim)
6. Token stored in HTTP-only cookie
7. User redirected to dashboard (/)
8. All subsequent API requests include JWT in Authorization header
```

**Login Component Example:**

```typescript
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signIn } from '@/lib/auth'; // Better Auth wrapper

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await signIn({ email, password });
      router.push('/'); // Redirect to dashboard
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

### Logout Flow

```
1. User clicks logout button
2. Frontend calls Better Auth signOut()
3. Better Auth clears JWT cookie
4. User redirected to /login
```

```typescript
'use client';
import { signOut } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    await signOut();
    router.push('/login');
  };

  return <button onClick={handleLogout}>Logout</button>;
}
```

### Protected Routes Pattern

**Middleware handles protection automatically**, but for fine-grained control:

```typescript
// app/tasks/page.tsx (Server Component)
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';

export default async function TasksPage() {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  // Fetch and display tasks
  return <TaskList />;
}
```

### Token Management

**Better Auth handles token storage and refresh automatically.**

Frontend doesn't directly manipulate tokens - Better Auth manages:
- Token storage (HTTP-only cookie)
- Token expiration
- Token refresh
- Token inclusion in requests

---

## Data Flow

### Centralized API Client

**All API calls MUST go through `lib/api.ts`**

```typescript
// lib/api.ts
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
    credentials: 'include', // Include JWT cookie
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Request failed'
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle 204 No Content (DELETE responses)
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const api = {
  // Tasks
  getTasks: () => fetchWithAuth<Task[]>('/api/v1/tasks'),
  getTask: (id: number) => fetchWithAuth<Task>(`/api/v1/tasks/${id}`),
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

### Request Lifecycle

```
1. Component calls api.getTasks()
2. api.getTasks() calls fetchWithAuth()
3. fetchWithAuth() adds:
   - Content-Type: application/json
   - Credentials: include (JWT cookie)
4. Request sent to backend
5. Backend validates JWT, returns data
6. fetchWithAuth() checks response.ok
7. If error: Parse error, throw Error
8. If success: Parse JSON, return data
9. Component receives data or catches error
```

### Error Handling

**Three levels of error handling:**

**1. API Client Level (lib/api.ts)**
```typescript
async function fetchWithAuth<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, { ... });

  if (!response.ok) {
    // Parse error from backend
    const error = await response.json().catch(() => ({
      detail: 'Request failed'
    }));
    throw new Error(error.detail);
  }

  return response.json();
}
```

**2. Component Level (try/catch)**
```typescript
'use client';
import { api } from '@/lib/api';

export function TaskList() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTasks() {
      try {
        const tasks = await api.getTasks();
        setTasks(tasks);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tasks');
      }
    }
    loadTasks();
  }, []);

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return <div>{/* Render tasks */}</div>;
}
```

**3. Global Error Boundary (app/error.tsx)**
```typescript
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Retry Logic (Optional Enhancement)

```typescript
async function fetchWithRetry<T>(
  endpoint: string,
  options: RequestInit = {},
  retries = 3
): Promise<T> {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetchWithAuth<T>(endpoint, options);
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## UI State Management

### State Types

Every data-fetching component should handle these states:

1. **Loading** - Data is being fetched
2. **Empty** - No data exists
3. **Error** - Request failed
4. **Success** - Data loaded successfully

### State Management Pattern

```typescript
'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Task } from '@shared/types/task';

type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [status, setStatus] = useState<LoadingState>('idle');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTasks() {
      setStatus('loading');
      setError(null);

      try {
        const data = await api.getTasks();
        setTasks(data);
        setStatus('success');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tasks');
        setStatus('error');
      }
    }

    loadTasks();
  }, []);

  // Loading state
  if (status === 'loading') {
    return <LoadingSpinner />;
  }

  // Error state
  if (status === 'error') {
    return (
      <ErrorMessage
        message={error}
        retry={() => window.location.reload()}
      />
    );
  }

  // Empty state
  if (status === 'success' && tasks.length === 0) {
    return (
      <EmptyState
        message="No tasks yet. Create your first task!"
        action={<Link href="/tasks/new">Create Task</Link>}
      />
    );
  }

  // Success state with data
  return (
    <ul>
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </ul>
  );
}
```

### Loading States

**Skeleton Loaders (Preferred):**

```typescript
export function TaskListSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map(i => (
        <div key={i} className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      ))}
    </div>
  );
}
```

**Spinner (Simple fallback):**

```typescript
export function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );
}
```

### Empty States

```typescript
export function EmptyState({
  message,
  action
}: {
  message: string;
  action?: React.ReactNode
}) {
  return (
    <div className="text-center py-12">
      <p className="text-gray-500 mb-4">{message}</p>
      {action}
    </div>
  );
}
```

### Error States

```typescript
export function ErrorMessage({
  message,
  retry
}: {
  message: string;
  retry?: () => void
}) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <p className="text-red-800 mb-2">{message}</p>
      {retry && (
        <button
          onClick={retry}
          className="text-sm text-red-600 hover:text-red-800"
        >
          Try again
        </button>
      )}
    </div>
  );
}
```

### Form Submission States

```typescript
type FormStatus = 'idle' | 'submitting' | 'success' | 'error';

export function TaskForm() {
  const [status, setStatus] = useState<FormStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');
    setError(null);

    try {
      await api.createTask({ title, description });
      setStatus('success');
      // Show success message, redirect, etc.
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      setStatus('error');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}

      <button
        type="submit"
        disabled={status === 'submitting'}
      >
        {status === 'submitting' ? 'Creating...' : 'Create Task'}
      </button>

      {status === 'error' && <ErrorMessage message={error!} />}
      {status === 'success' && <SuccessMessage message="Task created!" />}
    </form>
  );
}
```

---

## Component Boundaries

### Server Components vs Client Components

**Use Server Components by default. Only use Client Components when you need:**
- Interactivity (onClick, onChange)
- React hooks (useState, useEffect, useContext)
- Browser APIs (localStorage, window)
- Event listeners

### Server Components (Default)

**Characteristics:**
- No `'use client'` directive
- Can fetch data directly (async functions)
- Can access backend resources
- Cannot use hooks or browser APIs
- Rendered on server

**Use for:**
- Pages that fetch data
- Layouts
- Static content
- SEO-critical content

```typescript
// app/tasks/page.tsx (Server Component)
import { api } from '@/lib/api';
import { TaskList } from '@/components/tasks/TaskList';

export default async function TasksPage() {
  // Fetch data on server
  const tasks = await api.getTasks();

  return (
    <div>
      <h1>My Tasks</h1>
      <TaskList tasks={tasks} />
    </div>
  );
}
```

### Client Components

**Characteristics:**
- Includes `'use client'` directive at top
- Can use hooks and browser APIs
- Rendered on client (browser)
- Can handle user interactions

**Use for:**
- Forms with user input
- Interactive components (buttons, modals)
- Components using state or effects
- Browser API usage

```typescript
// components/tasks/TaskForm.tsx (Client Component)
'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

export function TaskForm() {
  const [title, setTitle] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createTask({ title });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <button type="submit">Create</button>
    </form>
  );
}
```

### Component Organization

```
frontend/components/
├── ui/                      # Shared UI components (Client)
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx            # Reusable modal dialog
│   ├── Card.tsx
│   └── ErrorMessage.tsx
│
├── tasks/                   # Feature-specific components
│   ├── TaskList.tsx         # Client (uses state)
│   ├── TaskForm.tsx         # Client (form with state)
│   ├── TaskCard.tsx         # Client (interactive)
│   ├── TaskModal.tsx        # Client (modal wrapper for TaskForm)
│   └── TaskDetail.tsx       # Could be Server
│
└── layout/                  # Layout components
    ├── Header.tsx           # Server (static)
    ├── Footer.tsx           # Server (static)
    └── Sidebar.tsx          # Client (collapsible)
```

### Modal Pattern for Forms

**Use modals for create/edit operations instead of separate pages:**

```typescript
// components/ui/Modal.tsx
'use client';

import { useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>

          {children}
        </div>
      </div>
    </div>
  );
}

// Usage in tasks page
'use client';
import { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { TaskForm } from '@/components/tasks/TaskForm';

export function TasksPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsCreateModalOpen(true)}>
        Create Task
      </button>

      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Task"
      >
        <TaskForm
          onSuccess={() => setIsCreateModalOpen(false)}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      </Modal>
    </div>
  );
}
```

### Prop Passing Pattern

**Pass data from Server Components to Client Components:**

```typescript
// Server Component (page)
export default async function TasksPage() {
  const tasks = await api.getTasks();

  // Pass data as props to Client Component
  return <TaskList tasks={tasks} />;
}

// Client Component
'use client';
export function TaskList({ tasks }: { tasks: Task[] }) {
  const [localTasks, setLocalTasks] = useState(tasks);
  // Now can use state and interactivity
}
```

---

## Design System Basics

### Tailwind Configuration

**Use Tailwind CSS for all styling. No custom CSS files.**

**Common Utilities:**

```typescript
// Layout
className="container mx-auto px-4 py-8"
className="flex items-center justify-between"
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"

// Spacing
className="space-y-4"  // Vertical spacing between children
className="space-x-2"  // Horizontal spacing

// Typography
className="text-3xl font-bold"
className="text-sm text-gray-500"

// Colors
className="bg-blue-600 text-white"
className="bg-gray-50 border border-gray-200"

// Interactive
className="hover:bg-blue-700 active:bg-blue-800"
className="focus:outline-none focus:ring-2 focus:ring-blue-500"
```

### Responsive Design

**Mobile-first approach:**

```typescript
className="
  text-sm          // Mobile (default)
  md:text-base     // Tablet (768px+)
  lg:text-lg       // Desktop (1024px+)
"

className="
  grid-cols-1      // Mobile: 1 column
  md:grid-cols-2   // Tablet: 2 columns
  lg:grid-cols-3   // Desktop: 3 columns
"
```

### Color Palette (Tailwind Defaults)

- **Primary:** Blue (bg-blue-600, text-blue-600)
- **Success:** Green (bg-green-600)
- **Error:** Red (bg-red-600)
- **Warning:** Yellow (bg-yellow-600)
- **Neutral:** Gray (bg-gray-50, bg-gray-100, etc.)

### Accessibility

**Always include:**
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus indicators
- Alt text for images

```typescript
<button
  aria-label="Delete task"
  className="focus:outline-none focus:ring-2 focus:ring-blue-500"
>
  Delete
</button>

<input
  aria-label="Task title"
  aria-required="true"
/>
```

---

## Non-Goals

### What Frontend Intentionally Does NOT Handle

1. **User Management**
   - Frontend does NOT manage user data
   - Better Auth handles all user operations
   - Backend has NO users table

2. **Business Logic**
   - Frontend does NOT implement business rules
   - All validation happens on backend (authoritative)
   - Frontend validation is UX enhancement only

3. **Data Storage**
   - Frontend does NOT persist data (no localStorage for tasks)
   - All data stored in backend database
   - JWT token is the only thing stored (by Better Auth)

4. **Authorization Decisions**
   - Frontend does NOT decide if user can access resource
   - Backend enforces all authorization (user_id filtering)
   - Frontend only provides UI based on backend responses

5. **Backend Concerns**
   - No database queries
   - No user_id management
   - No soft delete logic
   - All handled by backend

6. **Complex State Management**
   - No Redux, Zustand, or global state libraries in Phase 2
   - Use React state and Server Components
   - Deferred to Phase 3 if needed

7. **Real-Time Features**
   - No WebSocket connections
   - No live updates
   - Manual refresh required
   - Deferred to Phase 3

8. **Advanced UI Features**
   - No drag-and-drop (Phase 3+)
   - No rich text editor (Phase 3+)
   - No charts/graphs (Phase 5+)
   - Keep UI simple in Phase 2

### Frontend Validation is UX, Not Security

**Frontend validation prevents bad UX, backend validation prevents bad data.**

```typescript
// Frontend validation (UX)
const handleSubmit = async (e: React.FormEvent) => {
  // Check locally for quick feedback
  if (title.trim().length === 0) {
    setError('Title is required');
    return;
  }

  // Backend still validates!
  try {
    await api.createTask({ title });
  } catch (err) {
    // Backend rejected it - show backend error
    setError(err.message);
  }
};
```

---

## Code Examples

### Complete Page Example (Server Component)

```typescript
// app/tasks/page.tsx
import { api } from '@/lib/api';
import { TaskList } from '@/components/tasks/TaskList';
import { CreateTaskButton } from '@/components/tasks/CreateTaskButton';

export default async function TasksPage() {
  // Fetch on server
  const tasks = await api.getTasks();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">My Tasks</h1>
        <CreateTaskButton />
      </div>

      <TaskList tasks={tasks} />
    </div>
  );
}
```

### Complete Component Example (Client Component)

```typescript
// components/tasks/TaskList.tsx
'use client';

import { useState } from 'react';
import type { Task } from '@shared/types/task';
import { api } from '@/lib/api';
import { TaskCard } from './TaskCard';

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks: initialTasks }: TaskListProps) {
  const [tasks, setTasks] = useState(initialTasks);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async (id: number) => {
    try {
      await api.deleteTask(id);
      setTasks(tasks.filter(t => t.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No tasks yet. Create your first task!
      </div>
    );
  }

  return (
    <div>
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-4">
        {tasks.map(task => (
          <TaskCard
            key={task.id}
            task={task}
            onDelete={() => handleDelete(task.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

### Complete Form Example (Modal Pattern)

```typescript
// components/tasks/TaskForm.tsx
'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { TaskCreate } from '@shared/types/task';

interface TaskFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function TaskForm({ onSuccess, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'idle' | 'submitting' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation (UX)
    if (title.trim().length === 0) {
      setError('Title is required');
      return;
    }

    setStatus('submitting');
    setError(null);

    try {
      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || null,
      };

      await api.createTask(taskData);
      setStatus('idle');
      onSuccess?.(); // Close modal and refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      setStatus('error');
    } finally {
      setStatus('idle');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          maxLength={200}
          required
        />
        <p className="text-sm text-gray-500 mt-1">{title.length}/200 characters</p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={status === 'submitting'}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'submitting' ? 'Creating...' : 'Create Task'}
        </button>

        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
```

---

## Summary

This frontend architecture document establishes:

✅ **Purpose** - User interface, authentication, API communication
✅ **Routing & Navigation** - Next.js App Router, protected routes, middleware
✅ **Authentication Flow** - Better Auth, JWT tokens, login/logout, redirects
✅ **Data Flow** - Centralized API client, request lifecycle, error handling
✅ **UI State Management** - Loading, empty, error, success states
✅ **Component Boundaries** - Server Components (default) vs Client Components (interactivity)
✅ **Design System Basics** - Tailwind utilities, responsive design, accessibility
✅ **Non-Goals** - What frontend doesn't handle (business logic, data storage, authorization)

**All Phase 2 frontend features MUST follow these patterns.**

**Feature-specific UI details belong in Section 12 (UI/UX Requirements) of each feature spec, not in this architecture document.**

---

**Document Status:** Active
**Referenced By:** All Phase 2 feature specs (01-07)
**Enforced By:** UI Developer Agent, Quality Guardian Agent
**Next Review:** After Feature 02 (Task CRUD) implementation
