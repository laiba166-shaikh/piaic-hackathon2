---
name: api-contract-guardian
description: Validate API consistency between specification, frontend implementation, and backend implementation to ensure contract compliance. Use when (1) implementing API endpoints, (2) before merging API changes, (3) debugging frontend-backend mismatches, or (4) during integration testing.
license: Complete terms in LICENSE.txt
---

# API Contract Guardian

Validate that API implementations match specifications across all three layers: spec, frontend, and backend.

## Workflow

Follow these steps when validating API contracts:

1. **Compare API spec with actual implementation**
   - Read spec from `specs/phase2/api/[endpoint].md`
   - Check backend implementation in `src/core/backend/routers/`
   - Review frontend API client in `src/core/frontend/lib/api.ts`
   - Validate shared types in `shared/types/`

2. **Verify request/response shapes match**
   - Request body fields and types
   - Response body fields and types
   - Nested object structures
   - Array types and contents

3. **Check endpoint URLs and methods**
   - HTTP method (GET, POST, PUT, DELETE)
   - URL path and structure
   - Path parameters
   - Query parameters

4. **Validate error response formats**
   - Error status codes (400, 401, 404, etc.)
   - Error response schema
   - Error message format
   - Validation error details

5. **Alert on contract violations**
   - Missing fields in implementation
   - Type mismatches
   - Incorrect status codes
   - Drift between layers

## Output Format

Present API contract validation using this structure:

```
📋 API Contract Check: [endpoint-name]

Specification: specs/phase2/api/tasks-endpoints.md
Backend: src/core/backend/routers/tasks.py:45
Frontend: src/core/frontend/lib/api.ts:23
Types: shared/types/task.ts, shared/types/task.py

Endpoint: POST /api/v1/tasks

✅ Compliant:
- Endpoint URL matches spec
- HTTP method matches (POST)
- Request body schema matches
- Response status code correct (201)
- Response body schema matches

❌ Violations Found:

1. Missing field in response (Line 67 in src/core/backend/routers/tasks.py)
   Spec requires: created_at (ISO 8601 string)
   Backend returns: No created_at field
   Fix: Add created_at to TaskResponse schema

2. Incorrect status code (Line 45 in src/core/backend/routers/tasks.py)
   Spec requires: 201 Created
   Backend returns: 200 OK
   Fix: Change status_code=status.HTTP_201_CREATED

3. Type mismatch (Line 23 in src/core/frontend/lib/api.ts)
   Spec defines: tags as string[]
   Frontend expects: tags as string (incorrect)
   Fix: Update TaskResponse interface tags: string[]

4. Missing error handling (Line 89 in src/core/backend/routers/tasks.py)
   Spec requires: 400 Bad Request for invalid input
   Backend: No validation for missing title
   Fix: Add Pydantic validation with Field(...)
```

## Contract Verification Points

Check these elements for every endpoint:

### 1. Endpoint URL and HTTP Method

**Spec:**
```markdown
## POST /api/v1/tasks
```

**Backend (FastAPI):**
```python
@router.post("/api/v1/tasks", status_code=status.HTTP_201_CREATED)
```

**Frontend:**
```typescript
createTask: (data: TaskCreate) =>
  fetchWithAuth<Task>('/api/v1/tasks', { method: 'POST', ... })
```

**Verify:**
- [ ] URL path matches exactly
- [ ] HTTP method matches (GET, POST, PUT, DELETE)
- [ ] Path parameters in correct order
- [ ] Query parameters documented and used

### 2. Request Body Schema

**Spec:**
```markdown
Request Body:
- title: string (required, 1-200 chars)
- description: string (optional)
- priority: number (optional, 1-5)
- tags: string[] (optional)
```

**Backend (Pydantic):**
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)
```

**Frontend (TypeScript):**
```typescript
interface TaskCreate {
  title: string;
  description?: string;
  priority?: number;
  tags?: string[];
}
```

**Verify:**
- [ ] All required fields present
- [ ] Optional fields marked correctly (| None, ?)
- [ ] Field types match (string ↔ str, number ↔ int)
- [ ] Validation rules match (min/max length, range)
- [ ] Array types match (string[] ↔ list[str])

### 3. Response Body Schema

**Spec:**
```markdown
Response (201 Created):
- id: number
- title: string
- description: string | null
- priority: number | null
- tags: string[]
- created_at: string (ISO 8601)
- updated_at: string (ISO 8601)
```

**Backend (Pydantic):**
```python
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    priority: int | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Frontend (TypeScript):**
```typescript
interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: number | null;
  tags: string[];
  created_at: string;  // ISO 8601
  updated_at: string;  // ISO 8601
}
```

**Verify:**
- [ ] All fields present in response
- [ ] Field types match across layers
- [ ] Nullable fields handled (| None, | null)
- [ ] Timestamps formatted consistently (ISO 8601)
- [ ] Nested objects match structure

### 4. Status Codes (Success)

**Spec:**
```markdown
Response (201): Created successfully
Response (200): Retrieved successfully
Response (204): Deleted successfully (no content)
```

**Backend:**
```python
@router.post("/api/v1/tasks", status_code=status.HTTP_201_CREATED)
@router.get("/api/v1/tasks/{id}", status_code=status.HTTP_200_OK)
@router.delete("/api/v1/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
```

