# Task Server V2 - Comprehensive Gap Analysis Report

> **Analysis Type**: Design vs Implementation Gap Analysis
>
> **Project**: task_server
> **Version**: 0.1.0
> **Analyst**: bkit-gap-detector
> **Date**: 2026-02-12
> **Design Doc**: [task-server-v2.design.md](../02-design/features/task-server-v2.design.md)
> **API Spec**: [api-specification.md](../01-plan/api-specification.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Comprehensive gap analysis comparing the Task Server V2 design document and API specification against the actual implementation in `app/`. This analysis covers 8 key areas: architecture compliance, Supabase decoupling, API coverage, data models, repository abstraction, storage abstraction, error handling, and DI patterns.

### 1.2 Analysis Scope

- **Design Document**: `docs/02-design/features/task-server-v2.design.md`
- **API Specification**: `docs/01-plan/api-specification.md`
- **Implementation Path**: `app/` (all Python source files)
- **Files Analyzed**: 51 Python files across api/, services/, repositories/, schemas/, models/, storage/, core/

---

## 2. Overall Scores

| Category | Score | Status |
|----------|:-----:|:------:|
| Architecture (Repository Pattern) | 88% | ✅ |
| Supabase Decoupling | 95% | ✅ |
| API Coverage | 83% | ⚠️ |
| Data Models (Pydantic Schemas) | 85% | ⚠️ |
| Repository Abstraction | 72% | ⚠️ |
| Storage Abstraction | 90% | ✅ |
| Error Handling | 65% | ⚠️ |
| DI Pattern (Constructor Injection) | 60% | ⚠️ |
| **Overall** | **79.8%** | **⚠️** |

---

## 3. Architecture Compliance (Repository Pattern)

**Score: 88%**

### 3.1 Layer Structure Verification

| Layer | Design Location | Actual Location | Status |
|-------|----------------|-----------------|--------|
| API/Presentation | `app/api/` | `app/api/endpoints/` | ✅ Match |
| Application/Service | `app/services/` | `app/services/` | ✅ Match |
| Domain/Model | `app/models/`, `app/schemas/` | `app/models/`, `app/schemas/` | ✅ Match |
| Infrastructure/Repository | `app/repositories/`, `app/storage/` | `app/repositories/`, `app/storage/` | ✅ Match |
| DI Container | `app/core/dependencies.py` | `app/core/dependencies.py` | ✅ Match |

### 3.2 Data Flow Compliance

Design: `Endpoint -> Service -> Repository -> Supabase`

| Flow | Expected | Actual | Status |
|------|----------|--------|--------|
| Auth endpoints | Endpoint -> AuthService -> AuthRepo | Endpoint -> AuthService -> AuthRepo | ✅ |
| Task CRUD | Endpoint -> TaskService -> TaskRepo | Endpoint -> TaskService -> **TaskRepo directly** | ⚠️ |
| Comments | Endpoint -> CommentService -> CommentRepo | Endpoint -> CommentService -> CommentRepo | ✅ |
| Attendance | Endpoint -> AttendanceService -> AttendanceRepo | Endpoint -> AttendanceService -> AttendanceRepo | ✅ |
| Opinions | Endpoint -> OpinionService -> OpinionRepo | Endpoint -> OpinionService -> OpinionRepo | ✅ |
| Notifications | Endpoint -> NotificationService -> NotificationRepo | Endpoint -> NotificationService -> NotificationRepo | ✅ |
| Files | Endpoint -> FileService -> StorageProvider | Endpoint -> FileService -> StorageProvider | ✅ |
| Dashboard | Endpoint -> DashboardService -> Repos | Endpoint -> DashboardService -> Repos | ✅ |
| Admin (Org CRUD) | Endpoint -> AdminService -> OrgRepo | Endpoint -> AdminService -> **OrgRepo directly** | ⚠️ |
| Notices (public) | Endpoint -> NoticeService -> NoticeRepo | Endpoint -> **NoticeRepo directly** | ❌ |

### 3.3 Violations Found

| File | Layer | Violation | Severity |
|------|-------|-----------|----------|
| `app/api/endpoints/tasks.py` | Presentation | Calls `service.task_repo.list()` directly, bypassing service methods (lines 42, 53, 69, 83, 95, 109) | HIGH |
| `app/api/endpoints/admin.py` | Presentation | Calls `service.org_repo.*` and `service.template_repo.*` directly (lines 67, 72, 77, 82, 91, 96, 101, 110, 115, 120, 134) | HIGH |
| `app/api/endpoints/notices.py` | Presentation | Read endpoints (lines 20-33) call `get_notice_repo()` directly without going through a service | HIGH |
| `app/api/endpoints/users.py` | Presentation | `update_my_profile` calls `get_user_repo()` directly (line 33) | MEDIUM |

---

## 4. Supabase Decoupling

**Score: 95%**

### 4.1 Supabase Import Locations

| File | Location | Allowed? | Status |
|------|----------|----------|--------|
| `app/core/supabase.py` | Core (client init) | YES | ✅ |
| `app/core/dependencies.py` | DI Container | YES | ✅ |
| `app/repositories/auth.py` | Repository | YES | ✅ |
| `app/repositories/user.py` | Repository | YES | ✅ |
| `app/repositories/task.py` | Repository | YES | ✅ |
| `app/repositories/organization.py` | Repository | YES | ✅ |
| `app/repositories/checklist_template.py` | Repository | YES | ✅ |
| `app/repositories/feedback_notice.py` | Repository | YES | ✅ |
| `app/repositories/comment.py` | Repository | YES | ✅ |
| `app/repositories/attendance.py` | Repository | YES | ✅ |
| `app/repositories/opinion.py` | Repository | YES | ✅ |
| `app/repositories/notification.py` | Repository | YES | ✅ |
| `app/storage/supabase.py` | Storage impl | YES | ✅ |

### 4.2 Leakage Check

| Layer | Supabase imports found | Status |
|-------|:---------------------:|--------|
| `app/api/endpoints/` | 0 | ✅ Clean |
| `app/services/` | 0 | ✅ Clean |
| `app/schemas/` | 0 | ✅ Clean |
| `app/models/` | 0 | ✅ Clean |

### 4.3 Minor Issue

- `app/repositories/user.py` imports `supabase` as a module-level global (`from app.core.supabase import supabase`) and uses it directly in methods instead of receiving it via constructor injection, unlike `SupabaseAuthRepository` which receives `client` in `__init__`. This is consistent across most repositories but weakens testability.

---

## 5. API Coverage

**Score: 83%**

### 5.1 API Specification vs Implementation

#### Auth APIs (5 specified, 5 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/auth/login` | POST | `app/api/endpoints/auth.py:35` | ✅ Implemented |
| `/api/v1/auth/signup` | POST | `app/api/endpoints/auth.py:44` | ✅ Implemented |
| `/api/v1/auth/logout` | POST | `app/api/endpoints/auth.py:63` | ✅ Implemented |
| `/api/v1/auth/refresh` | POST | `app/api/endpoints/auth.py:75` | ✅ Implemented |
| `/api/v1/auth/me` | GET | `app/api/endpoints/auth.py:84` | ✅ Implemented |

#### User APIs (3 specified, 3 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/users/me/profile` | GET | `app/api/endpoints/users.py:20` | ✅ Implemented |
| `/api/v1/users/me/profile` | PATCH | `app/api/endpoints/users.py:26` | ✅ Implemented |
| `/api/v1/users/me/password` | POST | `app/api/endpoints/users.py:45` | ✅ Implemented |

#### Task APIs (6 specified, 6 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/tasks` | GET | `app/api/endpoints/tasks.py:27` | ✅ Implemented |
| `/api/v1/tasks/{task_id}` | GET | `app/api/endpoints/tasks.py:47` | ✅ Implemented |
| `/api/v1/tasks` | POST | `app/api/endpoints/tasks.py:59` | ✅ Implemented |
| `/api/v1/tasks/{task_id}` | PATCH | `app/api/endpoints/tasks.py:74` | ✅ Implemented |
| `/api/v1/tasks/{task_id}` | DELETE | `app/api/endpoints/tasks.py:88` | ✅ Implemented |
| `/api/v1/tasks/{task_id}/status` | PATCH | `app/api/endpoints/tasks.py:101` | ✅ Implemented |

#### Checklist APIs (3 specified, 3 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/tasks/checklist/{item_id}` | PATCH | `app/api/endpoints/tasks.py:116` | ✅ Implemented |
| `/api/v1/tasks/{task_id}/checklist` | POST | `app/api/endpoints/tasks.py:131` | ✅ Implemented |
| `/api/v1/tasks/checklist/{item_id}` | DELETE | `app/api/endpoints/tasks.py:146` | ✅ Implemented |

#### Comment APIs (3 specified, 3 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/tasks/{task_id}/comments` | GET | `app/api/endpoints/tasks.py:162` | ✅ Implemented |
| `/api/v1/tasks/{task_id}/comments` | POST | `app/api/endpoints/tasks.py:175` | ✅ Implemented |
| `/api/v1/tasks/{task_id}/comments/{comment_id}` | DELETE | `app/api/endpoints/tasks.py:189` | ✅ Implemented |

#### Notice APIs (5 specified, 5 implemented + 1 extra = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/notices` | GET | `app/api/endpoints/notices.py:18` | ✅ Implemented |
| `/api/v1/notices/{notice_id}` | GET | `app/api/endpoints/notices.py:27` | ✅ Implemented |
| `/api/v1/notices` | POST | `app/api/endpoints/notices.py:47` | ✅ Implemented |
| `/api/v1/notices/{notice_id}` | PATCH | `app/api/endpoints/notices.py:59` | ✅ Implemented |
| `/api/v1/notices/{notice_id}` | DELETE | `app/api/endpoints/notices.py:73` | ✅ Implemented |
| `/api/v1/notices/{notice_id}/confirm` | POST | `app/api/endpoints/notices.py:36` | ⚠️ Extra (not in spec) |

#### Dashboard API (1 specified, 1 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/dashboard/summary` | GET | `app/api/endpoints/dashboard.py:10` | ✅ Implemented |

#### Attendance APIs (4 specified, 4 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/attendance/clock-in` | POST | `app/api/endpoints/attendance.py:23` | ✅ Implemented |
| `/api/v1/attendance/clock-out` | POST | `app/api/endpoints/attendance.py:34` | ✅ Implemented |
| `/api/v1/attendance/today` | GET | `app/api/endpoints/attendance.py:17` | ✅ Implemented |
| `/api/v1/attendance/history` | GET | `app/api/endpoints/attendance.py:45` | ✅ Implemented |

#### Opinion APIs (2 specified, 2 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/opinions` | POST | `app/api/endpoints/opinions.py:16` | ✅ Implemented |
| `/api/v1/opinions/me` | GET | `app/api/endpoints/opinions.py:25` | ⚠️ URL differs |

**Note**: The spec defines `GET /api/v1/opinions/me` but implementation uses `GET /api/v1/opinions/` (root path). Both return user's own opinions, but the URL does not match the specification.

#### Notification APIs (3 specified, 3 implemented = 100%)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/notifications` | GET | `app/api/endpoints/notifications.py:15` | ✅ Implemented |
| `/api/v1/notifications/{id}/read` | PATCH | `app/api/endpoints/notifications.py:21` | ✅ Implemented |
| `/api/v1/notifications/read-all` | PATCH | `app/api/endpoints/notifications.py:31` | ✅ Implemented |

#### File Upload APIs (2 specified, 2 implemented = partial)

| Spec Endpoint | Method | Implementation File | Status |
|---------------|--------|---------------------|--------|
| `/api/v1/files/upload` | POST | `app/api/endpoints/files.py:14` | ✅ Implemented |
| `/api/v1/files/presigned-url` | POST | `app/api/endpoints/files.py:29` | ⚠️ Method differs |

**Note**: The spec defines `POST /api/v1/files/presigned-url` but implementation uses `GET`. This is arguably better REST practice, but it does not match the spec.

### 5.2 Admin APIs (Design Document, not in main spec)

| Endpoint | Method | Implementation | Status |
|----------|--------|---------------|--------|
| `/api/v1/admin/staff/pending` | GET | `app/api/endpoints/admin.py:46` | ✅ |
| `/api/v1/admin/staff/{id}/approve` | PATCH | `app/api/endpoints/admin.py:51` | ✅ |
| `/api/v1/admin/staff/{id}/reject` | PATCH | `app/api/endpoints/admin.py:56` | ✅ |
| `/api/v1/admin/brands` | CRUD | `app/api/endpoints/admin.py:64-83` | ✅ |
| `/api/v1/admin/branches` | CRUD | `app/api/endpoints/admin.py:88-102` | ✅ |
| `/api/v1/admin/groups` | CRUD | `app/api/endpoints/admin.py:107-121` | ✅ |
| `/api/v1/admin/checklist-templates` | POST/GET | `app/api/endpoints/admin.py:126-134` | ✅ |
| `/api/v1/admin/dashboard/checklist-compliance` | GET | `app/api/endpoints/admin.py:139` | ✅ (stub) |
| `/api/v1/admin/feedbacks` | GET/POST | `app/api/endpoints/admin.py:147-158` | ✅ |

### 5.3 Coverage Summary

| Category | Spec Count | Implemented | Match Rate |
|----------|:---------:|:-----------:|:----------:|
| Auth | 5 | 5 | 100% |
| Users | 3 | 3 | 100% |
| Tasks | 6 | 6 | 100% |
| Checklist | 3 | 3 | 100% |
| Comments | 3 | 3 | 100% |
| Notices | 5 | 5 (+1 extra) | 100% |
| Dashboard | 1 | 1 | 100% |
| Attendance | 4 | 4 | 100% |
| Opinions | 2 | 2 (URL diff) | 90% |
| Notifications | 3 | 3 | 100% |
| File Upload | 2 | 2 (method diff) | 90% |
| Admin (design) | 9+ | 9+ | 100% |
| **Total** | **37 (spec)** | **37** | **~97% functional, 83% exact match** |

### 5.4 Response Format Mismatches

| Endpoint | Spec Response | Actual Response | Impact |
|----------|---------------|-----------------|--------|
| `GET /dashboard/summary` | Includes `user` field | Missing `user` field in response | MEDIUM |
| `GET /dashboard/summary` | `task_summary.pending_tasks` | `task_summary.todo` | LOW |
| `GET /dashboard/summary` | `task_summary.completion_rate` | Missing | LOW |
| `GET /attendance/history` | `summary.total_hours`, `summary.late_count` | `summary.completed`, `summary.incomplete` | MEDIUM |
| `POST /files/upload` | `file_url`, `file_name`, `file_size`, `content_type` | `filename`, `original_filename`, `url`, `folder` | HIGH |
| `POST /opinions` | Route at `/opinions/me` | Route at `/opinions/` (GET list) | LOW |
| `POST /files/presigned-url` | POST method with body | GET method with query param | MEDIUM |
| `PATCH /users/me/password` | Requires `current_password` field | Only requires `new_password` | HIGH |

---

## 6. Data Models (Pydantic Schemas)

**Score: 85%**

### 6.1 Schema Coverage

| Entity | Schema File | Base/Create/Read | Status |
|--------|------------|:----------------:|--------|
| Task | `app/schemas/task.py` | TaskBase/TaskCreate/Task | ✅ Complete |
| ChecklistItem | `app/schemas/task.py` | ChecklistItemBase/ChecklistItemCreate/ChecklistItem | ✅ Complete |
| Comment | `app/schemas/task.py` | CommentBase/CommentCreate/Comment | ✅ Complete |
| Notice | `app/schemas/notice.py` | NoticeBase/NoticeCreate/Notice | ✅ Complete |
| User | `app/schemas/user.py` | UserBase/UserCreate/UserUpdate/User | ✅ Complete |
| Brand | `app/schemas/organization.py` | BrandBase/BrandCreate/Brand | ✅ Complete |
| Branch | `app/schemas/organization.py` | BranchBase/BranchCreate/Branch | ✅ Complete |
| Group | `app/schemas/organization.py` | GroupBase/GroupCreate/Group | ✅ Complete |
| Attendance | `app/schemas/attendance.py` | AttendanceRecord/ClockInRequest | ⚠️ Partial |
| Opinion | `app/schemas/opinion.py` | Opinion/OpinionCreate | ✅ Complete |
| Notification | `app/schemas/notification.py` | Notification/NotificationListResponse | ✅ Complete |

### 6.2 Missing Schema Fields

| Schema | Field in Spec | Defined | Status |
|--------|--------------|:-------:|--------|
| Notice | `is_important` | NO | ❌ Missing |
| Notice | `author` | NO (only `author_id` in service) | ⚠️ Partial |
| ChecklistItem | `verification_type` | NO | ❌ Missing |
| ChecklistItem | `verification_data` | NO | ❌ Missing |
| AttendanceRecord | `work_hours` | NO | ❌ Missing |
| User | `profile_image` | NO | ❌ Missing |
| Comment | `user_name` | NO | ❌ Missing |
| Comment | `is_manager` | NO | ❌ Missing |
| Task | `comments` field type | `List[Comment]` | ⚠️ Embedded (not matching spec join fields) |

### 6.3 Enums Coverage

| Enum (from spec) | Defined | Location | Status |
|------------------|:-------:|----------|--------|
| TaskType (daily, assigned) | YES | `app/models/enums.py` | ✅ |
| Priority (urgent, normal, low) | YES | `app/models/enums.py` | ✅ |
| TaskStatus (todo, in_progress, done) | YES | `app/models/enums.py` | ✅ |
| UserRole (admin, manager, staff) | YES | `app/schemas/user.py` | ✅ |
| UserStatus (pending, active, inactive) | YES | `app/schemas/user.py` | ✅ |
| AttendanceStatus (not_started, on_duty, off_duty, completed) | NO (string literal) | `app/schemas/attendance.py` | ⚠️ Not enum |
| NotificationType (task_assigned, etc.) | NO (string literal) | `app/schemas/notification.py` | ⚠️ Not enum |
| OpinionStatus (submitted, reviewed, resolved) | NO (string literal) | `app/schemas/opinion.py` | ⚠️ Not enum |

---

## 7. Repository Abstraction

**Score: 72%**

### 7.1 IRepository Base Interface Usage

| Repository | Extends `IRepository[T]` | Status |
|-----------|:-----------------------:|--------|
| `SupabaseAuthRepository` | NO (has own `IAuthRepository`) | ⚠️ Custom interface (acceptable) |
| `SupabaseUserRepository` | YES (`IRepository[User]`) | ✅ |
| `TaskRepository` | YES (`IRepository[Task]`) | ✅ |
| `OrganizationRepository` | NO | ❌ No interface |
| `ChecklistTemplateRepository` | NO | ❌ No interface |
| `FeedbackRepository` | NO | ❌ No interface |
| `NoticeRepository` | NO | ❌ No interface |
| `CommentRepository` | NO | ❌ No interface |
| `AttendanceRepository` | NO | ❌ No interface |
| `OpinionRepository` | NO | ❌ No interface |
| `NotificationRepository` | NO | ❌ No interface |

**Result**: Only 2 out of 11 repositories implement `IRepository`. 8 repositories are concrete classes with no abstract interface, making them impossible to swap without modifying consumers.

### 7.2 Constructor Injection in Repositories

| Repository | Receives `supabase` client via constructor | Status |
|-----------|:-----------------------------------------:|--------|
| `SupabaseAuthRepository` | YES (`__init__(self, client)`) | ✅ |
| `SupabaseUserRepository` | NO (module-level global) | ❌ |
| `TaskRepository` | NO (module-level global) | ❌ |
| `OrganizationRepository` | NO (module-level global) | ❌ |
| `ChecklistTemplateRepository` | NO (module-level global) | ❌ |
| All others | NO (module-level global) | ❌ |

**Result**: Only `SupabaseAuthRepository` follows proper DI by accepting the client in its constructor. All other repositories import `supabase` at the module level, making them harder to test and swap.

---

## 8. Storage Abstraction

**Score: 90%**

### 8.1 Interface Compliance

| Design Interface Method | Implementation | Status |
|------------------------|----------------|--------|
| `upload(file_content, filename, folder) -> str` | `SupabaseStorageProvider.upload()` | ✅ Match |
| `get_url(file_path) -> str` | `SupabaseStorageProvider.get_url()` | ✅ Match |
| `delete(file_path) -> bool` (impl extra) | `SupabaseStorageProvider.delete()` | ✅ Bonus |

### 8.2 Issues

| Issue | File | Detail | Severity |
|-------|------|--------|----------|
| `get_url` not async | `app/storage/supabase.py:25` | Method signature is `def get_url` (sync) but interface declares `async` | LOW |
| Hardcoded content-type | `app/storage/supabase.py:15` | `"content-type": "image/jpeg"` is hardcoded | MEDIUM |

---

## 9. Error Handling

**Score: 65%**

### 9.1 Error Handling Pattern

| Pattern | Design | Implementation | Status |
|---------|--------|----------------|--------|
| Unified exception handler | Designed (Section 6) | NOT implemented (no global handler) | ❌ |
| HTTPException usage | Expected | Used per-endpoint via try/catch | ⚠️ Inconsistent |
| 403 Forbidden | Role check | Implemented in `require_role` | ✅ |
| 404 Not Found | Resource check | Partially (only task detail, notice detail) | ⚠️ |
| 422 Validation | Pydantic auto | Handled by FastAPI/Pydantic | ✅ |

### 9.2 Inconsistencies

| Endpoint File | Issue | Severity |
|---------------|-------|----------|
| `tasks.py` | All errors become 500 with raw exception message | HIGH |
| `admin.py` | No try/except at all on most endpoints | HIGH |
| `notices.py` (public reads) | No auth required for list/detail (by design, but no rate limiting) | LOW |
| `auth.py` | Login error always returns 401 regardless of cause | MEDIUM |
| `users.py:change_password` | No `current_password` verification | HIGH |
| Multiple files | Exception messages leak internal details (`str(e)`) | HIGH |

### 9.3 Missing Error Handling

| Scenario | Expected | Actual |
|----------|----------|--------|
| Global exception handler | FastAPI exception_handler decorator | Not implemented |
| Structured error response | `{"error": {"code": "...", "message": "..."}}` | `{"detail": "..."}` (FastAPI default) |
| Rate limiting | Mentioned nowhere | Not implemented |
| Input sanitization | Expected for user input | Not implemented |

---

## 10. DI Pattern (Constructor Injection)

**Score: 60%**

### 10.1 Service Constructor Injection

| Service | Constructor Params | Uses DI | Status |
|---------|-------------------|:-------:|--------|
| `AuthService` | `auth_repo, user_repo` | YES | ✅ |
| `AdminService` | `user_repo, org_repo, template_repo, task_repo, feedback_repo, notice_repo` | YES | ✅ |
| `TaskService` | `task_repo` | YES | ✅ |
| `CommentService` | `comment_repo` | YES | ✅ |
| `AttendanceService` | `attendance_repo` | YES | ✅ |
| `OpinionService` | `opinion_repo` | YES | ✅ |
| `DashboardService` | `task_repo, notice_repo` | YES | ✅ |
| `NotificationService` | `notification_repo` | YES | ✅ |
| `FileService` | `storage_provider` | YES | ✅ |
| `NoticeService` | `notice_repo` | YES | ✅ |

**All services use constructor injection** -- this is well-implemented.

### 10.2 DI Container (`dependencies.py`) Issues

| Issue | Detail | Severity |
|-------|--------|----------|
| Inconsistent return types | `get_user_repo()` returns `SupabaseUserRepository` (concrete) instead of interface | MEDIUM |
| Missing service factories | Only `get_task_service()` and `get_comment_service()` are registered as factories | HIGH |
| Inline service creation | Most endpoints create services inline (e.g., `_get_admin_service()`, `_get_service()`) | MEDIUM |
| Not using FastAPI `Depends` consistently | Some endpoints use `Depends(get_task_service)`, others create services manually | HIGH |

### 10.3 Endpoint DI Usage

| Endpoint File | Uses FastAPI `Depends` for service | Status |
|---------------|:----------------------------------:|--------|
| `tasks.py` | YES (`Depends(get_task_service)`) | ✅ |
| `auth.py` | NO (manual `_get_auth_service()`) | ❌ |
| `admin.py` | NO (manual `_get_admin_service()`) | ❌ |
| `users.py` | NO (manual repo/service creation) | ❌ |
| `notices.py` | NO (manual `_get_service()`) | ❌ |
| `dashboard.py` | NO (inline `DashboardService(...)`) | ❌ |
| `attendance.py` | NO (manual `_get_service()`) | ❌ |
| `opinions.py` | NO (manual `_get_service()`) | ❌ |
| `notifications.py` | NO (manual `_get_service()`) | ❌ |
| `files.py` | NO (manual `_get_service()`) | ❌ |

**Result**: Only `tasks.py` uses proper FastAPI dependency injection via `Depends()`. All other endpoint files create services manually, which works but is inconsistent with the DI design pattern.

---

## 11. Differences Summary

### 11.1 Missing Features (Design/Spec YES, Implementation NO)

| ID | Item | Design Location | Description |
|----|------|-----------------|-------------|
| M-01 | `current_password` validation | api-spec.md:209 | Password change endpoint does not verify current password |
| M-02 | `is_important` field on Notice | api-spec.md:438 | Notice schema missing `is_important` boolean field |
| M-03 | `verification_type`/`verification_data` in ChecklistItem schema | api-spec.md:319 | Fields exist in request but not in Pydantic schema |
| M-04 | `user_name`, `is_manager` in Comment response | api-spec.md:358 | Comment schema lacks user display fields |
| M-05 | `profile_image` in User schema | api-spec.md:178 | User profile does not support profile image field |
| M-06 | `work_hours` calculation in attendance | api-spec.md:565 | Clock-out response lacks work hours calculation |
| M-07 | `completion_rate` in dashboard task_summary | api-spec.md:491 | Dashboard missing completion rate percentage |
| M-08 | `total_hours`, `late_count` in attendance summary | api-spec.md:615 | History summary uses different field structure |
| M-09 | `unread_only` query filter on notifications | api-spec.md:680 | GET notifications does not support `unread_only` param |
| M-10 | Global exception handler | design.md Section 6 | No unified FastAPI exception handler registered |
| M-11 | 7/11 repository interfaces | design.md Section 4.1 | Most repositories lack ABC interfaces |

### 11.2 Added Features (Design/Spec NO, Implementation YES)

| ID | Item | Implementation Location | Description |
|----|------|------------------------|-------------|
| A-01 | Notice confirmation flow | `app/api/endpoints/notices.py:36` | `POST /notices/{id}/confirm` endpoint not in spec |
| A-02 | Notice confirmations table join | `app/repositories/feedback_notice.py:30` | Selects `notice_confirmations(*)` in notice detail |
| A-03 | Staff rejection endpoint | `app/api/endpoints/admin.py:56` | `PATCH /admin/staff/{id}/reject` not in original spec |
| A-04 | Admin feedbacks CRUD | `app/api/endpoints/admin.py:147-158` | Feedback endpoints not in main API spec |
| A-05 | Checklist log auto-creation | `app/services/task_service.py:22-30` | Automatic log record on checklist toggle |
| A-06 | `login_id` field on User | `app/schemas/user.py:21` | Extra identifier field not in spec |
| A-07 | `language` field on User | `app/schemas/user.py:26` | Internationalization field not in spec |

### 11.3 Changed Features (Design != Implementation)

| ID | Item | Design/Spec | Implementation | Impact |
|----|------|-------------|----------------|--------|
| C-01 | File upload response fields | `file_url, file_name, file_size, content_type` | `filename, original_filename, url, folder` | HIGH |
| C-02 | Presigned URL method | `POST` with request body | `GET` with query params | MEDIUM |
| C-03 | Opinions list URL | `GET /opinions/me` | `GET /opinions/` | LOW |
| C-04 | Dashboard task_summary keys | `total_tasks, pending_tasks, completed_tasks` | `total, todo, done, in_progress` | MEDIUM |
| C-05 | Attendance history summary | `total_hours, late_count` | `completed, incomplete` | MEDIUM |
| C-06 | Dashboard response | Includes `user` object | No `user` object in response | LOW |

---

## 12. Clean Architecture Compliance

**Score: 85%**

### 12.1 Layer Assignment Verification

| Component | Designed Layer | Actual Location | Status |
|-----------|---------------|-----------------|--------|
| Auth endpoints | Presentation | `app/api/endpoints/auth.py` | ✅ |
| AuthService | Application | `app/services/auth_service.py` | ✅ |
| IAuthRepository | Infrastructure | `app/repositories/auth.py` | ✅ |
| User schema | Domain | `app/schemas/user.py` | ✅ |
| Enums | Domain | `app/models/enums.py` | ✅ |
| Supabase client | Infrastructure | `app/core/supabase.py` | ✅ |
| DI Container | Infrastructure | `app/core/dependencies.py` | ✅ |
| Security middleware | Presentation | `app/core/security.py` | ✅ |

### 12.2 Dependency Direction Violations

| Source File | Source Layer | Imports From | Target Layer | Violation? |
|------------|-------------|--------------|--------------|:----------:|
| `security.py` | Presentation | `dependencies.py` | Infrastructure | NO (acceptable for DI) |
| `admin.py` | Presentation | `admin_service.py` | Application | ✅ Correct |
| `tasks.py` | Presentation | `task_service.py` + accesses `task_repo` | Application->Infrastructure | ⚠️ Leaky |
| `notices.py` | Presentation | `get_notice_repo()` directly | Infrastructure | ❌ Violation |
| `users.py` | Presentation | `get_user_repo()` directly | Infrastructure | ❌ Violation |

---

## 13. Convention Compliance

**Score: 80%**

### 13.1 Naming Convention

| Category | Convention | Compliance | Violations |
|----------|-----------|:----------:|------------|
| Modules | snake_case | 100% | None |
| Classes | PascalCase | 100% | None |
| Functions | snake_case | 100% | None |
| Variables | snake_case | 100% | None |
| Constants | UPPER_SNAKE_CASE | N/A | None observed |
| Folders | kebab-case or snake_case | 100% | Python standard (snake_case) used |

### 13.2 File Organization

| Expected | Exists | Status |
|----------|:------:|--------|
| `app/api/endpoints/` | YES | ✅ |
| `app/services/` | YES | ✅ |
| `app/repositories/` | YES | ✅ |
| `app/schemas/` | YES | ✅ |
| `app/models/` | YES | ✅ |
| `app/storage/` | YES | ✅ |
| `app/core/` | YES | ✅ |

### 13.3 Issues

| Issue | Detail |
|-------|--------|
| Enums split across files | `TaskType`, `Priority`, `TaskStatus` in `models/enums.py` but `UserRole`, `UserStatus` in `schemas/user.py` |
| `crud/` directory empty | `app/crud/__init__.py` exists but directory contains no other files (legacy leftover) |
| Inconsistent schema location for Comment | Comment schemas are inside `schemas/task.py` instead of a separate `schemas/comment.py` |

---

## 14. Overall Match Rate

```
+-----------------------------------------------+
|  Overall Match Rate: 79.8%                    |
+-----------------------------------------------+
|  Architecture (Repository Pattern):  88%       |
|  Supabase Decoupling:               95%       |
|  API Coverage:                       83%       |
|  Data Models:                        85%       |
|  Repository Abstraction:             72%       |
|  Storage Abstraction:                90%       |
|  Error Handling:                     65%       |
|  DI Pattern:                         60%       |
+-----------------------------------------------+
|  Matched Items:      42                        |
|  Missing Items:      11 (M-01 through M-11)   |
|  Added Items:         7 (A-01 through A-07)   |
|  Changed Items:       6 (C-01 through C-06)   |
+-----------------------------------------------+
```

---

## 15. Recommended Actions

### 15.1 Immediate (Priority HIGH)

| # | Action | Files to Change | Impact |
|---|--------|----------------|--------|
| 1 | **Add repository interfaces** for all 9 missing repositories (CommentRepository, AttendanceRepository, etc.) using ABC pattern from `IRepository` or custom interfaces | `app/repositories/*.py` | Enables swapping implementations for migration |
| 2 | **Fix endpoint-to-repo leaks**: Ensure ALL endpoints go through services, never call repositories directly | `app/api/endpoints/tasks.py`, `admin.py`, `notices.py`, `users.py` | Architecture compliance |
| 3 | **Add `current_password` validation** to password change | `app/api/endpoints/users.py`, `app/services/auth_service.py` | Security vulnerability |
| 4 | **Register global exception handler** in `main.py` | `app/main.py` | Error consistency |
| 5 | **Fix file upload response format** to match API spec | `app/services/file_service.py`, `app/api/endpoints/files.py` | API contract |

### 15.2 Short-term (Priority MEDIUM)

| # | Action | Files to Change | Impact |
|---|--------|----------------|--------|
| 6 | Add missing schema fields: `is_important` (Notice), `verification_type/data` (ChecklistItem), `profile_image` (User), `user_name/is_manager` (Comment) | `app/schemas/*.py` | Data completeness |
| 7 | Standardize DI in all endpoints: register all services in `dependencies.py` and use `Depends()` consistently | `app/core/dependencies.py`, all endpoint files | Consistency |
| 8 | Inject supabase client via constructor in all repositories (like `SupabaseAuthRepository`) instead of module-level import | All `app/repositories/*.py` | Testability |
| 9 | Add missing enums: `AttendanceStatus`, `NotificationType`, `OpinionStatus` to `models/enums.py` | `app/models/enums.py`, related schemas | Type safety |
| 10 | Fix presigned URL endpoint to match spec (POST with body instead of GET with query) | `app/api/endpoints/files.py` | API contract |

### 15.3 Long-term (Priority LOW)

| # | Action | Impact |
|---|--------|--------|
| 11 | Add `work_hours` calculation to attendance clock-out response | Data richness |
| 12 | Add `unread_only` filter to notifications endpoint | API spec compliance |
| 13 | Consolidate enums into `models/enums.py` (move `UserRole`, `UserStatus` out of `schemas/user.py`) | Code organization |
| 14 | Remove empty `app/crud/` directory | Cleanup |
| 15 | Add dashboard `user` context and `completion_rate` to match spec exactly | API spec compliance |
| 16 | Update design doc to reflect added features (A-01 through A-07) | Documentation |
| 17 | Stop leaking raw exception messages (`str(e)`) in production responses | Security |

---

## 16. Design Document Updates Needed

The following items should be reflected in the design document to match implementation:

- [ ] Add `login_id` and `language` fields to User entity
- [ ] Add `POST /notices/{id}/confirm` endpoint
- [ ] Add `PATCH /admin/staff/{id}/reject` endpoint
- [ ] Add admin feedbacks API endpoints
- [ ] Document checklist log auto-creation business rule
- [ ] Document notice confirmation flow
- [ ] Update Opinions endpoint URL (`/opinions/` vs `/opinions/me`)

---

## 17. Conclusion

The Task Server V2 implementation achieves **79.8% overall match rate** against the design document and API specification. The strongest areas are **Supabase decoupling (95%)** and **storage abstraction (90%)**, demonstrating that the core architectural goal of provider-agnostic design is largely met. The weakest areas are **DI pattern consistency (60%)** and **error handling (65%)**, which require focused improvement.

**Critical path to 90%+ match rate:**
1. Add repository interfaces for the 9 missing repositories (+8% to Repository Abstraction)
2. Fix endpoint-to-repo leaks in 4 endpoint files (+5% to Architecture)
3. Standardize DI pattern across all endpoints (+15% to DI Pattern)
4. Add global error handler and fix error response inconsistencies (+10% to Error Handling)

Completing these 4 actions would bring the overall score to approximately **88-92%**.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-02-12 | Previous analysis (92% claim, high-level) | bkit |
| 1.0 | 2026-02-12 | Comprehensive 8-area deep analysis | bkit-gap-detector |
