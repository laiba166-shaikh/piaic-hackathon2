# UI Redesign Plan — Task Mate

**Date:** 2026-04-05  
**Branch:** 002-phase2-fullstack-web  
**Reference files:** `UI_inspiration/Login.png`, `UI_inspiration/Signup.png`, `UI_inspiration/Dashbaord.png`, `UI_inspiration/color-theme.txt`, `UI_inspiration/design_notes.txt`

---

## 1. Summary of Changes

The current UI uses a vintage/journal aesthetic (cream paper, sepia, ink) with no dark mode support. The redesign replaces this with a modern blue/navy design system matching the reference screenshots, with full light/dark mode.

### What changes
- `globals.css` — replace vintage utilities with CSS custom property tokens
- `tailwind.config.ts` — replace vintage palette with semantic tokens + enable `darkMode: 'class'`
- `app/layout.tsx` — update fonts, add ThemeScript for flash prevention
- `app/(auth)/layout.tsx` — remove centering wrapper (each auth page handles its own layout)
- `app/(auth)/login/page.tsx` — complete rewrite to split-pane layout
- `app/(auth)/register/page.tsx` — complete rewrite to split-pane layout
- `app/(dashboard)/layout.tsx` — no structural change, classes updated
- `app/(dashboard)/page.tsx` — complete rewrite: stats cards + filter tabs + task list
- `components/layout/Sidebar.tsx` — dark blue sidebar, logo, Tasks + disabled Task Mate AI nav
- `components/layout/Header.tsx` — personalized title, user avatar chip, dark mode toggle
- `components/auth/LoginForm.tsx` — update styling to new tokens
- `components/auth/RegisterForm.tsx` — split name → First Name + Last Name inputs (concatenated), new styling
- `components/tasks/TasksPageClient.tsx` — add filter state + filter logic + stats computation
- `components/tasks/TaskCard.tsx` — new design: circular checkbox, strikethrough, Completed badge
- `components/tasks/TaskList.tsx` — update loading/error/empty state styling; filter tabs live in TasksPageClient
- `components/tasks/TaskForm.tsx` — update styling to new tokens
- `components/ui/Button.tsx` — update color tokens
- `components/ui/Input.tsx` — update color tokens + dark mode
- `components/ui/Modal.tsx` — update color tokens + dark mode
- `components/ui/Card.tsx` — update color tokens + dark mode

### What does NOT change
- All business logic (auth flow, JWT storage, API calls)
- Component props/interfaces — kept identical
- Test files
- Backend, CLI, database

### New files to create
- `contexts/ThemeContext.tsx` — ThemeProvider + useTheme hook
- `components/layout/ThemeToggle.tsx` — sun/moon icon toggle button

---

## 2. Color System

### Source: `UI_inspiration/color-theme.txt`

The new color system uses HSL CSS custom properties, with `:root` (light) and `.dark` overrides.

#### Light mode tokens
```css
--background: 210 33% 98%       /* near-white page bg */
--foreground: 203 47% 12%       /* dark navy text */
--card: 0 0% 100%               /* pure white card bg */
--card-foreground: 203 47% 12%
--primary: 209 78% 48%          /* #1B7FDC — main brand blue */
--primary-foreground: 0 0% 100%
--secondary: 205 55% 93%
--secondary-foreground: 205 92% 22%
--muted: 205 30% 95%
--muted-foreground: 205 30% 45%
--accent: 188 88% 44%           /* #0DB8D3 — cyan */
--accent-foreground: 0 0% 100%
--destructive: 0 84.2% 60.2%
--destructive-foreground: 0 0% 100%
--border: 205 35% 87%
--input: 205 35% 87%
--ring: 188 88% 44%
--radius: 0.5rem
--sidebar-background: 205 92% 31%   /* #065B98 — dark navy sidebar */
--sidebar-foreground: 205 60% 92%
--sidebar-primary: 188 88% 44%      /* #0DB8D3 — active item cyan */
--sidebar-primary-foreground: 203 47% 12%
--sidebar-accent: 205 80% 25%
--sidebar-accent-foreground: 205 60% 92%
--sidebar-border: 205 70% 26%
--sidebar-ring: 188 88% 44%
```

