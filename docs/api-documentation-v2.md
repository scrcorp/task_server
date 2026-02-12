# Task Server V2 API Documentation

> **Base URL**: `https://{your-render-app}/api/v1`

---

## 1. Authentication (Staff/Admin Public)

### 1.1 Login
`POST /auth/login`
- Body: `{ login_id, password }`
- Response: `{ access_token, user: { id, role, ... } }`

### 1.2 Signup (Staff Only)
`POST /auth/signup`
- Body: `{ email, login_id, password, full_name, branch_id, language }`
- Role: Defaults to `staff`, Status: `pending`.

---

## 2. Staff APIs

### 2.1 My Tasks
`GET /tasks?assigned_to={user_id}`
- Returns tasks assigned to the user.

### 2.2 Update Checklist Item
`PATCH /tasks/checklist/{item_id}`
- Body: `{ is_completed: bool, verification_data: Optional[str] }`
- **Side Effect**: Automatically creates a log entry in `checklist_logs`.

---

## 3. Admin APIs (Require role: manager/admin)

### 3.1 Staff Approval
`PATCH /admin/staff/{user_id}/approve`
- Body: `{ group_id: str }`
- Action: Approves a pending staff and assigns them to a group.

### 3.2 Organization Management
- `GET /admin/brands`: List all brands.
- `POST /admin/brands`: Create a brand.
- `GET /admin/branches?brand_id={uuid}`: List branches.
- `GET /admin/groups?branch_id={uuid}`: List groups.

### 3.3 Checklist Template Management
- `POST /admin/checklist-templates`: Create a template with items.
- `GET /admin/checklist-templates`: List all templates.

### 3.4 Monitoring Dashboard
- `GET /admin/dashboard/checklist-compliance`: View compliance rates.
- `GET /admin/dashboard/checklist-logs`: View detailed logs by user/date.

---

## 4. Architecture Note (Extensibility)

The APIs are implemented using the **Repository Pattern**.
- Path: `app/repositories/` contains the data access logic.
- Path: `app/services/` contains the business logic.
- Path: `app/api/endpoints/` contains the route handlers.

For details on migration, refer to `docs/migration-guide.md`.
