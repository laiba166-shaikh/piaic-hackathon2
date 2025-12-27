# Frontend Guidelines

**Project:** Phase 2 - Full-Stack Web Application (Frontend)
**Framework:** Next.js 16+ with App Router
**Last Updated:** 2025-12-26

---

## Stack

- **Next.js 16+ (App Router)** - React framework with server components
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Better Auth** - Authentication library for Next.js

---

## Patterns

### Component Architecture

- **Use server components by default** - Leverage Next.js App Router's server components for better performance
- **Client components only when needed** - Use `"use client"` directive only for:
  - Interactive UI (buttons, forms with state)
  - Browser APIs (localStorage, window, document)
  - React hooks (useState, useEffect, etc.)
  - Event handlers (onClick, onChange, etc.)

### API Client

- **ALL backend calls must use the centralized API client**
- **Path:** `/lib/api.ts`
- **NO direct `fetch()` calls in components**

**Example:**
```typescript
import { api } from '@/lib/api'

// ✅ Correct
const tasks = await api.getTasks()

// ❌ Wrong - Do not use direct fetch
const response = await fetch('/api/tasks')
```

---

## Project Structure

```
frontend/
├── app/                        # Next.js App Router pages
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── login/                  # Login page
│   ├── register/               # Registration page
│   └── tasks/                  # Task pages
├── components/                 # Reusable UI components
│   ├── auth/                   # Authentication components
│   ├── tasks/                  # Task-related components
│   ├── layout/                 # Layout components (Header, Sidebar)
│   └── ui/                     # Generic UI components (Button, Input, Modal)
├── lib/                        # Utility libraries
│   ├── api.ts                  # Centralized API client
│   └── auth.ts                 # Better Auth configuration
├── hooks/                      # Custom React hooks
│   └── useAuth.ts              # Authentication hook
├── types/                      # TypeScript type definitions
│   ├── auth.ts                 # Auth types
│   └── task.ts                 # Task types
└── __tests__/                  # Test files
    ├── unit/                   # Unit tests
    └── e2e/                    # End-to-end tests
```

---

## API Client Guidelines

### Centralized API Client (`/lib/api.ts`)

All backend API calls must go through the centralized API client. This ensures:
- Consistent error handling
- Automatic JWT token inclusion
- Type-safe request/response
- Single source of truth for API endpoints

**Example API Client:**
```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchWithAuth(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include', // Include JWT cookie
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`)
  }

  return response.json()
}

export const api = {
  getTasks: () => fetchWithAuth('/api/v1/tasks'),
  createTask: (task: TaskCreate) => fetchWithAuth('/api/v1/tasks', {
    method: 'POST',
    body: JSON.stringify(task),
  }),
  // ... other API methods
}
```

---

## Styling Guidelines

### Tailwind CSS

- **Use Tailwind CSS classes exclusively** - No inline styles, no CSS modules
- **Follow the design system** - Use colors, fonts, and spacing from `tailwind.config.ts`
- **Responsive design** - Use Tailwind's responsive modifiers (sm:, md:, lg:, xl:)

**Journal Theme Palette:**
```javascript
// tailwind.config.ts
colors: {
  paper: '#F5F1E8',      // Paper Cream (background)
  ink: '#2C3E50',        // Ink Black (text)
  vintage: '#4A7C99',    // Vintage Blue (accent)
  sepia: '#8B7355',      // Sepia Brown (borders)
  // ... other colors
}
```

**Example Component:**
```tsx
<div className="bg-paper rounded-lg shadow-md p-6 border border-sepia">
  <h2 className="text-ink font-serif text-2xl mb-4">Task Title</h2>
  <p className="text-ink/80 leading-relaxed">Description...</p>
</div>
```

---

## Authentication Flow

### Better Auth Integration

**Configuration:** `/lib/auth.ts`
**Provider:** Email/Password
**Session Storage:** HTTP-only cookies (secure, SameSite=Strict)

**Key Functions:**
- `signIn(email, password)` - Login user
- `signUp(email, password, name)` - Register user
- `signOut()` - Logout user
- `getSession()` - Check auth status

**Example:**
```typescript
import { authClient } from '@/lib/auth'

