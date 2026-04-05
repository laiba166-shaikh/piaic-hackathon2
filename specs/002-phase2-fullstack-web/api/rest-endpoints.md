# REST API Endpoints Specification - Phase 2

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-12-25
**Type:** API Reference Document

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Headers](#authentication--headers)
3. [Common Response Formats](#common-response-formats)
4. [Task CRUD Endpoints](#task-crud-endpoints)
5. [Task Completion Endpoint](#task-completion-endpoint)
6. [Data Models](#data-models)
7. [Error Response Format](#error-response-format)
8. [HTTP Status Codes](#http-status-codes)
9. [Common Headers](#common-headers)
10. [Endpoint Summary Table](#endpoint-summary-table)

---

## Overview

This document defines all REST API endpoints for the Phase 2 Todo Web Application. All endpoints follow RESTful conventions and require JWT authentication.

### Base URLs

| Environment | Base URL |
|------------|----------|
| **Development** | http://localhost:8000 |
| **Production** | https://api.yourdomain.com |

### API Version

- All endpoints are prefixed with `/api/v1/`
- Current version: **v1**

### Authentication

- **Required for all endpoints:** JWT Bearer token
- **Token source:** Better Auth (frontend)
- **Token location:** `Authorization: Bearer {JWT_TOKEN}` header
- **User identification:** `user_id` extracted from JWT `sub` claim

### Key Principles

1. **User Isolation:** All endpoints filter data by authenticated user's ID
2. **No user_id in URLs:** User identity is extracted from JWT, not URL paths
3. **Soft Deletes:** DELETE operations set `deleted_at` timestamp, not hard delete
4. **Consistent Responses:** All responses return JSON with snake_case field names
5. **ISO 8601 Timestamps:** All timestamps in format `YYYY-MM-DDTHH:MM:SSZ`

---

## Authentication & Headers

### Required Headers (All Requests)

```http
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

### JWT Token Structure

**Better Auth issues JWT with this payload:**

```json
{
  "sub": "user-uuid-here",      // user_id (subject)
  "email": "user@example.com",  // optional
  "iat": 1703174400,            // issued at (timestamp)
  "exp": 1703260800             // expires at (timestamp)
}
```

**Backend extracts `user_id` from `sub` claim:**
- All operations automatically filter by this user_id
- User cannot access or modify other users' data
- Missing or invalid token returns 401 Unauthorized

### Error Response for Missing/Invalid Auth

**HTTP Status:** 401 Unauthorized

```json
{
  "detail": "Invalid or expired token"
}
```

**User-Facing Message:** "Your session has expired. Please log in again."

---

## Common Response Formats

### Success Response Structure

All successful responses return JSON with the following structure:

**Single Resource (201 Created, 200 OK):**

```json
{
  "id": 1,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "priority": null,
  "tags": [],
  "due_date": null,
  "recurrence": null,
  "deleted_at": null,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:00:00Z"
}
```

**Multiple Resources (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": "user-uuid",
    "title": "Buy groceries",
    "completed": false,
    ...
  },
  {
    "id": 2,
    "user_id": "user-uuid",
    "title": "Call dentist",
    "completed": true,
    ...
  }
]
```

**Empty List (200 OK):**

```json
[]
```

**Delete Success (204 No Content):**
- No response body
- Empty response

### Field Naming Conventions

- Use **snake_case** for all field names (Python/JSON convention)
- Examples: `user_id`, `created_at`, `due_date`
- NOT camelCase (`userId`, `createdAt`)

### Timestamp Format

- **Format:** ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)
- **Example:** `2025-12-25T10:30:00Z`
- **Timezone:** UTC (Z suffix)

---

## Task CRUD Endpoints

### 4.1 Create Task

**Endpoint:** `POST /api/v1/tasks`

**Description:** Create a new task for the authenticated user

**Request Headers:**
```http
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, nullable)"
}
```

**Request Body Rules:**
- `title`: Required, 1-200 characters, cannot be whitespace-only
- `description`: Optional, can be null or empty string, max 10,000 characters
- `user_id`: NOT accepted in request body (automatically extracted from JWT)

**Success Response (201 Created):**
```json
{
  "id": 1,
  "user_id": "user-uuid-from-jwt",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "priority": null,
  "tags": [],
  "due_date": null,
  "recurrence": null,
  "deleted_at": null,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:00:00Z"
}
```

**Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---------------|
| **400** | Missing title | `{"detail": "Title is required"}` |
| **400** | Title too long (>200 chars) | `{"detail": "Title must not exceed 200 characters"}` |
| **400** | Whitespace-only title | `{"detail": "Title is required"}` |
| **401** | Missing/invalid token | `{"detail": "Invalid or expired token"}` |
| **422** | Invalid data types | Pydantic validation error (see Error Response Format) |
| **500** | Database error | `{"detail": "An error occurred while processing your request"}` |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

---

### 4.2 List All Tasks

**Endpoint:** `GET /api/v1/tasks`

**Description:** Get all non-deleted tasks for the authenticated user

**Request Headers:**
```http
Authorization: Bearer {JWT_TOKEN}
```

**Query Parameters:**
- None in Phase 2 (filtering/sorting handled by separate features)

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": "user-uuid",
    "title": "Buy groceries",
    "description": "Milk and eggs",
    "completed": false,
    "priority": null,
    "tags": [],
    "due_date": null,
    "recurrence": null,
    "deleted_at": null,
    "created_at": "2025-12-25T10:00:00Z",
    "updated_at": "2025-12-25T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": "user-uuid",
    "title": "Call dentist",
    "description": null,
    "completed": true,
    "priority": null,
    "tags": [],
    "due_date": null,
    "recurrence": null,
    "deleted_at": null,
    "created_at": "2025-12-24T15:30:00Z",
    "updated_at": "2025-12-25T09:00:00Z"
  }
]
```

**Empty List Response (200 OK):**
```json
[]
```

**Behavior:**
- Returns only tasks where `user_id = authenticated_user_id` (from JWT)
- Excludes soft-deleted tasks (`deleted_at IS NULL`)
- Returns empty array if user has no tasks
- Order: Not guaranteed (implement sorting in separate feature)

**Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---------------|
| **401** | Missing/invalid token | `{"detail": "Invalid or expired token"}` |
| **500** | Database error | `{"detail": "An error occurred while processing your request"}` |

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 4.3 Get Single Task

**Endpoint:** `GET /api/v1/tasks/{id}`

**Description:** Get a specific task by ID (only if owned by authenticated user)

**Request Headers:**
```http
Authorization: Bearer {JWT_TOKEN}
```

**Path Parameters:**
- `id`: integer (required) - Task ID to retrieve

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "priority": null,
  "tags": [],
  "due_date": null,
  "recurrence": null,
  "deleted_at": null,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:00:00Z"
}
```

**Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---------------|
| **401** | Missing/invalid token | `{"detail": "Invalid or expired token"}` |
| **404** | Task doesn't exist | `{"detail": "Task not found"}` |
| **404** | Task belongs to another user | `{"detail": "Task not found"}` (same as above) |
| **404** | Task is soft-deleted | `{"detail": "Task not found"}` |
| **422** | Invalid task ID format (non-numeric) | Pydantic validation error |
| **500** | Database error | `{"detail": "An error occurred while processing your request"}` |

**Important Security Note:**
- Returns **404** (not 403) when task belongs to another user
- This prevents information leakage about task existence

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 4.4 Update Task

**Endpoint:** `PUT /api/v1/tasks/{id}`

**Description:** Update task title and/or description (only if owned by authenticated user)

**Request Headers:**
```http
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Path Parameters:**
- `id`: integer (required) - Task ID to update

**Request Body:**
```json
{
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, nullable)"
}
```

**Request Body Rules:**
- All fields are optional, but at least one should be provided
- Only `title` and `description` can be updated in basic CRUD
- Other fields (`completed`, `priority`, `tags`, etc.) updated by separate features
- `title`: If provided, must be 1-200 characters, cannot be whitespace-only
- `description`: If provided, can be null or any text length

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user-uuid",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, oranges",
  "completed": false,
  "priority": null,
  "tags": [],
  "due_date": null,
  "recurrence": null,
  "deleted_at": null,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T11:30:00Z"
}
```

**Behavior:**
- Only updates fields provided in request body
- Other fields remain unchanged
- `created_at` remains unchanged
- `updated_at` is refreshed to current timestamp

**Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---------------|
| **400** | Title empty or whitespace-only | `{"detail": "Title is required"}` |
| **400** | Title too long (>200 chars) | `{"detail": "Title must not exceed 200 characters"}` |
| **401** | Missing/invalid token | `{"detail": "Invalid or expired token"}` |
| **404** | Task doesn't exist | `{"detail": "Task not found"}` |
| **404** | Task belongs to another user | `{"detail": "Task not found"}` |
| **404** | Task is soft-deleted | `{"detail": "Task not found"}` |
| **422** | Invalid data types | Pydantic validation error |
| **500** | Database error | `{"detail": "An error occurred while processing your request"}` |

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and fruits",
    "description": "Milk, eggs, bread, apples, oranges"
  }'
```

---

### 4.5 Delete Task (Soft Delete)

**Endpoint:** `DELETE /api/v1/tasks/{id}`

**Description:** Soft delete a task (sets `deleted_at` timestamp, doesn't remove from database)

**Request Headers:**
```http
Authorization: Bearer {JWT_TOKEN}
```

**Path Parameters:**
- `id`: integer (required) - Task ID to delete

**Success Response (204 No Content):**
- No response body
- Empty response
- HTTP status code 204

**Behavior:**
- Sets `deleted_at` field to current timestamp
- Does NOT remove row from database (soft delete)
- Task no longer appears in `GET /api/v1/tasks` list
- Task cannot be retrieved, updated, or deleted again (returns 404)

**Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---------------|
| **401** | Missing/invalid token | `{"detail": "Invalid or expired token"}` |
| **404** | Task doesn't exist | `{"detail": "Task not found"}` |
| **404** | Task belongs to another user | `{"detail": "Task not found"}` |
| **404** | Task already deleted | `{"detail": "Task not found"}` |
| **422** | Invalid task ID format (non-numeric) | Pydantic validation error |
| **500** | Database error | `{"detail": "An error occurred while processing your request"}` |

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Success Response:**
```
HTTP/1.1 204 No Content
Content-Type: application/json
X-Request-ID: abc-123-def-456
```

---

## Task Completion Endpoint

### 5.1 Toggle Task Completion

**Endpoint:** `PATCH /api/v1/tasks/{id}/toggle`

**Description:** Toggle task completion status (incomplete ↔ complete)

**Request Headers:**
```http
Authorization: Bearer {JWT_TOKEN}
```

**Path Parameters:**
- `id`: integer (required) - Task ID to toggle

**Request Body:**
- No body required (simple toggle operation)
- Endpoint automatically flips `completed` field: `true` ↔ `false`

**Alternative Endpoint:** `PATCH /api/v1/tasks/{id}/complete`

**Alternative Request Body (Optional):**
```json
{
  "completed": true  // or false
}
```

**Alternative Behavior:**
- If body provided with `completed` field, sets to specified value
- If body empty, toggles current state

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": true,
  "priority": null,
  "tags": [],
  "due_date": null,
  "recurrence": null,
  "deleted_at": null,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T11:00:00Z"
}
```

**Behavior:**
- Toggles `completed` field: `false` → `true` or `true` → `false`
- Updates `updated_at` timestamp to current time
- All other fields remain unchanged
- Returns complete updated task object

**Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---------------|
| **401** | Missing/invalid token | `{"detail": "Invalid or expired token"}` |
| **404** | Task doesn't exist | `{"detail": "Task not found"}` |
| **404** | Task belongs to another user | `{"detail": "Task not found"}` |
| **404** | Task is soft-deleted | `{"detail": "Task not found"}` |
| **422** | Invalid task ID format (non-numeric) | Pydantic validation error |
| **422** | Invalid `completed` value (if using alternative endpoint) | Pydantic validation error |
| **500** | Database error | `{"detail": "An error occurred while processing your request"}` |

**Example Request (Toggle):**
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1/toggle \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Request (Explicit Set):**
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1/complete \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

---

## Data Models

### Task Object Schema

**Complete Task Object:**

```json
{
  "id": "integer (auto-increment, primary key)",
  "user_id": "string (from JWT, indexed)",
  "title": "string (required, 1-200 chars)",
  "description": "text (optional, nullable)",
  "completed": "boolean (default: false)",
  "priority": "string (nullable, max 20 chars, managed by separate feature)",
  "tags": "array of strings (default: [], JSONB)",
  "due_date": "ISO 8601 timestamp (nullable, managed by separate feature)",
  "recurrence": "string (nullable, max 20 chars, managed by separate feature)",
  "deleted_at": "ISO 8601 timestamp (nullable, for soft deletes)",
  "created_at": "ISO 8601 timestamp (auto-set)",
  "updated_at": "ISO 8601 timestamp (auto-update)"
}
```

### Field Details

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| **id** | integer | Auto | Auto-increment | Unique task identifier |
| **user_id** | string | Yes | From JWT | Owner's user ID (from token `sub` claim) |
| **title** | string | Yes | - | Task title (1-200 chars) |
| **description** | text | No | null | Task description (nullable, unlimited length) |
| **completed** | boolean | Yes | false | Task completion status |
| **priority** | string | No | null | Priority level (Phase 2: not used, managed by Feature 04) |
| **tags** | JSONB array | Yes | [] | Array of tag strings (Phase 2: not used, managed by Feature 05) |
| **due_date** | timestamp | No | null | Task deadline (Phase 2: not used, managed by Feature 06) |
| **recurrence** | string | No | null | Recurrence pattern (Phase 2: not used, managed by Feature 06) |
| **deleted_at** | timestamp | No | null | Soft delete timestamp (null = not deleted) |
| **created_at** | timestamp | Yes | Auto | Creation timestamp (auto-set on insert) |
| **updated_at** | timestamp | Yes | Auto | Last modification timestamp (auto-update) |

### Database Constraints

- `id` PRIMARY KEY
- `user_id` NOT NULL, VARCHAR(255)
- `title` NOT NULL, VARCHAR(200)
- `description` TEXT, NULLABLE
- `completed` BOOLEAN NOT NULL DEFAULT FALSE
- `priority` VARCHAR(20), NULLABLE
- `tags` JSONB NOT NULL DEFAULT '[]'
- `due_date` TIMESTAMP WITH TIME ZONE, NULLABLE
- `recurrence` VARCHAR(20), NULLABLE
- `deleted_at` TIMESTAMP WITH TIME ZONE, NULLABLE
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()

### Database Indexes

```sql
-- Primary key
CREATE INDEX pk_tasks ON tasks(id);

-- User isolation queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Soft delete filtering
CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at) WHERE deleted_at IS NULL;

-- Combined user + soft delete queries (most common)
CREATE INDEX idx_tasks_user_deleted ON tasks(user_id, deleted_at);

-- Completion filtering (for Feature 03)
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Optional: Combined user + completed queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed) WHERE deleted_at IS NULL;
```

---

## Error Response Format

### Standard Error (400, 404, 500)

```json
{
  "detail": "Human-readable error message"
}
```

**Examples:**

```json
{"detail": "Title is required"}
{"detail": "Task not found"}
{"detail": "Invalid or expired token"}
{"detail": "An error occurred while processing your request"}
```

### Validation Error (422 Unprocessable Entity)

**FastAPI Pydantic validation error format:**

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Multiple validation errors:**

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 1}
    },
    {
      "loc": ["body", "completed"],
      "msg": "value is not a valid boolean",
      "type": "type_error.boolean"
    }
  ]
}
```

**Field Description:**
- `loc`: Location of error (`["body", "field_name"]` or `["path", "id"]`)
- `msg`: Human-readable error message
- `type`: Error type identifier
- `ctx`: Additional context (optional)

---

## HTTP Status Codes

### Success Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST (resource created) |
| **204** | No Content | Successful DELETE (no response body) |

### Client Error Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| **400** | Bad Request | Invalid request format, missing required field, validation failure |
| **401** | Unauthorized | Missing, invalid, or expired JWT token |
| **404** | Not Found | Resource doesn't exist OR belongs to different user (never 403) |
| **422** | Unprocessable Entity | Pydantic validation errors (wrong data types, format) |

### Server Error Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| **500** | Internal Server Error | Database errors, unexpected exceptions |
| **504** | Gateway Timeout | Request timeout (rarely used) |

### Important Notes

- **404 vs 403:** Always return **404** (not 403) when user tries to access another user's resource
  - Prevents information leakage about resource existence
  - Example: User A tries to access User B's task → 404 "Task not found"
- **400 vs 422:**
  - 400 for business logic errors ("Title is required")
  - 422 for data type/format errors (Pydantic validation)

---

## Common Headers

### Request Headers

**All Requests:**

```http
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Optional Headers:**