#### Dark mode tokens (under `.dark` class on `<html>`)
```css
--background: 203 47% 10%       /* deep navy */
--foreground: 205 40% 92%
--card: 203 47% 15%
--card-foreground: 205 40% 92%
--primary: 188 88% 44%          /* cyan leads in dark */
--primary-foreground: 203 47% 10%
--secondary: 203 47% 19%
--secondary-foreground: 205 40% 88%
--muted: 203 40% 21%
--muted-foreground: 205 30% 60%
--accent: 209 78% 55%           /* blue becomes accent in dark */
--accent-foreground: 0 0% 100%
--destructive: 0 62.8% 40%
--destructive-foreground: 0 0% 100%
--border: 205 40% 24%
--input: 203 47% 19%
--ring: 188 88% 44%
--sidebar-background: 203 55% 7%
--sidebar-foreground: 205 40% 88%
--sidebar-primary: 188 88% 44%
--sidebar-primary-foreground: 203 47% 10%
--sidebar-accent: 203 47% 16%
--sidebar-accent-foreground: 205 40% 88%
--sidebar-border: 205 40% 18%
--sidebar-ring: 188 88% 44%
```

### Tailwind color mapping
In `tailwind.config.ts`, map these variables to Tailwind color names using `hsl(var(--xxx))`:

```ts
colors: {
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  card: {
    DEFAULT: "hsl(var(--card))",
    foreground: "hsl(var(--card-foreground))",
  },
  primary: {
    DEFAULT: "hsl(var(--primary))",
    foreground: "hsl(var(--primary-foreground))",
  },
  secondary: {
    DEFAULT: "hsl(var(--secondary))",
    foreground: "hsl(var(--secondary-foreground))",
  },
  muted: {
    DEFAULT: "hsl(var(--muted))",
    foreground: "hsl(var(--muted-foreground))",
  },
  accent: {
    DEFAULT: "hsl(var(--accent))",
    foreground: "hsl(var(--accent-foreground))",
  },
  destructive: {
    DEFAULT: "hsl(var(--destructive))",
    foreground: "hsl(var(--destructive-foreground))",
  },
  border: "hsl(var(--border))",
  input: "hsl(var(--input))",
  ring: "hsl(var(--ring))",
  sidebar: {
    background: "hsl(var(--sidebar-background))",
    foreground: "hsl(var(--sidebar-foreground))",
    primary: "hsl(var(--sidebar-primary))",
    "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
    accent: "hsl(var(--sidebar-accent))",
    "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
    border: "hsl(var(--sidebar-border))",
    ring: "hsl(var(--sidebar-ring))",
  },
}
```

Also add `darkMode: 'class'` at the top level of the Tailwind config.

Keep `borderRadius` using `--radius`:
```ts
borderRadius: {
  lg: "var(--radius)",
  md: "calc(var(--radius) - 2px)",
  sm: "calc(var(--radius) - 4px)",
}
```

Remove all legacy vintage colors (`paper`, `ink`, `vintage`, `sepia`, `accent.gold`).

---

## 3. Dark Mode Infrastructure

### File: `contexts/ThemeContext.tsx` (NEW)

```tsx
"use client";
import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "light",
  toggleTheme: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    const initial = stored ?? preferred;
    setTheme(initial);
    document.documentElement.classList.toggle("dark", initial === "dark");
  }, []);

  function toggleTheme() {
    setTheme((prev) => {
      const next = prev === "light" ? "dark" : "light";
      localStorage.setItem("theme", next);
      document.documentElement.classList.toggle("dark", next === "dark");
      return next;
    });
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
```

### File: `components/layout/ThemeToggle.tsx` (NEW)

