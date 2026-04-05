---
name: frontend-data-enforcer
description: Enforce centralized data access patterns in frontend to prevent direct fetch() calls and ensure consistent API usage. Use when (1) reviewing frontend code that fetches data, (2) user adds API calls to components, (3) during code review for data patterns, or (4) before merging frontend changes.
license: Complete terms in LICENSE.txt
---

# Frontend Data Enforcer

Enforce centralized API client usage and prevent direct fetch() calls to ensure consistent data access patterns and security.

## Workflow

Follow these steps when reviewing frontend data access:

1. **Verify all API calls use centralized client**
   - Check imports from `@/lib/api`
   - No direct fetch() in components
   - All requests go through api object
   - Consistent error handling

2. **Flag direct fetch() calls in components**
   - Search for fetch() usage
   - Identify hardcoded URLs
   - Check for missing auth headers
   - Note inconsistent patterns

3. **Ensure consistent error handling**
   - Try-catch blocks around API calls
   - User-friendly error messages
   - Loading states managed
   - Error boundaries in place

4. **Check type safety in API responses**
   - TypeScript interfaces used
   - Response types defined
   - No `any` types
   - Proper type assertions

5. **Validate auth headers are included**
   - JWT token in requests
   - Cookies sent with credentials
   - Auth refresh handling
   - Unauthorized redirects

## Output Format

Present data access review using this structure:

```
🔍 Data Access Review: [component-name]

File: src/core/frontend/components/tasks/TaskList.tsx

✅ Compliant Patterns:
- Uses centralized API client (api.getTasks)
- Type-safe response handling (Task[])
- Error handling with try-catch
- Loading state managed

❌ Violations Found:
Line 23: Direct fetch() call
  Current: const res = await fetch('/api/v1/tasks')
  Fix: const tasks = await api.getTasks()
  Reason: Bypasses centralized client, missing auth, no type safety

Line 45: Hardcoded URL
  Current: fetch('http://localhost:8000/api/v1/tasks')
  Fix: Use api.getTasks() from @/lib/api
  Reason: Environment-specific URL should come from config

Line 67: Missing error handling
  Current: const data = await api.getTasks()
  Fix: Wrap in try-catch with setError state
  Reason: Unhandled errors crash the app
```

## Required Pattern: Centralized API Client

**Single API Client (lib/api.ts):**
```typescript
import type { Task, TaskCreate } from '@/types/task';

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
    credentials: 'include',  // Auto-include JWT cookie
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
  getTasks: () => fetchWithAuth<Task[]>('/api/v1/tasks'),
  createTask: (data: TaskCreate) =>
    fetchWithAuth<Task>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  // ... other methods
};
```

**Component Usage (CORRECT):**
```typescript
'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Task } from '@/types/task';

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTasks() {
      try {
        setIsLoading(true);
        setError(null);
        const data = await api.getTasks();  // ✅ Centralized client
        setTasks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tasks');
      } finally {
        setIsLoading(false);
      }
    }

    loadTasks();
  }, []);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  );
}
```

## Anti-Patterns to Flag

**❌ Direct fetch() in Component:**
```typescript
// WRONG: Bypasses centralized client
export function TaskList() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetch('/api/v1/tasks')  // ❌ Direct fetch
      .then(res => res.json())
      .then(setTasks);
  }, []);

  // Problems:
  // - No auth headers
  // - No error handling
  // - Hardcoded URL
  // - No type safety
  // - No loading state
}
```

**✅ Correct Pattern:**
```typescript
// CORRECT: Uses centralized client
export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTasks() {
      try {
        setIsLoading(true);
        const data = await api.getTasks();  // ✅ Centralized
        setTasks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed');
      } finally {
        setIsLoading(false);
      }
    }
    loadTasks();
  }, []);

  // Benefits:
  // - Auth headers automatic
  // - Error handling
  // - Environment-aware URLs
  // - Type-safe
  // - Loading/error states
}
```

**❌ Hardcoded URLs:**
```typescript
// WRONG: Environment-specific hardcoding
fetch('http://localhost:8000/api/v1/tasks')  // ❌
fetch('https://api.production.com/tasks')    // ❌
```

**✅ Correct Pattern:**
```typescript
// CORRECT: URLs from centralized client
api.getTasks()  // ✅ Environment configured in lib/api.ts
```

**❌ Missing Auth Headers:**
```typescript
// WRONG: No authentication
fetch('/api/v1/tasks')  // ❌ Missing Authorization header
```

**✅ Correct Pattern:**
```typescript
// CORRECT: Auth handled by centralized client
api.getTasks()  // ✅ credentials: 'include' sends JWT cookie
```

**❌ Inconsistent Error Handling:**
```typescript
// WRONG: Different error patterns everywhere
const data = await fetch('/api/tasks').then(r => r.json());  // ❌ No handling

try {
  const data = await fetch('/api/tasks');  // ❌ Inconsistent
  return data.json();
} catch {
  console.log('Error');  // ❌ Silent failure
}
```

**✅ Correct Pattern:**
```typescript
// CORRECT: Consistent error handling via centralized client
try {
  const tasks = await api.getTasks();  // ✅ Throws on error
  setTasks(tasks);
} catch (err) {
  setError(err instanceof Error ? err.message : 'Failed');  // ✅ User-friendly
}
```

**❌ No Type Safety:**
```typescript
// WRONG: Any types everywhere
const [tasks, setTasks] = useState<any>([]);  // ❌
const data: any = await fetch('/api/tasks').then(r => r.json());  // ❌
```

**✅ Correct Pattern:**
```typescript
// CORRECT: Full type safety
const [tasks, setTasks] = useState<Task[]>([]);  // ✅
const data: Task[] = await api.getTasks();  // ✅
```

## Review Checklist

When reviewing frontend data access code, verify:

**✅ Centralized Client:**
- [ ] All API calls use `api` object from `@/lib/api`
- [ ] No direct `fetch()` calls in components
- [ ] No hardcoded API URLs
- [ ] Environment variables for API base URL

**✅ Type Safety:**
- [ ] TypeScript interfaces for all API responses
- [ ] No `any` types
- [ ] Proper type imports from `@/types`
- [ ] Type assertions only when necessary

**✅ Error Handling:**
- [ ] Try-catch around all API calls
- [ ] Error state managed in component
- [ ] User-friendly error messages
- [ ] Error boundaries for global errors

**✅ Loading States:**
- [ ] Loading state before API call
- [ ] Loading UI shown to user
- [ ] Loading cleared on success/error
- [ ] No content flash while loading

**✅ Authentication:**
- [ ] JWT token included automatically
- [ ] Credentials sent with requests
- [ ] 401 errors handled (redirect to login)
- [ ] Token refresh handled if needed

**✅ Consistency:**
- [ ] All components use same patterns
- [ ] No duplicate API client code
- [ ] Shared error handling logic
- [ ] Consistent response parsing

## Key Rules

- **NO direct fetch() in components** - Use centralized `@/lib/api` client
- **All API calls through api object** - Single source for all requests
- **Auth headers automatic** - Centralized client handles credentials
- **Consistent error handling** - Same pattern across all components
- **Type-safe requests/responses** - Use TypeScript interfaces
- **Environment-aware URLs** - From process.env, not hardcoded
- **Loading/error states required** - Every API call manages state
- **No silent failures** - Always show errors to user
- **Validate all reviews** - Check every component that fetches data
- **Enforce in code review** - Flag violations before merge