```http
Accept: application/json
X-Request-ID: {unique-request-id}  # For request tracing
```

### Response Headers

**All Responses:**

```http
Content-Type: application/json
X-Request-ID: {unique-request-id}  # Echo back if provided
```

**Example Complete Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: abc-123-def-456

{
  "id": 1,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  ...
}
```

---

## Endpoint Summary Table

| Method | Endpoint | Description | Auth | Request Body | Success Status | Response Body |
|--------|----------|-------------|------|--------------|----------------|---------------|
| **POST** | `/api/v1/tasks` | Create new task | ✅ | `{title, description?}` | 201 Created | Task object |
| **GET** | `/api/v1/tasks` | List all user tasks | ✅ | - | 200 OK | Task array |
| **GET** | `/api/v1/tasks/{id}` | Get single task | ✅ | - | 200 OK | Task object |
| **PUT** | `/api/v1/tasks/{id}` | Update task | ✅ | `{title?, description?}` | 200 OK | Updated task object |
| **DELETE** | `/api/v1/tasks/{id}` | Soft delete task | ✅ | - | 204 No Content | Empty |
| **PATCH** | `/api/v1/tasks/{id}/toggle` | Toggle completion | ✅ | - | 200 OK | Updated task object |

### Quick Reference

**Authentication:**
- All endpoints require JWT token
- Token in `Authorization: Bearer {token}` header
- Missing/invalid token → 401 Unauthorized

**User Isolation:**
- All endpoints filter by `user_id` from JWT
- Users cannot access other users' data
- Cross-user access attempts → 404 Not Found

**Soft Deletes:**
- DELETE sets `deleted_at` timestamp
- Deleted tasks excluded from GET /api/v1/tasks
- Deleted tasks return 404 on GET, PUT, PATCH, DELETE

**Timestamps:**
- `created_at` set once on creation
- `updated_at` refreshed on every update
- Format: ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)

---

## Examples

### Example 1: Complete Task Creation Flow

**1. Create Task:**

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": null,
  "tags": [],
  "due_date": null,
  "recurrence": null,
  "deleted_at": null,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:00:00Z"
}
```

**2. List Tasks:**

```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": "user-123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    ...
  }
]
```

**3. Mark as Complete:**

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1/toggle \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T11:00:00Z",
  ...
}
```

**4. Update Task:**

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and fruits"
  }'
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread",
  "completed": true,
  "updated_at": "2025-12-25T12:00:00Z",
  ...
}
```

**5. Delete Task:**

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (204 No Content):**
```
HTTP/1.1 204 No Content
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-25 | Initial REST API specification for Phase 2 |

---

## References

- **Backend Architecture:** `specs/002-phase2-fullstack-web/00-backend-architecture.md`
- **Task CRUD Spec:** `specs/002-phase2-fullstack-web/features/02-task-crud.md`
- **Task Completion Spec:** `specs/002-phase2-fullstack-web/features/03-task-completion.md`
- **Authentication Spec:** `specs/002-phase2-fullstack-web/01-authentication.md`

---

**Document Status:** Active
**Maintained By:** API Developer Agent
**Referenced By:** Frontend developers, API consumers, testing team
**Next Review:** After Phase 2 implementation complete