A button that reads `useTheme()` and renders a sun icon (light) or moon icon (dark).  
Use `aria-label="Toggle dark mode"`.

### File: `app/layout.tsx` (UPDATE)

- Add `ThemeProvider` wrapping `{children}` inside `<body>`
- Add an inline `<script>` before `{children}` to apply the `dark` class before first paint (prevents flash):
  ```html
  <script dangerouslySetInnerHTML={{ __html: `
    (function(){
      var t = localStorage.getItem('theme');
      var d = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (t === 'dark' || (!t && d)) document.documentElement.classList.add('dark');
    })()
  `}} />
  ```
- Update metadata: `title: "Task Mate"`, `description: "Organise your thoughts and tasks"`
- Keep Inter font, drop Patrick Hand and Courier Prime (no longer needed)
- Change `<body>` base class: `bg-background text-foreground antialiased`

---

## 4. Pipeline: Ordered Tasks

Execute in this exact order. Each task depends on the previous phase being complete.

---

### PHASE 1 — Design Tokens & Dark Mode Foundation
> All subsequent phases depend on this. Complete entirely before moving on.

#### Task 1.1 — Update `globals.css`
**File:** `src/core/frontend/app/globals.css`

Replace the entire file contents with:
1. `@import "tailwindcss";`
2. `@layer base { :root { ... } .dark { ... } }` — paste all CSS variables from `color-theme.txt`
3. `body { background: hsl(var(--background)); color: hsl(var(--foreground)); font-family: Inter, system-ui, sans-serif; }`
4. Remove all old `.bg-paper-cream`, `.text-ink-black`, `.bg-vintage-blue`, etc. custom utility classes.

#### Task 1.2 — Update `tailwind.config.ts`
**File:** `src/core/frontend/tailwind.config.ts`

Full rewrite:
- Add `darkMode: 'class'`
- Replace `theme.extend.colors` with the CSS variable mapping from Section 2
- Replace `borderRadius` with `--radius`-based values
- Remove `boxShadow.journal` and `boxShadow.journal-lg`
- Keep `fontFamily.sans: ["Inter", "system-ui", "sans-serif"]` only; remove Patrick Hand and Courier Prime

#### Task 1.3 — Create `contexts/ThemeContext.tsx`
**File:** `src/core/frontend/contexts/ThemeContext.tsx` (NEW)

Implement as specified in Section 3.

#### Task 1.4 — Create `components/layout/ThemeToggle.tsx`
**File:** `src/core/frontend/components/layout/ThemeToggle.tsx` (NEW)

Sun/moon toggle button using `useTheme()`. No text, icon only, `aria-label="Toggle dark mode"`.

SVG icons:
- Sun: `<circle cx="12" cy="12" r="5"/>` + 8 radial lines at 45° increments
- Moon: crescent shape using two overlapping circles

Tailwind classes: `p-2 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent transition-colors`

#### Task 1.5 — Update `app/layout.tsx`
**File:** `src/core/frontend/app/layout.tsx`

- Import `ThemeProvider` from `@/contexts/ThemeContext`
- Keep only `Inter` font import, remove `Patrick_Hand` and `Courier_Prime`
- Update metadata title to `"Task Mate"`
- Add anti-flash inline script before `{children}`
- Wrap `{children}` with `<ThemeProvider>`
- Update body classes: `${inter.variable} antialiased bg-background text-foreground`

---

### PHASE 2 — Auth Pages
> Depends on Phase 1. Implement login page, then register page.

#### Task 2.1 — Update `app/(auth)/layout.tsx`
**File:** `src/core/frontend/app/(auth)/layout.tsx`

Change to a passthrough layout — remove centering wrappers. Each auth page handles its own split layout:

```tsx
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
```

#### Task 2.2 — Rewrite `app/(auth)/login/page.tsx`
**File:** `src/core/frontend/app/(auth)/login/page.tsx`

**Reference:** `UI_inspiration/Login.png`