// Login
await authClient.signIn.email({ email, password })

// Register
await authClient.signUp.email({ email, password, name })

// Logout
await authClient.signOut()
```

### Protected Routes

**Middleware:** `middleware.ts` checks authentication status
- **Public routes:** `/login`, `/register`
- **Protected routes:** `/`, `/tasks/*`
- **Redirect logic:** Unauthenticated users → `/login`

---

## Component Conventions

### File Naming

- **Components:** PascalCase (e.g., `TaskCard.tsx`, `LoginForm.tsx`)
- **Utilities:** camelCase (e.g., `api.ts`, `auth.ts`)
- **Types:** camelCase with `.ts` extension (e.g., `task.ts`, `auth.ts`)

### Component Structure

```tsx
// components/tasks/TaskCard.tsx

import { Task } from '@/types/task'

interface TaskCardProps {
  task: Task
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export function TaskCard({ task, onToggle, onDelete }: TaskCardProps) {
  return (
    <div className="...">
      {/* Component content */}
    </div>
  )
}
```

### Server vs Client Components

**Server Components (default):**
- Fetch data from backend
- Render static content
- No interactivity needed

**Client Components (`"use client"`):**
- Form interactions
- State management
- Event handlers
- Browser APIs

---

## Error Handling

### Display User-Friendly Messages

- **Network Errors:** "Unable to connect. Please check your internet."
- **401 Unauthorized:** Redirect to `/login`
- **404 Not Found:** "Task not found"
- **500 Server Error:** "Something went wrong. Please try again."

### Error UI Components

```tsx
// components/ui/ErrorMessage.tsx
export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded">
      {message}
    </div>
  )
}
```

---

## Testing Guidelines

### Test File Location

- **Unit Tests:** `__tests__/unit/ComponentName.test.tsx`
- **E2E Tests:** `__tests__/e2e/feature.spec.ts`

### Testing Tools

- **Vitest** - Unit testing framework
- **React Testing Library** - Component testing
- **Playwright** - End-to-end testing

### Example Test

```tsx
// __tests__/unit/TaskCard.test.tsx
import { render, screen } from '@testing-library/react'
import { TaskCard } from '@/components/tasks/TaskCard'

test('renders task title', () => {
  const task = { id: 1, title: 'Test Task', completed: false }
  render(<TaskCard task={task} onToggle={() => {}} onDelete={() => {}} />)
  expect(screen.getByText('Test Task')).toBeInTheDocument()
})
```

---

## Development Workflow

### Running the Development Server

```bash
cd frontend
npm install
npm run dev
```

**Server starts at:** http://localhost:3000

### Environment Variables

Create `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Linting and Formatting

```bash
npm run lint        # Run ESLint
npm run format      # Run Prettier
```

---

## Key Principles

1. **Server-first** - Default to server components, use client components only when necessary
2. **Centralized API** - All backend calls through `/lib/api.ts`
3. **Type Safety** - Use TypeScript types for all data structures
4. **Tailwind Only** - No inline styles, no CSS modules
5. **User Experience** - Loading states, error messages, success feedback
6. **Accessibility** - Keyboard navigation, ARIA labels, screen reader support

---

## Common Pitfalls to Avoid

❌ **Don't use direct `fetch()` calls** - Use the centralized API client
❌ **Don't use inline styles** - Use Tailwind CSS classes
❌ **Don't mix server and client logic** - Separate concerns clearly
❌ **Don't hardcode API URLs** - Use environment variables
❌ **Don't skip loading states** - Always show feedback during async operations

---

## Additional Resources

- **Next.js App Router Docs:** https://nextjs.org/docs/app
- **Better Auth Docs:** https://www.better-auth.com/docs
- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **Phase 2 Backend Architecture:** `../specs/002-phase2-fullstack-web/00-backend-architecture.md`
- **Frontend Design Flow:** `../specs/002-phase2-fullstack-web/08-frontend-design-flow.md`

---

**Last Updated:** 2025-12-26
**Maintained By:** Phase 2 Implementation Team
