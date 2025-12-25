# UI Design System - Journal/Diary Aesthetic

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-12-25
**Type:** Design Specification Document

---

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Color Palette](#color-palette)
4. [Typography](#typography)
5. [Layout & Grid System](#layout--grid-system)
6. [Spacing System](#spacing-system)
7. [Component Library](#component-library)
8. [Application Layout](#application-layout)
9. [Dashboard Design](#dashboard-design)
10. [Task List Design](#task-list-design)
11. [Interactive States](#interactive-states)
12. [Responsive Design](#responsive-design)
13. [Visual Examples](#visual-examples)
14. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

This design system defines the visual language, UI components, and layout patterns for the Phase 2 task management application. The design follows a **journal/diary aesthetic**, creating an intimate, personal, and reflective user experience that feels like writing in a cherished notebook.

### Design Goals

1. **Emotional Connection** - Create a warm, personal experience that feels like journaling
2. **Readability** - Ensure text is comfortable to read with serif fonts and paper-like backgrounds
3. **Simplicity** - Keep UI elements minimal and unobtrusive, like a physical diary
4. **Consistency** - Maintain cohesive visual language across all pages
5. **Usability** - Balance aesthetics with functional, accessible interactions

### Target Audience

- Users who value personal task management with a reflective, mindful approach
- Users who appreciate analog aesthetics in digital interfaces
- Users seeking a calming, distraction-free task management experience

---

## Design Philosophy

### Journal/Diary Concept

The application should evoke the experience of **writing in a personal hardcover journal**:

- **Paper Texture** - Warm, cream-colored backgrounds reminiscent of aged notebook paper
- **Ink Colors** - Deep blue-black and sepia tones like fountain pen ink
- **Typography** - Serif fonts that feel handwritten yet readable
- **Subtle Details** - Faint ruled lines, soft shadows, and paper-like textures
- **Intimate Spacing** - Generous whitespace that feels calm and uncluttered
- **Minimal Chrome** - Avoid heavy UI "chrome" (borders, buttons) in favor of simplicity

### Emotional Touchpoints

**Primary Emotion:** Calm reflection and mindful productivity

**Secondary Emotions:**
- Warmth (through color palette)
- Nostalgia (through analog references)
- Comfort (through familiar patterns)
- Focus (through minimal distractions)

### Design Inspirations

- Physical Moleskine notebooks
- Vintage diary entries
- Classic letterpress printing
- Japanese stationery (simplicity + elegance)
- Mid-century office aesthetics

---

## Color Palette

### Primary Colors

| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| **Paper Cream** | `#F5F1E8` | `bg-[#F5F1E8]` | Main background, page surface |
| **Ink Black** | `#2C3E50` | `text-[#2C3E50]` | Primary text, headings |
| **Sepia Brown** | `#8B7355` | `text-[#8B7355]` | Secondary text, labels |
| **Warm Gray** | `#D4CFC4` | `border-[#D4CFC4]` | Borders, dividers, subtle lines |

### Accent Colors

| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| **Vintage Blue** | `#4A7C99` | `bg-[#4A7C99]` | Primary actions, links, Create button |
| **Rust Orange** | `#C45D3F` | `bg-[#C45D3F]` | Delete, warnings, destructive actions |
| **Olive Green** | `#6B7F5B` | `bg-[#6B7F5B]` | Success states, completed tasks |
| **Lavender** | `#9B8FA8` | `bg-[#9B8FA8]` | Hover states, secondary actions |

### Semantic Colors

| Semantic Use | Color | Hex Code | Tailwind Class |
|--------------|-------|----------|----------------|
| **Success** | Olive Green | `#6B7F5B` | `text-[#6B7F5B]` |
| **Error** | Rust Orange | `#C45D3F` | `text-[#C45D3F]` |
| **Warning** | Amber | `#D4A574` | `text-[#D4A574]` |
| **Info** | Vintage Blue | `#4A7C99` | `text-[#4A7C99]` |

### Color Usage Guidelines

**Do:**
- Use Paper Cream (#F5F1E8) as the primary background
- Use Ink Black (#2C3E50) for primary text
- Use Vintage Blue (#4A7C99) for primary actions
- Use Warm Gray (#D4CFC4) for subtle borders and dividers

**Don't:**
- Use pure white (#FFFFFF) - feels too digital
- Use pure black (#000000) - feels too harsh
- Use bright neon colors - breaks the journal aesthetic
- Use gradients or heavy shadows - keep it flat and paper-like

---

## Typography

### Font Families

**Primary Font (Body Text):**
- **Font Name:** Crimson Text (serif)
- **Fallback:** Georgia, 'Times New Roman', serif
- **Character:** Classic, readable serif with elegant proportions
- **Use Cases:** Body text, task descriptions, paragraphs

**Secondary Font (Headings):**
- **Font Name:** Playfair Display (serif)
- **Fallback:** Georgia, serif
- **Character:** High-contrast serif with distinctive personality
- **Use Cases:** Page headings, modal titles, emphasis

**Monospace Font (Optional):**
- **Font Name:** Courier Prime (monospace)
- **Fallback:** 'Courier New', monospace
- **Character:** Typewriter aesthetic
- **Use Cases:** Timestamps, metadata, code-like elements

### Font Configuration (Tailwind)

```typescript
// tailwind.config.ts
import { type Config } from 'tailwindcss'

export default {
  theme: {
    extend: {
      fontFamily: {
        'body': ['Crimson Text', 'Georgia', 'Times New Roman', 'serif'],
        'heading': ['Playfair Display', 'Georgia', 'serif'],
        'mono': ['Courier Prime', 'Courier New', 'monospace'],
      },
    },
  },
} satisfies Config
```

### Typography Scale

| Element | Font | Size | Weight | Line Height | Tailwind Classes |
|---------|------|------|--------|-------------|------------------|
| **Page Heading (h1)** | Playfair Display | 36px | 700 | 1.2 | `font-heading text-4xl font-bold` |
| **Section Heading (h2)** | Playfair Display | 28px | 600 | 1.3 | `font-heading text-3xl font-semibold` |
| **Subsection (h3)** | Playfair Display | 20px | 600 | 1.4 | `font-heading text-xl font-semibold` |
| **Body Text** | Crimson Text | 18px | 400 | 1.7 | `font-body text-lg leading-relaxed` |
| **Small Text** | Crimson Text | 16px | 400 | 1.6 | `font-body text-base` |
| **Labels** | Crimson Text | 14px | 500 | 1.5 | `font-body text-sm font-medium` |
| **Metadata** | Courier Prime | 13px | 400 | 1.4 | `font-mono text-xs` |

### Typography Examples

```html
<!-- Page Heading -->
<h1 class="font-heading text-4xl font-bold text-[#2C3E50]">
  Want todos
</h1>

<!-- Section Heading -->
<h2 class="font-heading text-3xl font-semibold text-[#2C3E50]">
  Today's Tasks
</h2>

<!-- Body Text -->
<p class="font-body text-lg leading-relaxed text-[#2C3E50]">
  This is body text that feels like writing in a journal.
</p>

<!-- Label -->
<label class="font-body text-sm font-medium text-[#8B7355]">
  Task Title
</label>

<!-- Timestamp -->
<span class="font-mono text-xs text-[#8B7355]">
  Created: Dec 25, 2025 at 3:45 PM
</span>
```

---

## Layout & Grid System

### Overall Application Layout

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────┐  ┌─────────────────────────────────────────┐ │
│  │          │  │         NAVBAR/HEADER                    │ │
│  │          │  │  (minimal, right-aligned elements)       │ │
│  │          │  └─────────────────────────────────────────┘ │
│  │          │                                               │
│  │          │  ┌─────────────────────────────────────────┐ │
│  │ SIDEBAR  │  │                                          │ │
│  │          │  │         MAIN CONTENT AREA                │ │
│  │ (left)   │  │                                          │ │
│  │          │  │  - Page Heading: "Want todos"            │ │
│  │ Tasks    │  │  - Filters                               │ │
│  │ (nav)    │  │  - Task List                             │ │
│  │          │  │                                          │ │
│  │          │  │                                          │ │
│  └──────────┘  └─────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Layout Specifications

**Sidebar:**
- Width: 240px (fixed)
- Background: Slightly darker cream (#EDE8DD)
- Position: Fixed left
- Contains: Navigation items (Tasks, etc.)

**Main Content Area:**
- Left margin: 240px (sidebar width)
- Max width: 1200px (centered)
- Padding: 48px horizontal, 32px vertical
- Background: Paper Cream (#F5F1E8)

**Header/Navbar:**
- Height: 64px
- Background: Transparent or very subtle
- Position: Top right (not full width)
- Contains: User menu, logout

### Grid System

Use **CSS Grid** for main layout structure, **Flexbox** for components.

**Container Widths:**

| Breakpoint | Min Width | Max Width | Container Class |
|------------|-----------|-----------|-----------------|
| Mobile | 0px | 639px | `max-w-full` |
| Tablet | 640px | 1023px | `max-w-3xl` |
| Desktop | 1024px+ | 1200px | `max-w-5xl` |

**Grid Columns:**

```typescript
// Task list grid (responsive)
<div class="grid grid-cols-1 gap-4">
  {/* Mobile: 1 column, all breakpoints single column for task list */}
</div>
```

---

## Spacing System

### Spacing Scale

Based on **8px base unit** for consistency:

| Name | Value | Tailwind Class | Usage |
|------|-------|----------------|-------|
| **xs** | 4px | `space-y-1` | Tight spacing (form field groups) |
| **sm** | 8px | `space-y-2` | Small gaps (labels to inputs) |
| **md** | 16px | `space-y-4` | Default spacing (between sections) |
| **lg** | 24px | `space-y-6` | Large spacing (between major sections) |
| **xl** | 32px | `space-y-8` | Extra large (page sections) |
| **2xl** | 48px | `space-y-12` | Generous spacing (page top margin) |

### Spacing Guidelines

**Vertical Rhythm:**
- Use consistent vertical spacing throughout
- Prefer `space-y-*` for stacked elements
- Maintain 1.5-2x spacing between sections

**Horizontal Spacing:**
- Sidebar padding: 24px
- Main content padding: 48px (desktop), 24px (mobile)
- Component padding: 16px-24px

**Example:**

```html
<div class="p-12"> <!-- 48px padding -->
  <h1 class="mb-6">Want todos</h1> <!-- 24px bottom margin -->

  <div class="space-y-4"> <!-- 16px between children -->
    <TaskCard />
    <TaskCard />
    <TaskCard />
  </div>
</div>
```

---

## Component Library

### Buttons

**Primary Button (Create Task)**

```html
<button class="
  px-6 py-2.5
  bg-[#4A7C99]
  text-white
  font-body text-base font-medium
  rounded-md
  shadow-sm
  hover:bg-[#3A6C89]
  focus:outline-none focus:ring-2 focus:ring-[#4A7C99] focus:ring-offset-2 focus:ring-offset-[#F5F1E8]
  transition-colors duration-200
">
  Create Task
</button>
```

**Secondary Button (Cancel)**

```html
<button class="
  px-6 py-2.5
  bg-transparent
  text-[#8B7355]
  font-body text-base font-medium
  border border-[#D4CFC4]
  rounded-md
  hover:bg-[#EDE8DD]
  focus:outline-none focus:ring-2 focus:ring-[#8B7355] focus:ring-offset-2
  transition-colors duration-200
">
  Cancel
</button>
```

**Destructive Button (Delete)**

```html
<button class="
  px-4 py-2
  bg-transparent
  text-[#C45D3F]
  font-body text-sm font-medium
  hover:bg-[#C45D3F] hover:text-white
  rounded-md
  transition-colors duration-200
">
  Delete
</button>
```

### Input Fields

**Text Input**

```html
<div>
  <label class="block font-body text-sm font-medium text-[#8B7355] mb-2">
    Task Title
  </label>
  <input
    type="text"
    class="
      w-full
      px-4 py-3
      bg-white
      border border-[#D4CFC4]
      rounded-md
      font-body text-lg text-[#2C3E50]
      placeholder:text-[#8B7355] placeholder:opacity-50
      focus:outline-none focus:border-[#4A7C99] focus:ring-2 focus:ring-[#4A7C99] focus:ring-opacity-20
      transition-colors duration-200
    "
    placeholder="Enter your task..."
  />
</div>
```

**Textarea**

```html
<textarea
  rows="4"
  class="
    w-full
    px-4 py-3
    bg-white
    border border-[#D4CFC4]
    rounded-md
    font-body text-base text-[#2C3E50] leading-relaxed
    placeholder:text-[#8B7355] placeholder:opacity-50
    focus:outline-none focus:border-[#4A7C99] focus:ring-2 focus:ring-[#4A7C99] focus:ring-opacity-20
    transition-colors duration-200
    resize-none
  "
  placeholder="Add details..."
></textarea>
```

### Cards

**Task Card**

```html
<div class="
  bg-white
  border border-[#D4CFC4]
  rounded-lg
  p-5
  shadow-sm
  hover:shadow-md
  transition-shadow duration-200
">
  <h3 class="font-heading text-xl font-semibold text-[#2C3E50] mb-2">
    Task Title
  </h3>
  <p class="font-body text-base text-[#8B7355] leading-relaxed mb-4">
    Task description goes here...
  </p>
  <div class="flex items-center justify-between">
    <span class="font-mono text-xs text-[#8B7355]">
      Created: Dec 25, 2025
    </span>
    <div class="flex gap-2">
      <button class="text-[#4A7C99] hover:underline text-sm">Edit</button>
      <button class="text-[#C45D3F] hover:underline text-sm">Delete</button>
    </div>
  </div>
</div>
```

### Modal Dialog

```html
<!-- Backdrop -->
<div class="fixed inset-0 bg-[#2C3E50] bg-opacity-40 z-40"></div>

<!-- Modal -->
<div class="
  fixed inset-0 z-50
  flex items-center justify-center
  p-4
">
  <div class="
    bg-[#F5F1E8]
    border-2 border-[#8B7355]
    rounded-lg
    shadow-2xl
    max-w-lg w-full
    p-8
  ">
    <div class="flex items-start justify-between mb-6">
      <h2 class="font-heading text-3xl font-semibold text-[#2C3E50]">
        Create New Task
      </h2>
      <button
        class="text-[#8B7355] hover:text-[#2C3E50] text-2xl leading-none"
        aria-label="Close modal"
      >
        ×
      </button>
    </div>

    <!-- Modal content -->
    <div class="space-y-6">
      <!-- Form fields go here -->
    </div>
  </div>
</div>
```

### Sidebar Navigation

```html
<aside class="
  fixed left-0 top-0 bottom-0
  w-60
  bg-[#EDE8DD]
  border-r border-[#D4CFC4]
  p-6
">
  <div class="mb-8">
    <h2 class="font-heading text-2xl font-bold text-[#2C3E50]">
      Journal
    </h2>
  </div>

  <nav>
    <ul class="space-y-2">
      <li>
        <a href="/tasks" class="
          block
          px-4 py-2.5
          font-body text-base
          text-[#2C3E50]
          rounded-md
          hover:bg-[#D4CFC4]
          transition-colors duration-200
        ">
          Tasks
        </a>
      </li>
      <!-- More nav items -->
    </ul>
  </nav>
</aside>
```

---

## Application Layout

### Root Layout Structure

```typescript
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#F5F1E8] font-body antialiased">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <div className="flex-1 ml-60"> {/* ml-60 = 240px sidebar width */}
            {/* Header */}
            <Header />

            {/* Page Content */}
            <main className="max-w-5xl mx-auto px-12 py-8">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
```

### Sidebar Component

```typescript
// components/layout/Sidebar.tsx
export function Sidebar() {
  return (
    <aside className="
      fixed left-0 top-0 bottom-0
      w-60
      bg-[#EDE8DD]
      border-r border-[#D4CFC4]
      overflow-y-auto
    ">
      <div className="p-6">
        {/* Logo/Brand */}
        <div className="mb-8">
          <h2 className="font-heading text-2xl font-bold text-[#2C3E50]">
            Journal
          </h2>
        </div>

        {/* Navigation */}
        <nav>
          <ul className="space-y-2">
            <li>
              <Link
                href="/tasks"
                className="
                  block px-4 py-2.5
                  font-body text-base text-[#2C3E50]
                  rounded-md
                  hover:bg-[#D4CFC4]
                  transition-colors duration-200
                "
              >
                Tasks
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </aside>
  );
}
```

### Header Component

```typescript
// components/layout/Header.tsx
export function Header() {
  return (
    <header className="
      h-16
      border-b border-[#D4CFC4]
      bg-[#F5F1E8]
    ">
      <div className="h-full max-w-5xl mx-auto px-12 flex items-center justify-end">
        <div className="flex items-center gap-4">
          {/* User Menu */}
          <span className="font-body text-sm text-[#8B7355]">
            user@example.com
          </span>
          <button className="
            px-4 py-2
            font-body text-sm text-[#8B7355]
            hover:text-[#2C3E50]
            transition-colors
          ">
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
```

---

## Dashboard Design

### Dashboard Layout

The main dashboard (`/tasks` page) contains:

1. **Page Heading** - "Want todos" (left-aligned)
2. **Create Task Button** - Right-aligned with heading
3. **Filters Section** - Below heading
4. **Task List** - Main content area

### Dashboard Structure

```typescript
// app/tasks/page.tsx
export default function TasksPage() {
  return (
    <div className="space-y-8">
      {/* Heading + Create Button */}
      <div className="flex items-center justify-between">
        <h1 className="font-heading text-4xl font-bold text-[#2C3E50]">
          Want todos
        </h1>
        <button className="
          px-6 py-2.5
          bg-[#4A7C99]
          text-white
          font-body text-base font-medium
          rounded-md
          shadow-sm
          hover:bg-[#3A6C89]
          transition-colors duration-200
        ">
          Create Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <FilterButton active>All</FilterButton>
        <FilterButton>Active</FilterButton>
        <FilterButton>Completed</FilterButton>
      </div>

      {/* Task List */}
      <div className="space-y-4">
        <TaskCard />
        <TaskCard />
        <TaskCard />
      </div>
    </div>
  );
}
```

### Filter Buttons

```html
<!-- Active Filter -->
<button class="
  px-4 py-2
  font-body text-sm font-medium
  text-[#2C3E50]
  bg-[#D4CFC4]
  rounded-md
  transition-colors duration-200
">
  All
</button>

<!-- Inactive Filter -->
<button class="
  px-4 py-2
  font-body text-sm font-medium
  text-[#8B7355]
  bg-transparent
  border border-[#D4CFC4]
  rounded-md
  hover:bg-[#EDE8DD]
  transition-colors duration-200
">
  Active
</button>
```

---

## Task List Design

### Task Card Variants

**Uncompleted Task**

```html
<div class="
  bg-white
  border border-[#D4CFC4]
  rounded-lg
  p-5
  shadow-sm
  hover:shadow-md
  transition-shadow duration-200
">
  <!-- Checkbox + Title -->
  <div class="flex items-start gap-3 mb-3">
    <input
      type="checkbox"
      class="
        mt-1 w-5 h-5
        border-2 border-[#D4CFC4]
        rounded
        text-[#6B7F5B]
        focus:ring-2 focus:ring-[#6B7F5B] focus:ring-offset-2
      "
    />
    <h3 class="flex-1 font-heading text-xl font-semibold text-[#2C3E50]">
      Write project proposal
    </h3>
  </div>

  <!-- Description -->
  <p class="font-body text-base text-[#8B7355] leading-relaxed mb-4 pl-8">
    Draft the initial proposal for the new client project, including timeline and budget.
  </p>

  <!-- Metadata + Actions -->
  <div class="flex items-center justify-between pl-8">
    <span class="font-mono text-xs text-[#8B7355]">
      Created: Dec 25, 2025 at 9:30 AM
    </span>
    <div class="flex gap-3">
      <button class="font-body text-sm text-[#4A7C99] hover:underline">
        Edit
      </button>
      <button class="font-body text-sm text-[#C45D3F] hover:underline">
        Delete
      </button>
    </div>
  </div>
</div>
```

**Completed Task**

```html
<div class="
  bg-white
  border border-[#D4CFC4]
  rounded-lg
  p-5
  shadow-sm
  opacity-60
">
  <div class="flex items-start gap-3 mb-3">
    <input
      type="checkbox"
      checked
      class="mt-1 w-5 h-5 text-[#6B7F5B]"
    />
    <h3 class="flex-1 font-heading text-xl font-semibold text-[#2C3E50] line-through">
      Review team meeting notes
    </h3>
  </div>

  <p class="font-body text-base text-[#8B7355] leading-relaxed mb-4 pl-8 line-through">
    Go through yesterday's meeting notes and extract action items.
  </p>

  <div class="flex items-center justify-between pl-8">
    <span class="font-mono text-xs text-[#6B7F5B]">
      Completed: Dec 25, 2025 at 11:15 AM
    </span>
    <button class="font-body text-sm text-[#C45D3F] hover:underline">
      Delete
    </button>
  </div>
</div>
```

### Empty State

```html
<div class="
  flex flex-col items-center justify-center
  py-20
  text-center
">
  <div class="mb-6">
    <svg class="w-24 h-24 text-[#D4CFC4]" fill="currentColor" viewBox="0 0 24 24">
      <!-- Icon SVG path -->
    </svg>
  </div>

  <h3 class="font-heading text-2xl font-semibold text-[#2C3E50] mb-2">
    No tasks yet
  </h3>

  <p class="font-body text-base text-[#8B7355] mb-6 max-w-md">
    Start your journal by creating your first task. What would you like to accomplish today?
  </p>

  <button class="
    px-6 py-2.5
    bg-[#4A7C99]
    text-white
    font-body text-base font-medium
    rounded-md
    shadow-sm
    hover:bg-[#3A6C89]
  ">
    Create Your First Task
  </button>
</div>
```

### Loading State (Skeleton)

```html
<div class="space-y-4 animate-pulse">
  <!-- Skeleton Card 1 -->
  <div class="bg-white border border-[#D4CFC4] rounded-lg p-5">
    <div class="h-6 bg-[#EDE8DD] rounded w-3/4 mb-3"></div>
    <div class="h-4 bg-[#EDE8DD] rounded w-full mb-2"></div>
    <div class="h-4 bg-[#EDE8DD] rounded w-5/6"></div>
  </div>

  <!-- Skeleton Card 2 -->
  <div class="bg-white border border-[#D4CFC4] rounded-lg p-5">
    <div class="h-6 bg-[#EDE8DD] rounded w-2/3 mb-3"></div>
    <div class="h-4 bg-[#EDE8DD] rounded w-full mb-2"></div>
    <div class="h-4 bg-[#EDE8DD] rounded w-4/5"></div>
  </div>
</div>
```

---

## Interactive States

### Button States

**Normal → Hover → Active → Focus**

```css
/* Primary Button States */
.btn-primary {
  /* Normal */
  background: #4A7C99;
  color: white;

  /* Hover */
  &:hover {
    background: #3A6C89;
  }

  /* Active (pressed) */
  &:active {
    background: #2A5C79;
    transform: translateY(1px);
  }

  /* Focus */
  &:focus {
    outline: none;
    ring: 2px solid #4A7C99;
    ring-offset: 2px;
  }

  /* Disabled */
  &:disabled {
    background: #D4CFC4;
    cursor: not-allowed;
    opacity: 0.5;
  }
}
```

### Input States

**Default → Focus → Error → Success**

```html
<!-- Default -->
<input class="border border-[#D4CFC4] focus:border-[#4A7C99]" />

<!-- Error -->
<input class="border border-[#C45D3F] focus:ring-[#C45D3F]" />

<!-- Success -->
<input class="border border-[#6B7F5B] focus:ring-[#6B7F5B]" />
```

### Card Hover Effect

```css
.task-card {
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 6px rgba(44, 62, 80, 0.1);
    transform: translateY(-2px);
  }
}
```

---

## Responsive Design

### Breakpoints

| Breakpoint | Min Width | Max Width | Tailwind Prefix |
|------------|-----------|-----------|-----------------|
| **Mobile** | 0px | 639px | (default) |
| **Tablet** | 640px | 1023px | `md:` |
| **Desktop** | 1024px+ | - | `lg:` |

### Mobile Layout

**Sidebar on Mobile:**
- Hidden by default
- Toggle with hamburger menu
- Slide-in overlay when opened

```typescript
// Mobile: Collapsible sidebar
<aside className="
  fixed left-0 top-0 bottom-0 z-50
  w-60
  bg-[#EDE8DD]
  transform transition-transform duration-300
  -translate-x-full md:translate-x-0
">
  {/* Sidebar content */}
</aside>

// Hamburger button (mobile only)
<button className="
  md:hidden
  fixed top-4 left-4 z-40
  p-2 bg-[#4A7C99] text-white rounded-md
">
  ☰
</button>
```

**Main Content on Mobile:**

```typescript
<main className="
  px-4 py-6          /* Mobile: 16px horizontal padding */
  md:px-12 md:py-8   /* Desktop: 48px horizontal padding */
  ml-0 md:ml-60      /* Desktop: offset for sidebar */
">
  {children}
</main>
```

### Responsive Typography

```html
<h1 class="
  text-3xl md:text-4xl lg:text-5xl
  font-heading font-bold
">
  Want todos
</h1>

<p class="
  text-base md:text-lg
  font-body leading-relaxed
">
  Body text scales with viewport.
</p>
```

### Responsive Task Cards

```html
<div class="
  p-4 md:p-5
  space-y-3 md:space-y-4
">
  <h3 class="text-lg md:text-xl">Task Title</h3>
  <p class="text-sm md:text-base">Description</p>
</div>
```

---

## Visual Examples

### Dashboard ASCII Wireframe

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ┌──────────┐  ┌──────────────────────────────────────────────┐  │
│  │          │  │  user@example.com  │  Logout                  │  │
│  │          │  └──────────────────────────────────────────────┘  │
│  │          │                                                     │
│  │          │  Want todos                          [Create Task] │
│  │          │  ─────────────────────────────────────────────────  │
│  │          │                                                     │
│  │ Journal  │  [ All ] [ Active ] [ Completed ]                  │
│  │          │                                                     │
│  │ ───────  │  ┌───────────────────────────────────────────────┐ │
│  │          │  │ ☐ Write project proposal                      │ │
│  │ Tasks ◀──│  │   Draft the initial proposal for the new...   │ │
│  │          │  │   Created: Dec 25, 2025 at 9:30 AM            │ │
│  │          │  │                            Edit  │  Delete     │ │
│  │          │  └───────────────────────────────────────────────┘ │
│  │          │                                                     │
│  │          │  ┌───────────────────────────────────────────────┐ │
│  │          │  │ ☑ Review team meeting notes                   │ │
│  │          │  │   Go through yesterday's meeting notes...     │ │
│  │          │  │   Completed: Dec 25, 2025 at 11:15 AM         │ │
│  │          │  │                                     Delete     │ │
│  │          │  └───────────────────────────────────────────────┘ │
│  │          │                                                     │
│  └──────────┘  └──────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Create Task Modal Wireframe

```
               ┌─────────────────────────────────────┐
               │                                     │
               │  Create New Task               ✕   │
               │  ─────────────────────────────────  │
               │                                     │
               │  Task Title                         │
               │  ┌───────────────────────────────┐  │
               │  │ Enter your task...            │  │
               │  └───────────────────────────────┘  │
               │                                     │
               │  Description (optional)             │
               │  ┌───────────────────────────────┐  │
               │  │ Add details...                │  │
               │  │                               │  │
               │  │                               │  │
               │  └───────────────────────────────┘  │
               │                                     │
               │  [Create Task]  [Cancel]            │
               │                                     │
               └─────────────────────────────────────┘
```

### Color Palette Swatch

```
Paper Cream      Ink Black        Sepia Brown      Warm Gray
#F5F1E8          #2C3E50          #8B7355          #D4CFC4
█████████        █████████        █████████        █████████

Vintage Blue     Rust Orange      Olive Green      Lavender
#4A7C99          #C45D3F          #6B7F5B          #9B8FA8
█████████        █████████        █████████        █████████
```

---

## Implementation Guide

### Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors
        'paper-cream': '#F5F1E8',
        'ink-black': '#2C3E50',
        'sepia-brown': '#8B7355',
        'warm-gray': '#D4CFC4',

        // Accent colors
        'vintage-blue': '#4A7C99',
        'rust-orange': '#C45D3F',
        'olive-green': '#6B7F5B',
        'lavender': '#9B8FA8',

        // Semantic
        'sidebar-bg': '#EDE8DD',
      },
      fontFamily: {
        body: ['Crimson Text', 'Georgia', 'Times New Roman', 'serif'],
        heading: ['Playfair Display', 'Georgia', 'serif'],
        mono: ['Courier Prime', 'Courier New', 'monospace'],
      },
      spacing: {
        '60': '15rem', // 240px for sidebar width
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // For better form styling
  ],
}

export default config
```

### Google Fonts Import

```typescript
// app/layout.tsx
import { Crimson_Text, Playfair_Display, Courier_Prime } from 'next/font/google'

const crimsonText = Crimson_Text({
  weight: ['400', '600', '700'],
  subsets: ['latin'],
  variable: '--font-body',
})

const playfairDisplay = Playfair_Display({
  weight: ['600', '700'],
  subsets: ['latin'],
  variable: '--font-heading',
})

const courierPrime = Courier_Prime({
  weight: ['400'],
  subsets: ['latin'],
  variable: '--font-mono',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${crimsonText.variable} ${playfairDisplay.variable} ${courierPrime.variable}`}
    >
      <body className="min-h-screen bg-paper-cream font-body antialiased">
        {children}
      </body>
    </html>
  )
}
```

### Component Implementation Example

```typescript
// components/ui/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/utils' // Utility for className merging

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'font-body font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'

    const variants = {
      primary: 'bg-vintage-blue text-white hover:bg-[#3A6C89] focus:ring-vintage-blue',
      secondary: 'bg-transparent text-sepia-brown border border-warm-gray hover:bg-sidebar-bg focus:ring-sepia-brown',
      destructive: 'bg-transparent text-rust-orange hover:bg-rust-orange hover:text-white focus:ring-rust-orange',
    }

    const sizes = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-2.5 text-base',
      lg: 'px-8 py-3 text-lg',
    }

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'
```

### Paper Texture Effect (Optional Enhancement)

```css
/* globals.css */
@layer base {
  body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" /></filter><rect width="100" height="100" filter="url(%23noise)" opacity="0.03"/></svg>');
    z-index: 1;
  }
}
```

### Utility Function for Class Names

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Implementation Checklist

- [ ] Install required fonts (Crimson Text, Playfair Display, Courier Prime)
- [ ] Configure Tailwind with custom colors and fonts
- [ ] Set up layout components (Sidebar, Header, RootLayout)
- [ ] Create reusable UI components (Button, Input, Card, Modal)
- [ ] Implement responsive sidebar (collapsible on mobile)
- [ ] Add paper texture effect (optional)
- [ ] Test on mobile, tablet, and desktop viewports
- [ ] Verify accessibility (keyboard navigation, ARIA labels, focus states)
- [ ] Ensure consistent spacing using Tailwind's spacing scale
- [ ] Validate color contrast ratios for accessibility (WCAG AA)

---

## Summary

This UI Design System establishes:

✅ **Design Philosophy** - Journal/diary aesthetic with warm, paper-like tones
✅ **Color Palette** - Paper Cream, Ink Black, Sepia Brown, Vintage Blue, and accent colors
✅ **Typography** - Crimson Text (body), Playfair Display (headings), serif fonts
✅ **Layout Structure** - Sidebar (left), Header (top right), Main content area
✅ **Component Library** - Buttons, inputs, cards, modals with journal styling
✅ **Application Layout** - "Want todos" heading, Create Task button, filters, task list
✅ **Task Card Design** - Paper-like cards with checkbox, title, description, metadata
✅ **Responsive Design** - Mobile-first approach with collapsible sidebar
✅ **Implementation Guide** - Tailwind configuration, font imports, component examples

**All frontend features MUST follow this design system for visual consistency.**

---

**Document Status:** Active
**Referenced By:** Feature 02 (Task CRUD UI), Feature 03 (Better Auth UI)
**Enforced By:** UI Developer Agent, Quality Guardian Agent
**Next Review:** After initial UI implementation