Layout: `min-h-screen flex` (full screen, no scroll)

**Left pane** (40% width, `w-2/5`):
- Background: `bg-sidebar-background`
- Contains:
  - Top: logo icon (a small white hexagon/diamond shape — use a simple `<div>` with border or SVG) + "Task Mate" text in `text-sidebar-foreground font-semibold text-xl`
  - Middle: bold heading `"Clarity for every task ahead"` in `text-white font-bold text-3xl`
  - Subtitle: `"Organise your day, track your progress, and get things done — all in one place."` in `text-sidebar-foreground/70 text-base`
  - Bottom: motivational quote `"The secret of getting ahead is getting started."` in small italic text + 3 dot pagination indicators (first dot filled/white, others muted)

**Right pane** (60% width, `w-3/5`):
- Background: `bg-background`
- Vertically centered content
- Contains:
  - Heading: `"Welcome back"` in `text-foreground font-semibold text-3xl`
  - Subheading: `"Sign in to continue to Task Mate"` in `text-muted-foreground`
  - `<LoginForm />` component
  - Below form: `"New here?"` + `<Link href="/register">Create an account</Link>` in `text-primary font-semibold`

#### Task 2.3 — Update `components/auth/LoginForm.tsx`
**File:** `src/core/frontend/components/auth/LoginForm.tsx`

Keep all logic identical. Update only styling:

- Label: `text-xs font-semibold uppercase tracking-wide text-foreground`
- Input: `w-full px-4 py-3 border border-border bg-card text-foreground rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent placeholder:text-muted-foreground`
- Submit button: `w-full bg-card border border-border text-foreground font-bold py-3 px-4 rounded-lg hover:bg-muted transition-colors disabled:opacity-50`
  - Note: per reference, the Sign In button is outlined/white style, not filled blue
- "Forgot password?" link: `text-sm text-muted-foreground hover:text-primary text-right block mt-1` (add this as a non-functional link between password field and submit button)
- Keep `<ErrorMessage>` at top of form

#### Task 2.4 — Rewrite `app/(auth)/register/page.tsx`
**File:** `src/core/frontend/app/(auth)/register/page.tsx`

**Reference:** `UI_inspiration/Signup.png`

Same split-pane structure as login (40/60).

**Left pane:**
- Same logo + "Task Mate" at top
- Bold heading: `"Your productivity, organised"`
- Subtitle: `"Join Task Mate and start building your focused, clutter-free workflow today."`
- Bottom: two stat cards side by side:
  - Card 1: `"2k+"` bold + `"Active users"` small text — `bg-sidebar-accent rounded-lg p-3`
  - Card 2: `"4.9★"` bold + `"User rating"` small text — `bg-sidebar-accent rounded-lg p-3`
- Below stats: 3 dot pagination (second dot filled)

**Right pane:**
- Heading: `"Create account"`
- Subheading: `"Get started — it's completely free"`
- `<RegisterForm />` component
- Below form: `"Already a member?"` + `<Link href="/login">Sign in</Link>` in `text-primary font-semibold`

#### Task 2.5 — Update `components/auth/RegisterForm.tsx`
**File:** `src/core/frontend/components/auth/RegisterForm.tsx`

**Logic change:** Split `name` field into `firstName` + `lastName` inputs. Concatenate as `name: \`${firstName.trim()} ${lastName.trim()}\`` when calling `authClient.signUp.email()`. Keep all existing validation/error/loading logic.

**UI layout change:**
- First row: two inputs side by side (`flex gap-4`): First Name + Last Name
- Second row: Email Address (full width)
- Third row: Password (full width, with toggle)
- Fourth row: Confirm Password (full width, with toggle)
- Remove password strength indicator (simplify)
- Labels: `text-xs font-semibold uppercase tracking-wide text-foreground`
- Inputs: same style as LoginForm inputs
- Submit button: `"Create my account"` — same outlined style as Sign In button

---