**Verify:**
- [ ] 201 for resource creation (POST)
- [ ] 200 for successful retrieval (GET)
- [ ] 200 for successful update (PUT)
- [ ] 204 for successful deletion (DELETE)

### 5. Error Responses

**Spec:**
```markdown
Errors:
- 400 Bad Request: Invalid input (missing required fields, validation errors)
- 401 Unauthorized: Missing or invalid authentication token
- 403 Forbidden: Authenticated but not authorized
- 404 Not Found: Resource doesn't exist
- 422 Unprocessable Entity: Validation errors (detailed)
```

**Backend:**
```python
# 400 - Automatic from Pydantic validation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)  # Raises 422 if invalid

# 401 - From auth dependency
@router.post("/api/v1/tasks")
async def create_task(user_id: str = Depends(get_current_user)):
    # Raises 401 if token invalid

# 404 - Manual check
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

**Frontend:**
```typescript
try {
  await api.createTask(data);
} catch (error) {
  if (error.message.includes('401')) {
    // Redirect to login
  } else if (error.message.includes('400')) {
    // Show validation errors
  }
}
```

**Verify:**
- [ ] 400/422 for validation errors
- [ ] 401 for authentication failures
- [ ] 404 for missing resources
- [ ] Error response has consistent format
- [ ] Error messages are user-friendly

### 6. Query Parameters

**Spec:**
```markdown
## GET /api/v1/tasks?status=active&limit=10

Query Parameters:
- status: string (optional, "active" | "completed")
- limit: number (optional, default: 50, max: 100)
- offset: number (optional, default: 0)
```

**Backend:**
```python
@router.get("/api/v1/tasks")
async def get_tasks(
    status: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user),
):
    # Implementation
```

**Frontend:**
```typescript
getTasks: (params?: { status?: string; limit?: number; offset?: number }) =>
  fetchWithAuth<Task[]>(`/api/v1/tasks?${new URLSearchParams(params)}`)
```

**Verify:**
- [ ] Query params match spec
- [ ] Default values match
- [ ] Validation rules match (min/max)
- [ ] Optional params handled correctly

### 7. Path Parameters

**Spec:**
```markdown
## GET /api/v1/tasks/{id}

Path Parameters:
- id: number (task ID)
```

**Backend:**
```python
@router.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: int, user_id: str = Depends(get_current_user)):
```

**Frontend:**
```typescript
getTask: (id: number) =>
  fetchWithAuth<Task>(`/api/v1/tasks/${id}`)
```

**Verify:**
- [ ] Path parameter names match (or are clearly mapped)
- [ ] Types match (number ↔ int)
- [ ] Required in all three layers

## Expected Spec Format

API specs should follow this format:

```markdown
# Tasks API Endpoints

## POST /api/v1/tasks

Create a new task for the authenticated user.

### Request Body

- title: string (required, 1-200 characters)
- description: string (optional)
- priority: number (optional, 1-5)
- tags: string[] (optional)

### Response (201 Created)

- id: number
- title: string
- description: string | null
- priority: number | null
- tags: string[]
- created_at: string (ISO 8601)
- updated_at: string (ISO 8601)

### Errors

- 400 Bad Request: Invalid input
  - Missing required field (title)
  - Title too long (> 200 chars)
  - Priority out of range (< 1 or > 5)

- 401 Unauthorized: Missing or invalid token

## GET /api/v1/tasks

Retrieve all tasks for the authenticated user.

### Query Parameters

- status: string (optional, "active" | "completed" | "all", default: "active")
- limit: number (optional, default: 50, max: 100)
- offset: number (optional, default: 0)

### Response (200 OK)

Array of Task objects (same schema as POST response)

### Errors

- 401 Unauthorized: Missing or invalid token
```

## Validation Checklist

For each endpoint, verify:

**✅ Specification:**
- [ ] Endpoint documented in specs/phase2/api/
- [ ] HTTP method specified
- [ ] Request schema documented
- [ ] Response schema documented
- [ ] Status codes documented
- [ ] Error cases documented

**✅ Backend Implementation:**
- [ ] Route matches spec URL
- [ ] HTTP method matches
- [ ] Request schema (Pydantic) matches spec
- [ ] Response schema (Pydantic) matches spec
- [ ] Status codes match spec
- [ ] Error handling matches spec
- [ ] User isolation enforced (user_id from JWT)

**✅ Frontend Implementation:**
- [ ] API client method exists
- [ ] URL matches spec
- [ ] HTTP method matches
- [ ] Request type (TypeScript) matches spec
- [ ] Response type (TypeScript) matches spec
- [ ] Error handling present

**✅ Shared Types:**
- [ ] TypeScript interfaces match spec
- [ ] Pydantic models match spec
- [ ] TypeScript and Pydantic types aligned
- [ ] Types exported and importable

## Key Rules

- **Spec is single source of truth** - All implementations must match spec
- **Three-way validation** - Check spec, backend, AND frontend
- **Flag drift immediately** - Alert on any mismatch
- **Suggest spec updates** - If intentional change, update spec first
- **Type consistency** - Ensure string↔str, number↔int, array↔list alignment
- **Status codes matter** - 201 vs 200, 400 vs 422 must be correct
- **Error formats** - Consistent error response structure
- **Version changes carefully** - Breaking changes require migration plan
- **User isolation** - Every endpoint filters by user_id from JWT
- **Soft deletes** - Deleted resources return 404, not included in lists
