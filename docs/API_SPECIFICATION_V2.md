# Task Server API Specification v2

> **Base URL**: `/api/v1`
> **Version**: 0.2.0
> **Auth**: Custom JWT (HS256) — `Authorization: Bearer <access_token>`
> **Language**: All API messages in English

---

## Table of Contents

1. [Auth](#1-auth)
2. [Assignments](#2-assignments)
3. [Daily Checklists](#3-daily-checklists)
4. [Notices](#4-notices)
5. [Admin](#5-admin)
6. [Users](#6-users)
7. [Dashboard](#7-dashboard)
8. [Attendance](#8-attendance)
9. [Opinions](#9-opinions)
10. [Notifications](#10-notifications)
11. [Files](#11-files)
12. [Setup](#12-setup)
13. [Health Check](#13-health-check)
14. [Schema Definitions](#14-schema-definitions)
15. [Enum Definitions](#15-enum-definitions)
16. [Error Responses](#16-error-responses)

---

## 1. Auth

### POST `/auth/login` — Login

| Item | Value |
|------|-------|
| Auth | Not required |

**Request Body**
```json
{
  "login_id": "user123",
  "password": "password123"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "login_id": "user123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "staff",
    "company_id": "uuid",
    "email_verified": false
  }
}
```

**Error** `401`
```json
{ "detail": "Invalid login ID or password." }
```

---

### POST `/auth/signup` — Sign Up

| Item | Value |
|------|-------|
| Auth | Not required |

**Request Body**
```json
{
  "email": "user@example.com",
  "login_id": "user123",
  "password": "password123",
  "full_name": "John Doe",
  "company_code": "ABC",
  "language": "en"
}
```

**Response** `201 Created`
```json
{
  "message": "Signup successful. A 6-digit verification code has been sent to your email.",
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "login_id": "user123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_id": "uuid"
  }
}
```

**Errors**
| Code | Detail |
|------|--------|
| 400 | `"Login ID is already taken."` |
| 400 | `"Email is already registered."` |
| 400 | `"Invalid company code: {code}"` |
| 400 | `"Signup failed."` |

---

### POST `/auth/logout` — Logout

| Item | Value |
|------|-------|
| Auth | Bearer Token |

**Response** `200 OK`
```json
{ "message": "Successfully logged out." }
```

---

### POST `/auth/refresh` — Refresh Token

| Item | Value |
|------|-------|
| Auth | Not required |

**Request Body**
```json
{ "refresh_token": "eyJ..." }
```

**Response** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

**Error** `401`
```json
{ "detail": "Token refresh failed." }
```

---

### GET `/auth/me` — Get Current User

| Item | Value |
|------|-------|
| Auth | Bearer Token |

**Response** `200 OK` — [User](#user) object

---

### POST `/auth/verify-email` — Verify Email with 6-digit Code

| Item | Value |
|------|-------|
| Auth | Not required |

**Request Body**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response** `200 OK`
```json
{ "message": "Email verified successfully." }
```

**Errors**
| Code | Detail |
|------|--------|
| 400 | `"Invalid or expired verification code."` |
| 429 | `"Too many requests. Please try again later."` |

---

### POST `/auth/resend-verification` — Resend Verification Code

| Item | Value |
|------|-------|
| Auth | Not required |

**Request Body**
```json
{
  "email": "user@example.com"
}
```

**Response** `200 OK`
```json
{ "message": "Verification code sent." }
```

**Errors**
| Code | Detail |
|------|--------|
| 400 | `"Email is already verified."` |
| 404 | `"No account found with this email."` |
| 429 | `"Too many requests. Please try again later."` |

---

## 2. Assignments

> All endpoints require authentication. Scoped by `company_id` from current user.

### GET `/assignments/` — List Assignments

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `status` | string | No | Filter by status (`todo`/`in_progress`/`done`) |
| `branch_id` | string | No | Filter by branch |

**Response** `200 OK` — Assignment[] array

---

### GET `/assignments/my` — My Assignments

Returns assignments where current user is an assignee.

**Response** `200 OK` — Assignment[] array

---

### GET `/assignments/{assignment_id}` — Get Assignment

**Response** `200 OK` — [Assignment](#assignment) object (with assignees & comments)

**Error** `404`
```json
{ "detail": "Assignment not found." }
```

---

### POST `/assignments/` — Create Assignment

**Request Body**
```json
{
  "title": "Store cleaning",
  "description": "Clean the entire first floor (optional)",
  "priority": "normal",
  "status": "todo",
  "due_date": "2026-02-14T09:00:00",
  "branch_id": "uuid (optional)",
  "recurrence": null,
  "assignee_ids": ["uuid1", "uuid2"]
}
```

**Response** `201 Created` — [Assignment](#assignment) object

---

### PATCH `/assignments/{assignment_id}` — Update Assignment

**Request Body** (all fields optional)
```json
{
  "title": "string",
  "description": "string",
  "status": "todo | in_progress | done",
  "priority": "urgent | normal | low",
  "due_date": "datetime",
  "branch_id": "uuid",
  "recurrence": {}
}
```

**Response** `200 OK` — Assignment object

---

### DELETE `/assignments/{assignment_id}` — Delete Assignment

**Response** `200 OK`
```json
{ "message": "Assignment deleted." }
```

---

### PATCH `/assignments/{assignment_id}/status` — Update Status

**Request Body**
```json
{ "status": "in_progress" }
```

**Response** `200 OK` — Updated Assignment object

---

### POST `/assignments/{assignment_id}/assignees` — Add Assignees

**Request Body**
```json
{ "user_ids": ["uuid1", "uuid2"] }
```

**Response** `201 Created`
```json
{ "message": "Assignees added.", "data": [...] }
```

---

### DELETE `/assignments/{assignment_id}/assignees/{user_id}` — Remove Assignee

**Response** `200 OK`
```json
{ "message": "Assignee removed." }
```

---

### GET `/assignments/{assignment_id}/comments` — List Comments

**Response** `200 OK` — [Comment](#comment)[] array

---

### POST `/assignments/{assignment_id}/comments` — Create Comment

**Request Body**
```json
{
  "content": "Looks good.",
  "content_type": "text",
  "attachments": [
    {"type": "image", "url": "/storage/img.jpg", "name": "photo.jpg", "size": 204800}
  ]
}
```

**Response** `201 Created` — [Comment](#comment) object

---

### DELETE `/assignments/{assignment_id}/comments/{comment_id}` — Delete Comment

**Response** `200 OK`
```json
{ "message": "Comment deleted." }
```

---

## 3. Daily Checklists

> All endpoints require authentication.

### GET `/daily-checklists/` — List Daily Checklists

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `branch_id` | string | Yes | Branch ID |
| `date` | string | Yes | Date (YYYY-MM-DD) |

**Response** `200 OK` — DailyChecklist[] array

---

### GET `/daily-checklists/{checklist_id}` — Get Checklist

**Response** `200 OK` — DailyChecklist object

**Error** `404`
```json
{ "detail": "Checklist not found." }
```

---

### POST `/daily-checklists/generate` — Generate from Template

**Request Body**
```json
{
  "template_id": "uuid",
  "branch_id": "uuid",
  "date": "2026-02-13",
  "group_ids": ["uuid1", "uuid2"]
}
```

**Response** `201 Created` — DailyChecklist object

**Error** `400`
```json
{ "detail": "Template not found." }
```

---

### PATCH `/daily-checklists/{checklist_id}/items/{item_index}` — Update Item

**Request Body**
```json
{
  "is_completed": true,
  "verification_data": "https://storage.example.com/photo.jpg"
}
```

**Response** `200 OK` — Updated DailyChecklist object

**Errors**
| Code | Detail |
|------|--------|
| 400 | `"Checklist not found."` |
| 400 | `"Invalid item index: {index}"` |

---

## 4. Notices

### GET `/notices/` — List Notices

| Item | Value |
|------|-------|
| Auth | Bearer Token |

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `limit` | int | No | Max number of results |

**Response** `200 OK` — [Notice](#notice)[] array (scoped by company_id)

---

### GET `/notices/{notice_id}` — Get Notice

| Item | Value |
|------|-------|
| Auth | Bearer Token |

**Response** `200 OK` — [Notice](#notice) object

**Error** `404`
```json
{ "detail": "Notice not found." }
```

---

### POST `/notices/{notice_id}/confirm` — Confirm Notice

| Item | Value |
|------|-------|
| Auth | Bearer Token |

**Response** `200 OK` — Confirmation record

---

### POST `/notices/` — Create Notice

| Item | Value |
|------|-------|
| Auth | Bearer Token |
| Role | ADMIN, MANAGER |

**Request Body**
```json
{
  "title": "February operations update",
  "content": "Notice content here.",
  "is_important": false,
  "branch_id": "uuid (optional, null = company-wide)"
}
```

Auto-injected from current user: `author_id`, `author_name`, `author_role`, `company_id`

**Response** `201 Created` — Notice record

---

### PATCH `/notices/{notice_id}` — Update Notice

| Item | Value |
|------|-------|
| Auth | Bearer Token |
| Role | ADMIN, MANAGER |

**Request Body** (same fields as create, all optional)

**Response** `200 OK` — Updated Notice object

---

### DELETE `/notices/{notice_id}` — Delete Notice

| Item | Value |
|------|-------|
| Auth | Bearer Token |
| Role | ADMIN, MANAGER |

**Response** `200 OK`
```json
{ "message": "Notice deleted." }
```

---

## 5. Admin

> All endpoints require **ADMIN** or **MANAGER** role.

### Staff Management

#### GET `/admin/staff/pending` — Pending Staff List

**Response** `200 OK` — [User](#user)[] array (scoped by company_id)

#### PATCH `/admin/staff/{user_id}/approve` — Approve Staff

**Response** `200 OK` — [User](#user) object (status → active)

#### PATCH `/admin/staff/{user_id}/reject` — Reject Staff

**Response** `200 OK` — [User](#user) object (status → inactive)

---

### Company

#### GET `/admin/company` — Get Company Info

**Response** `200 OK` — Company object

#### PATCH `/admin/company` — Update Company

**Request Body**
```json
{ "name": "Updated Company Name" }
```

**Response** `200 OK` — Updated Company object

---

### Brands

#### GET `/admin/brands` — List Brands (scoped by company_id)

**Response** `200 OK` — Brand[] array

#### POST `/admin/brands` — Create Brand

**Request Body**
```json
{ "name": "Brand Name" }
```

**Response** `201 Created` — Brand object (company_id auto-injected)

#### PATCH `/admin/brands/{brand_id}` — Update Brand

**Request Body**
```json
{ "name": "Updated Name" }
```

**Response** `200 OK` — Brand object

#### DELETE `/admin/brands/{brand_id}` — Delete Brand

**Response** `200 OK`
```json
{ "message": "Brand deleted." }
```

---

### Branches

#### GET `/admin/branches` — List Branches

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `brand_id` | string | No | Filter by brand |

**Response** `200 OK` — Branch[] array

#### POST `/admin/branches` — Create Branch

**Request Body**
```json
{
  "brand_id": "uuid",
  "name": "Gangnam Branch",
  "address": "123 Gangnam Blvd (optional)"
}
```

**Response** `201 Created` — Branch object

#### DELETE `/admin/branches/{branch_id}` — Delete Branch

**Response** `200 OK`
```json
{ "message": "Branch deleted." }
```

---

### Group Types

#### GET `/admin/branches/{branch_id}/group-types` — List Group Types

**Response** `200 OK` — GroupType[] array

#### POST `/admin/group-types` — Create Group Type

**Request Body**
```json
{
  "branch_id": "uuid",
  "priority": 1,
  "label": "time"
}
```

**Response** `201 Created` — GroupType object

#### DELETE `/admin/group-types/{group_type_id}` — Delete Group Type

**Response** `200 OK`
```json
{ "message": "Group type deleted." }
```

---

### Groups

#### GET `/admin/group-types/{group_type_id}/groups` — List Groups

**Response** `200 OK` — Group[] array

#### POST `/admin/groups` — Create Group

**Request Body**
```json
{
  "group_type_id": "uuid",
  "name": "Opening Shift"
}
```

**Response** `201 Created` — Group object

#### DELETE `/admin/groups/{group_id}` — Delete Group

**Response** `200 OK`
```json
{ "message": "Group deleted." }
```

---

### Checklist Templates

#### GET `/admin/checklist-templates` — List Templates

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `branch_id` | string | No | Filter by branch |

Scoped by company_id from current user.

**Response** `200 OK` — ChecklistTemplate[] array

#### POST `/admin/checklist-templates` — Create Template

**Request Body**
```json
{
  "name": "Opening Checklist",
  "branch_id": "uuid",
  "brand_id": "uuid (optional)",
  "recurrence": {"type": "daily"},
  "items": [
    {"content": "Turn on AC", "verification_type": "none", "sort_order": 1},
    {"content": "Take store photo", "verification_type": "photo", "sort_order": 2}
  ],
  "group_ids": ["uuid1", "uuid2"]
}
```

**Response** `201 Created` — ChecklistTemplate object

---

### Admin Dashboard

#### GET `/admin/dashboard/checklist-compliance` — Compliance Summary

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `branch_id` | string | Yes | Branch ID |
| `date` | string | Yes | Date (YYYY-MM-DD) |

**Response** `200 OK`
```json
{
  "branch_id": "uuid",
  "date": "2026-02-13",
  "compliance_rate": 85.5,
  "details": [...]
}
```

---

### Feedbacks

#### GET `/admin/feedbacks` — List Feedbacks

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `target_user_id` | string | No | Filter by target user |
| `assignment_id` | string | No | Filter by assignment |

Scoped by company_id from current user.

**Response** `200 OK` — Feedback[] array

#### POST `/admin/feedbacks` — Create Feedback

**Request Body**
```json
{
  "content": "Good work on this assignment.",
  "assignment_id": "uuid (optional)",
  "branch_id": "uuid (optional)",
  "target_user_id": "uuid (optional)"
}
```

Auto-injected: `company_id`, `author_id` from current user.

**Response** `201 Created` — Feedback object

---

## 6. Users

> All endpoints require authentication.

### GET `/users/me/profile` — Get My Profile

**Response** `200 OK` — [User](#user) object

---

### PATCH `/users/me/profile` — Update My Profile

**Request Body** (all fields optional)
```json
{
  "full_name": "John Doe",
  "profile_image": "https://...",
  "language": "en"
}
```

**Response** `200 OK` — [User](#user) object

**Error** `400`
```json
{ "detail": "No fields to update." }
```

---

### POST `/users/me/password` — Change Password

**Request Body**
```json
{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

**Response** `200 OK`
```json
{ "message": "Password changed successfully." }
```

**Error** `400`
```json
{ "detail": "Current password is incorrect." }
```

---

## 7. Dashboard

### GET `/dashboard/summary` — Dashboard Summary

| Item | Value |
|------|-------|
| Auth | Bearer Token |

**Response** `200 OK`
```json
{
  "assignment_summary": {
    "total": 10,
    "completed": 7,
    "in_progress": 2,
    "todo": 1,
    "completion_rate": 70.0
  },
  "attendance": {
    "status": "on_duty",
    "clock_in": "2026-02-13T09:00:00"
  },
  "recent_notices": [
    {
      "id": "uuid",
      "title": "Notice Title",
      "created_at": "2026-02-13T08:00:00"
    }
  ]
}
```

---

## 8. Attendance

> All endpoints require authentication. Scoped by company_id.

### GET `/attendance/today` — Today's Status

**Response** `200 OK` — [AttendanceRecord](#attendancerecord) or `null`

---

### POST `/attendance/clock-in` — Clock In

**Request Body**
```json
{
  "branch_id": "uuid (optional)",
  "location": "Gangnam Branch (optional)"
}
```

**Response** `201 Created` — [AttendanceRecord](#attendancerecord)

**Error** `400`
```json
{ "detail": "Clock-in record already exists for today." }
```

---

### POST `/attendance/clock-out` — Clock Out

**Response** `200 OK` — [AttendanceRecord](#attendancerecord) (includes work_hours)

**Errors**
| Code | Detail |
|------|--------|
| 400 | `"No clock-in record found for today."` |
| 400 | `"Already clocked out for today."` |

---

### GET `/attendance/history` — Monthly History

| Query Parameter | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `year` | int | No | Current year | Year |
| `month` | int | No | Current month | Month |

**Response** `200 OK`
```json
{
  "month": "2026-02",
  "records": [],
  "summary": {
    "total_days": 20,
    "completed": 18,
    "incomplete": 2
  }
}
```

---

## 9. Opinions

> All endpoints require authentication. Scoped by company_id.

### POST `/opinions/` — Create Opinion

**Request Body**
```json
{ "content": "Suggestion content here." }
```

**Response** `201 Created` — [Opinion](#opinion) object

---

### GET `/opinions/` — My Opinions

**Response** `200 OK` — [Opinion](#opinion)[] array

---

## 10. Notifications

> All endpoints require authentication. Scoped by company_id.

### GET `/notifications/` — List Notifications

**Response** `200 OK`
```json
{
  "unread_count": 3,
  "notifications": []
}
```

---

### PATCH `/notifications/{notification_id}/read` — Mark as Read

**Response** `200 OK`
```json
{ "message": "Notification marked as read.", "data": {...} }
```

---

### PATCH `/notifications/read-all` — Mark All as Read

**Response** `200 OK`
```json
{ "message": "5 notifications marked as read.", "count": 5 }
```

---

## 11. Files

> All endpoints require authentication.
> **Limits**: Max file size = 10MB (configurable via `MAX_FILE_SIZE_MB`). Allowed types: jpg, jpeg, png, gif, webp, pdf, doc, docx, xls, xlsx, ppt, pptx, txt, csv, zip (configurable via `ALLOWED_FILE_EXTENSIONS`).

### POST `/files/upload` — Upload File

| Item | Value |
|------|-------|
| Content-Type | `multipart/form-data` |

| Parameter | Type | In | Required | Default | Description |
|-----------|------|-----|----------|---------|-------------|
| `file` | UploadFile | body | Yes | - | File to upload |
| `folder` | string | query | No | `uploads` | Storage folder |

**Response** `200 OK`
```json
{
  "file_url": "https://storage.example.com/uploads/abc123.png",
  "file_name": "abc123.png",
  "file_size": 102400,
  "content_type": "image/png"
}
```

**Error Responses**

| Status | Condition | Detail |
|--------|-----------|--------|
| 400 | File type not in allowed list | `"File type '.exe' is not allowed."` |
| 413 | File exceeds size limit | `"File size exceeds 10MB limit."` |

---

### POST `/files/presigned-url` — Get Presigned URL

**Request Body**
```json
{ "file_path": "uploads/abc123.png" }
```

**Response** `200 OK`
```json
{ "url": "https://storage.example.com/signed/..." }
```

---

### DELETE `/files/delete` — Delete File

**Request Body**
```json
{ "file_path": "uploads/abc123.png" }
```

**Response** `200 OK`
```json
{ "message": "File deleted successfully." }
```

---

## 12. Setup

> System initialization endpoint. No authentication required (intended for first-time setup).

### POST `/setup/init` — Initialize System

| Item | Value |
|------|-------|
| Auth | Not required |

Creates the initial company and admin account. Idempotent for company creation; returns `409` if the admin user already exists.

**Request Body** (all fields have defaults)
```json
{
  "company_code": "SCR",
  "company_name": "SCR",
  "admin_login_id": "admin",
  "admin_password": "admin1234",
  "admin_email": "admin@scr.com",
  "admin_name": "Admin"
}
```

**Response** `200 OK`
```json
{
  "message": "System initialized successfully.",
  "company": {
    "id": "uuid",
    "code": "SCR"
  },
  "admin": {
    "id": "uuid",
    "login_id": "admin"
  }
}
```

**Error** `409`
```json
{ "detail": "User 'admin' already exists." }
```

---

## 13. Health Check

> Root-level endpoints for health monitoring. No authentication required.

### GET `/` — Root

**Response** `200 OK`
```json
{ "message": "Welcome to Task Server API" }
```

---

### GET `/health` — Health Check

**Response** `200 OK`
```json
{ "status": "healthy" }
```

---

## 14. Schema Definitions

### User

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | User ID (UUID) |
| email | string | No | Email (for SMTP verification & notifications) |
| login_id | string | No | Login ID |
| full_name | string | No | Full name |
| company_id | string | No | Company ID |
| role | UserRole | No | `staff` / `manager` / `admin` |
| status | UserStatus | No | `pending` / `active` / `inactive` |
| language | string | No | Language (default: `en`) |
| email_verified | boolean | No | Email verification status |
| profile_image | string | Yes | Profile image URL |
| join_date | datetime | Yes | Join date |
| created_at | datetime | No | Created at |
| updated_at | datetime | No | Updated at |

### Assignment

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Assignment ID (UUID) |
| company_id | string | No | Company ID |
| branch_id | string | Yes | Branch ID |
| title | string | No | Title |
| description | string | Yes | Description |
| priority | Priority | No | `urgent` / `normal` / `low` |
| status | AssignmentStatus | No | `todo` / `in_progress` / `done` |
| due_date | datetime | Yes | Due date |
| recurrence | object | Yes | Recurrence rule (JSONB) |
| created_by | string | No | Creator user ID |
| created_at | datetime | No | Created at |
| updated_at | datetime | No | Updated at |
| assignees | AssignmentAssignee[] | No | Assigned users (N:M) |
| comments | Comment[] | No | Comments |

### AssignmentAssignee

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| assignment_id | string | No | Assignment ID |
| user_id | string | No | User ID |
| assigned_at | datetime | No | Assignment timestamp |

### Comment

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Comment ID |
| assignment_id | string | No | Assignment ID |
| user_id | string | No | Author user ID |
| user_name | string | Yes | Author name (denormalized) |
| is_manager | boolean | No | Whether author is manager/admin |
| content | string | Yes | Text content |
| content_type | ContentType | No | `text` / `image` / `video` / `file` |
| attachments | object[] | Yes | Attachment metadata (JSONB) |
| created_at | datetime | No | Created at |

### DailyChecklist

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Checklist ID |
| template_id | string | No | Source template ID |
| branch_id | string | No | Branch ID |
| date | string | No | Date (YYYY-MM-DD) |
| checklist_data | object[] | No | JSONB snapshot of checklist items |
| group_ids | string[] | Yes | Group combination (UUID array) |
| created_at | datetime | No | Created at |

### Notice

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Notice ID |
| company_id | string | No | Company ID |
| branch_id | string | Yes | Branch ID (null = company-wide) |
| author_id | string | Yes | Author user ID |
| author_name | string | No | Author name (denormalized) |
| author_role | string | Yes | Author role (denormalized) |
| title | string | No | Title |
| content | string | No | Content |
| is_important | boolean | No | Important flag |
| created_at | datetime | No | Created at |

### AttendanceRecord

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Record ID |
| company_id | string | No | Company ID |
| user_id | string | No | User ID |
| branch_id | string | Yes | Branch ID |
| clock_in | datetime | **Yes** | Clock-in time (nullable) |
| clock_out | datetime | Yes | Clock-out time |
| location | string | Yes | Location info |
| status | string | No | Attendance status |
| work_hours | float | Yes | Work hours (calculated on clock-out) |

### Notification

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Notification ID |
| company_id | string | No | Company ID |
| user_id | string | No | Recipient user ID |
| type | NotificationType | No | Notification type |
| title | string | No | Title |
| message | string | No | Message body |
| reference_id | string | Yes | Referenced resource ID |
| reference_type | string | Yes | Referenced resource type |
| action_url | string | Yes | Deep link URL |
| is_read | boolean | No | Read status (default: false) |
| created_at | datetime | No | Created at |

### Opinion

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Opinion ID |
| company_id | string | No | Company ID |
| user_id | string | No | Author user ID |
| content | string | No | Content |
| status | OpinionStatus | No | Processing status |
| created_at | datetime | No | Created at |

### Feedback

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Feedback ID |
| company_id | string | No | Company ID |
| assignment_id | string | Yes | Related assignment ID |
| branch_id | string | Yes | Related branch ID |
| author_id | string | No | Author user ID |
| target_user_id | string | Yes | Target user ID |
| content | string | No | Feedback content |
| status | string | Yes | Feedback status |
| created_at | datetime | No | Created at |

---

## 15. Enum Definitions

### UserRole
| Value | Description |
|-------|-------------|
| `staff` | Regular employee |
| `manager` | Manager |
| `admin` | Administrator |

### UserStatus
| Value | Description |
|-------|-------------|
| `pending` | Pending approval |
| `active` | Active |
| `inactive` | Inactive |

### Priority
| Value | Description |
|-------|-------------|
| `urgent` | Urgent |
| `normal` | Normal |
| `low` | Low |

### AssignmentStatus
| Value | Description |
|-------|-------------|
| `todo` | To do |
| `in_progress` | In progress |
| `done` | Done |

### AttendanceStatus
| Value | Description |
|-------|-------------|
| `not_started` | Not clocked in |
| `on_duty` | On duty |
| `off_duty` | Off duty |
| `completed` | Completed |

### NotificationType
| Value | Description |
|-------|-------------|
| `task_assigned` | Assignment notification |
| `task_updated` | Assignment update |
| `notice` | Notice notification |
| `feedback` | Feedback notification |
| `comment` | Comment notification |
| `system` | System notification |

### OpinionStatus
| Value | Description |
|-------|-------------|
| `submitted` | Submitted |
| `reviewed` | Under review |
| `resolved` | Resolved |

### ContentType
| Value | Description |
|-------|-------------|
| `text` | Text |
| `image` | Image |
| `video` | Video |
| `file` | File |

### VerificationType
| Value | Description |
|-------|-------------|
| `none` | No verification |
| `photo` | Photo verification |
| `signature` | Signature verification |

---

## 16. Error Responses

### Common Error Format

All errors follow FastAPI's standard format:

```json
{ "detail": "Error message here." }
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid input, business rule violation |
| 401 | Unauthorized | Missing/invalid/expired token |
| 403 | Forbidden | Insufficient role |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Unhandled exception |

### Auth-specific Errors

| Endpoint | Code | Detail |
|----------|------|--------|
| Login | 401 | `"Invalid login ID or password."` |
| Signup | 400 | `"Login ID is already taken."` |
| Signup | 400 | `"Email is already registered."` |
| Signup | 400 | `"Invalid company code: {code}"` |
| Refresh | 401 | `"Token refresh failed."` |
| Any auth | 401 | `"Authorization token is missing."` |
| Any auth | 401 | `"Token has expired."` |
| Any auth | 401 | `"Invalid token."` |
| Role check | 403 | `"Access denied. Required roles: [...]"` |

### Global Error Handler

Unhandled exceptions return:
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Internal server error."
  }
}
```

---

## v1 → v2 Migration Summary

| Category | v1 | v2 |
|----------|-----|-----|
| Auth backend | Supabase Auth | Custom JWT + bcrypt |
| Email verification | Supabase built-in | Google SMTP |
| Login field | email | login_id |
| Signup field | branch_id | company_code |
| Task system | `/tasks` (single type) | `/assignments` + `/daily-checklists` |
| Assignees | `assigned_to` (1:1) | `assignment_assignees` (N:M) |
| Comments | `task_id` | `assignment_id` + multimedia |
| Organization | brand → branch → group | company → brand → branch → group_type → group |
| Multi-tenancy | None | `company_id` scoping on all endpoints |
| API language | Korean | English |
| Token type | Supabase JWT | Custom HS256 JWT |
| Password storage | Supabase Auth | bcrypt in `users.password_hash` |