### PHASE 3 — Dashboard Layout (Sidebar + Header)
> Depends on Phase 1. Can run in parallel with Phase 2.

#### Task 3.1 — Rewrite `components/layout/Sidebar.tsx`
**File:** `src/core/frontend/components/layout/Sidebar.tsx`

**Reference:** `UI_inspiration/Dashbaord.png` (left panel)

```
aside classes: w-[260px] bg-sidebar-background flex flex-col h-screen
```

Structure:
1. **Logo area** (top, `p-5`):
   - Logo icon: small white rounded square with diamond/hexagon SVG icon — `bg-white/20 rounded-lg p-2 w-10 h-10 flex items-center justify-center`
   - "Task Mate" text: `text-sidebar-foreground font-semibold text-xl ml-3`
   - Wrap both in `flex items-center`

2. **Navigation** (`mt-8 px-3 space-y-1`):
   - **Tasks link** (`href="/"`):
     - Active state (when `pathname === "/"` or `pathname.startsWith("/tasks")`):
       `flex items-center gap-3 px-4 py-3 rounded-lg bg-sidebar-accent text-sidebar-foreground font-medium`
     - Inactive: `flex items-center gap-3 px-4 py-3 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent/50 transition-colors`
     - Icon: 2x2 grid squares SVG (dashboard icon)
     - Label: "Tasks"

   - **Task Mate AI** (disabled, NOT a link):
     - `flex items-center gap-3 px-4 py-3 rounded-lg text-sidebar-foreground/30 cursor-not-allowed`
     - Same grid icon (slightly different or identical)
     - Label: "Task Mate AI"
     - Note: Design notes say "Task Mate AI should be disabled for now"

3. **Spacer:** `flex-1`

4. **Bottom area** (optional): dark mode toggle could live here or in header

#### Task 3.2 — Rewrite `components/layout/Header.tsx`
**File:** `src/core/frontend/components/layout/Header.tsx`

**Reference:** `UI_inspiration/Dashbaord.png` (top bar)

Make `"use client"` (needs auth context for user name + useTheme).

Import `useAuth` from `@/contexts/AuthContext` and `useTheme` from `@/contexts/ThemeContext`.

```
header classes: bg-background border-b border-border px-6 py-4 flex items-center justify-between
```

Structure:
- **Left:** `"{user.name}'s Task Mate"` — derive from auth session. If user name unavailable, fall back to `"Task Mate"`.  
  Class: `text-foreground font-semibold text-lg`
- **Right:** flex row with:
  - `<ThemeToggle />` component
  - User avatar chip: circle with first initial of user's name  
    `w-9 h-9 rounded-full bg-muted flex items-center justify-center text-foreground font-semibold text-sm ml-3`

---

### PHASE 4 — Dashboard Page (Main Content)
> Depends on Phases 1, 2, 3.

#### Task 4.1 — Rewrite `app/(dashboard)/page.tsx`
**File:** `src/core/frontend/app/(dashboard)/page.tsx`

**Reference:** `UI_inspiration/Dashbaord.png`

Change this from a placeholder to the full task management page. Import and render `<TasksPageClient />`.

```tsx
import { TasksPageClient } from "@/components/tasks/TasksPageClient";

export default function Home() {
  return <TasksPageClient />;
}
```

#### Task 4.2 — Rewrite `components/tasks/TasksPageClient.tsx`
**File:** `src/core/frontend/components/tasks/TasksPageClient.tsx`

**Reference:** `UI_inspiration/Dashbaord.png`

Keep all existing API logic (loadTasks, handleCreateTask, handleUpdateTask, handleDeleteTask, openEditModal, openDeleteModal) exactly as-is.

Add filter state:
```tsx
type FilterType = "all" | "today" | "todo" | "done";
const [activeFilter, setActiveFilter] = useState<FilterType>("all");
```

Add filter logic:
```tsx
const today = new Date().toDateString();
const filteredTasks = tasks.filter((t) => {
  if (activeFilter === "today") return new Date(t.created_at).toDateString() === today;
  if (activeFilter === "todo") return !t.completed;
  if (activeFilter === "done") return t.completed;
  return true; // "all"
});
```

Add computed stats:
```tsx
const totalCount = tasks.length;
const completedCount = tasks.filter((t) => t.completed).length;
const remainingCount = totalCount - completedCount;
```

**Rendered layout** (replaces current return):

```
<div className="h-full flex flex-col">
  
  {/* Stats row */}
  <div className="grid grid-cols-3 gap-4 mb-6">
    {/* Total Tasks card */}
    {/* Completed card */}  
    {/* Remaining card */}
  </div>

  {/* Page header row */}
  <div className="flex items-start justify-between mb-4">
    <div>
      <h1 className="text-2xl font-semibold text-foreground">Task Mate</h1>
      <p className="text-muted-foreground text-sm">Organise your thoughts and tasks</p>
      <p className="text-muted-foreground text-sm mt-0.5">
        {new Date().toLocaleDateString("en-US", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
      </p>
    </div>
    <button onClick={() => setIsCreateModalOpen(true)}
      className="flex items-center gap-2 px-5 py-2.5 border border-border rounded-lg text-foreground font-semibold hover:bg-muted transition-colors">
      + Create Task
    </button>
  </div>

  {/* Filter tabs */}
  <div className="flex gap-2 mb-4">
    {(["all","today","todo","done"] as FilterType[]).map((f) => (
      <button key={f} onClick={() => setActiveFilter(f)}
        className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors border ${
          activeFilter === f
            ? "bg-foreground text-background border-foreground"
            : "bg-transparent text-foreground border-border hover:bg-muted"
        }`}>
        {f === "all" ? "All" : f === "today" ? "Today" : f === "todo" ? "To Do" : "Done"}
      </button>
    ))}
  </div>

  {/* Task list */}
  <TaskList tasks={filteredTasks} loading={loading} error={error}
    onEdit={openEditModal} onDelete={openDeleteModal} />

  {/* Modals — keep exactly as before */}
</div>
```

**Stats card design** (per reference — white card, large number, label, progress bar):
```tsx
function StatCard({ label, value, total, color }: { label: string; value: number; total: number; color: string }) {
  const pct = total > 0 ? (value / total) * 100 : 0;
  return (
    <div className="bg-card rounded-xl p-5 border border-border">
      <p className="text-3xl font-bold text-foreground">{value}</p>
      <p className="text-muted-foreground text-sm mt-1">{label}</p>
      <div className="mt-3 h-1 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
```
- Total Tasks: `color="bg-primary"`, `value=totalCount`, `total=totalCount` (bar always full)
- Completed: `color="bg-accent"`, `value=completedCount`, `total=totalCount`
- Remaining: `color="bg-primary"`, `value=remainingCount`, `total=totalCount`

#### Task 4.3 — Rewrite `components/tasks/TaskCard.tsx`
**File:** `src/core/frontend/components/tasks/TaskCard.tsx`

**Reference:** `UI_inspiration/Dashbaord.png` (task row)

The task row design:
- Full-width white card with border: `bg-card rounded-xl border border-border p-4 flex items-center gap-4`
- **Left:** Circular checkbox/checkmark
  - Completed: `w-8 h-8 rounded-full bg-accent/20 border-2 border-accent flex items-center justify-center` with a white checkmark SVG inside
  - Incomplete: `w-8 h-8 rounded-full border-2 border-border` (empty circle, no fill)
  - The checkbox is NOT clickable in this redesign (toggle is done via edit). Keep it visual only unless the `onToggle` prop is passed.
- **Middle** (`flex-1 min-w-0`):
  - Task name: 
    - Completed: `text-muted-foreground line-through text-base` 
    - Incomplete: `text-foreground text-base font-medium`
  - Below name: date + badge row:
    - Date: `text-sm text-muted-foreground` — format as "5 Apr 2026"
    - If completed: `<span className="ml-2 px-2 py-0.5 rounded-full bg-accent/15 text-accent text-xs font-medium">Completed</span>`
- **Right** (`flex gap-2 ml-auto shrink-0`):
  - Edit button: `p-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:border-primary transition-colors`
    - Pencil icon SVG
  - Delete button: `p-2 rounded-lg border border-border text-muted-foreground hover:text-destructive hover:border-destructive transition-colors`
    - Trash icon SVG

Remove description display from card (keep it in the edit modal form only, as the reference design doesn't show descriptions in the list).

Keep `onEdit` and `onDelete` prop interfaces unchanged.

#### Task 4.4 — Update `components/tasks/TaskList.tsx`
**File:** `src/core/frontend/components/tasks/TaskList.tsx`

Keep props and logic identical. Update only class names:

**Loading skeleton:**
```tsx
<div className="bg-card rounded-xl border border-border p-4 animate-pulse">
  <div className="h-5 bg-muted rounded w-3/4 mb-2" />
  <div className="h-4 bg-muted rounded w-1/3" />
</div>
```

**Error state:**
```tsx
<div className="bg-destructive/10 border border-destructive/30 rounded-xl p-6 text-center">
  <p className="text-destructive font-medium">{error}</p>
</div>
```

**Empty state:**
```tsx
<div className="bg-card rounded-xl border border-border p-12 text-center">
  {/* clipboard SVG icon in text-muted-foreground */}
  <h3 className="text-foreground font-medium text-lg mb-1">No tasks yet</h3>
  <p className="text-muted-foreground text-sm">Click "Create Task" to add your first task.</p>
</div>
```

---

### PHASE 5 — UI Primitives
> Can run in parallel with Phase 4. Depends only on Phase 1.

#### Task 5.1 — Update `components/ui/Button.tsx`
**File:** `src/core/frontend/components/ui/Button.tsx`

Replace vintage color tokens with new tokens. Keep same interface and variants:

```tsx
const variantStyles = {
  primary:   "bg-primary text-primary-foreground hover:bg-primary/90 focus:ring-primary",
  secondary: "border border-border text-foreground hover:bg-muted focus:ring-ring",
  danger:    "bg-destructive text-destructive-foreground hover:bg-destructive/90 focus:ring-destructive",
  ghost:     "text-primary hover:bg-primary/10 focus:ring-primary",
};
const baseStyles = "rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
```

#### Task 5.2 — Update `components/ui/Input.tsx`
**File:** `src/core/frontend/components/ui/Input.tsx`

```tsx
// label class:
"block text-sm font-medium text-foreground"

// input class (normal):
"w-full px-3 py-2 border border-input bg-background text-foreground rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent placeholder:text-muted-foreground transition-colors"

// input class (error state):
"border-destructive bg-destructive/10"

// error text:
"text-destructive text-sm"

// helper text:
"text-muted-foreground text-sm"
```

#### Task 5.3 — Update `components/ui/Modal.tsx`
**File:** `src/core/frontend/components/ui/Modal.tsx`

```tsx
// backdrop: keep "fixed inset-0 bg-black/50 backdrop-blur-sm"

// modal container:
"relative bg-card text-card-foreground rounded-xl shadow-xl max-w-md w-full border border-border"

// header:
"flex justify-between items-center p-6 border-b border-border"

// title:
"text-xl font-semibold text-foreground"

// close button:
"text-muted-foreground hover:text-foreground transition-colors"
```

#### Task 5.4 — Update `components/ui/Card.tsx`
**File:** `src/core/frontend/components/ui/Card.tsx`

Update container to use: `bg-card text-card-foreground border border-border rounded-xl shadow-sm`

#### Task 5.5 — Update `components/tasks/TaskForm.tsx`
**File:** `src/core/frontend/components/tasks/TaskForm.tsx`

Update input/textarea/button classes to use new tokens:
- Inputs: `border-input bg-background text-foreground focus:ring-ring`
- Cancel button: `border-border text-foreground hover:bg-muted`
- Submit button: `bg-primary text-primary-foreground hover:bg-primary/90`
- Error state: `border-destructive bg-destructive/10`

---

## 5. File Change Summary Table

| File | Type | Phase |
|------|------|-------|
| `app/globals.css` | Full rewrite | 1.1 |
| `tailwind.config.ts` | Full rewrite | 1.2 |
| `contexts/ThemeContext.tsx` | NEW | 1.3 |
| `components/layout/ThemeToggle.tsx` | NEW | 1.4 |
| `app/layout.tsx` | Update | 1.5 |
| `app/(auth)/layout.tsx` | Update (passthrough) | 2.1 |
| `app/(auth)/login/page.tsx` | Full rewrite | 2.2 |
| `components/auth/LoginForm.tsx` | Style update | 2.3 |
| `app/(auth)/register/page.tsx` | Full rewrite | 2.4 |
| `components/auth/RegisterForm.tsx` | Style + name split | 2.5 |
| `components/layout/Sidebar.tsx` | Full rewrite | 3.1 |
| `components/layout/Header.tsx` | Full rewrite | 3.2 |
| `app/(dashboard)/page.tsx` | Full rewrite | 4.1 |
| `components/tasks/TasksPageClient.tsx` | Add filters + stats | 4.2 |
| `components/tasks/TaskCard.tsx` | Full rewrite | 4.3 |
| `components/tasks/TaskList.tsx` | Style update | 4.4 |
| `components/ui/Button.tsx` | Style update | 5.1 |
| `components/ui/Input.tsx` | Style update | 5.2 |
| `components/ui/Modal.tsx` | Style update | 5.3 |
| `components/ui/Card.tsx` | Style update | 5.4 |
| `components/tasks/TaskForm.tsx` | Style update | 5.5 |

**Total:** 19 files modified, 2 new files created.

---

## 6. Design Notes Compliance Checklist

- [ ] Task Mate AI nav item exists in sidebar but is visually disabled (non-clickable, low opacity)
- [ ] Login/Register form on the 60% right pane (right `w-3/5` column)
- [ ] Colors match `color-theme.txt` exactly — primary `#1B7FDC`, accent/cyan `#0DB8D3`, sidebar `#065B98`
- [ ] Dark mode: primary swaps to cyan (`#0DB8D3`), accent becomes blue (`#1B7FDC`) — handled by CSS variables
- [ ] Task fields displayed: name, date, completed status badge only (no priority, no tags)
- [ ] Filter "All" → all tasks
- [ ] Filter "Today" → `created_at` date equals today's date
- [ ] Filter "To Do" → `completed === false`
- [ ] Filter "Done" → `completed === true`

---

## 7. Constraints & Non-Goals

- **DO NOT** change any API call, auth logic, JWT storage, or hook behavior
- **DO NOT** modify test files (`__tests__/`)
- **DO NOT** add new npm packages (use only Tailwind + Next.js built-ins)
- **DO NOT** add task toggle on card click (no `onToggle` prop exists — status changes via edit modal only)
- **DO NOT** implement "Forgot password?" functionality (add the link visually as non-functional)
- **DO NOT** add router logic to `app/(dashboard)/tasks/page.tsx` or `app/(dashboard)/tasks/[id]/page.tsx` — leave those unchanged
- The `app/(dashboard)/tasks/page.tsx` and `tasks/[id]/page.tsx` pages are NOT part of this redesign

---

## 8. Execution Order for Subagent

```
Phase 1 (all 5 tasks) → must complete first
  ↓
Phase 2 + Phase 3 (can run in parallel, but Phase 2 before Phase 3 is fine)
  ↓  
Phase 4 (depends on 2+3)
  ↓
Phase 5 (can overlap with Phase 4)
```

The subagent should execute each task sequentially in phase order. Each task modifies exactly the files listed — no other files should be touched.
