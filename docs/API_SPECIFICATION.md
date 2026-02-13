# Task Server API 명세서

> **Base URL**: `/api/v1`
> **Version**: 0.1.0
> **인증 방식**: `Authorization: Bearer <access_token>`

---

## 목차

1. [Auth (인증)](#1-auth-인증)
2. [Tasks (업무)](#2-tasks-업무)
3. [Notices (공지사항)](#3-notices-공지사항)
4. [Admin (관리자)](#4-admin-관리자)
5. [Users (사용자)](#5-users-사용자)
6. [Dashboard (대시보드)](#6-dashboard-대시보드)
7. [Attendance (출퇴근)](#7-attendance-출퇴근)
8. [Opinions (건의사항)](#8-opinions-건의사항)
9. [Notifications (알림)](#9-notifications-알림)
10. [Files (파일)](#10-files-파일)
11. [Schema 정의](#schema-정의)
12. [Enum 정의](#enum-정의)
13. [에러 응답](#에러-응답)

---

## 1. Auth (인증)

### POST `/api/v1/auth/signup` - 회원가입

| 항목 | 내용 |
|------|------|
| 인증 | 불필요 |

**Request Body**
```json
{
  "email": "user@example.com",
  "login_id": "user123",
  "password": "password123",
  "full_name": "홍길동",
  "branch_id": "uuid (optional)",
  "language": "ko (default: ko)"
}
```

**Response** `201 Created`
```json
{
  "message": "회원가입이 완료되었습니다. 관리자 승인을 기다려주세요.",
  "user": { ... }
}
```

**Error** `400 Bad Request`
```json
{
  "detail": "회원가입에 실패했습니다: ..."
}
```

---

### POST `/api/v1/auth/login` - 로그인

| 항목 | 내용 |
|------|------|
| 인증 | 불필요 |

**Request Body**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "홍길동",
    "role": "staff"
  }
}
```

**Error** `401 Unauthorized`
```json
{
  "detail": "이메일 또는 비밀번호가 올바르지 않습니다."
}
```

---

### POST `/api/v1/auth/logout` - 로그아웃

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |

**Response** `200 OK`
```json
{
  "message": "로그아웃되었습니다."
}
```

---

### POST `/api/v1/auth/refresh` - 토큰 갱신

| 항목 | 내용 |
|------|------|
| 인증 | 불필요 |

**Request Body**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Error** `401 Unauthorized`
```json
{
  "detail": "토큰 갱신에 실패했습니다."
}
```

---

### GET `/api/v1/auth/me` - 현재 사용자 조회

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |

**Response** `200 OK` → [User](#user) 객체

---

## 2. Tasks (업무)

> 모든 엔드포인트 인증 필요

### GET `/api/v1/tasks/` - 업무 목록 조회

| Query Parameter | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `type` | TaskType | No | - | `daily` \| `assigned` |
| `assigned_to` | string | No | 현재 사용자 ID | 대상 사용자 ID |

**Response** `200 OK` → [Task](#task)[] 배열

---

### GET `/api/v1/tasks/{task_id}` - 업무 상세 조회

| Path Parameter | Type | Description |
|----------------|------|-------------|
| `task_id` | string | 업무 ID |

**Response** `200 OK` → [Task](#task) 객체 (checklist, comments 포함)

**Error** `404 Not Found`
```json
{
  "detail": "업무를 찾을 수 없습니다."
}
```

---

### POST `/api/v1/tasks/` - 업무 생성

**Request Body**
```json
{
  "title": "매장 청소",
  "description": "1층 매장 전체 청소 (optional)",
  "type": "daily | assigned",
  "priority": "urgent | normal | low (default: normal)",
  "status": "todo | in_progress | done (default: todo)",
  "due_date": "2026-02-14T09:00:00 (optional)",
  "assigned_to": "uuid (optional, default: 현재 사용자)"
}
```

**Response** `201 Created` → [Task](#task) 객체

---

### PATCH `/api/v1/tasks/{task_id}` - 업무 수정

**Request Body** (모든 필드 optional)
```json
{
  "title": "string",
  "description": "string",
  "status": "todo | in_progress | done",
  "priority": "urgent | normal | low"
}
```

**Response** `200 OK` → [Task](#task) 객체

---

### DELETE `/api/v1/tasks/{task_id}` - 업무 삭제

**Response** `200 OK`
```json
{
  "message": "업무가 삭제되었습니다."
}
```

---

### PATCH `/api/v1/tasks/{task_id}/status` - 업무 상태 변경

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `status` | TaskStatus | Yes | `todo` \| `in_progress` \| `done` |

**Response** `200 OK` → 업데이트된 Task 객체

---

### POST `/api/v1/tasks/{task_id}/checklist` - 체크리스트 항목 추가

**Request Body**
```json
{
  "content": "재고 확인",
  "verification_type": "none | photo | signature (default: none)"
}
```

**Response** `201 Created` → [ChecklistItem](#checklistitem) 객체

---

### PATCH `/api/v1/tasks/checklist/{item_id}` - 체크리스트 완료 토글

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `is_completed` | boolean | Yes | 완료 여부 |

**Response** `200 OK` → 업데이트된 ChecklistItem 객체

---

### DELETE `/api/v1/tasks/checklist/{item_id}` - 체크리스트 항목 삭제

**Response** `200 OK`
```json
{
  "message": "체크리스트 항목이 삭제되었습니다."
}
```

---

### GET `/api/v1/tasks/{task_id}/comments` - 댓글 목록 조회

**Response** `200 OK` → [Comment](#comment)[] 배열

---

### POST `/api/v1/tasks/{task_id}/comments` - 댓글 작성

**Request Body**
```json
{
  "content": "확인했습니다."
}
```

**Response** `201 Created` → [Comment](#comment) 객체

---

### DELETE `/api/v1/tasks/{task_id}/comments/{comment_id}` - 댓글 삭제

**Response** `200 OK`
```json
{
  "message": "댓글이 삭제되었습니다."
}
```

---

## 3. Notices (공지사항)

### GET `/api/v1/notices/` - 공지사항 목록 조회

| 항목 | 내용 |
|------|------|
| 인증 | 불필요 |

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `limit` | int | No | 조회 개수 제한 |

**Response** `200 OK` → [Notice](#notice)[] 배열

---

### GET `/api/v1/notices/{notice_id}` - 공지사항 상세 조회

| 항목 | 내용 |
|------|------|
| 인증 | 불필요 |

**Response** `200 OK` → [Notice](#notice) 객체

**Error** `404 Not Found`
```json
{
  "detail": "공지사항을 찾을 수 없습니다."
}
```

---

### POST `/api/v1/notices/{notice_id}/confirm` - 공지사항 확인

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |

**Response** `200 OK`
```json
{
  "message": "공지사항을 확인했습니다.",
  "data": { ... }
}
```

---

### POST `/api/v1/notices/` - 공지사항 작성

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |
| 권한 | ADMIN, MANAGER |

**Request Body**
```json
{
  "title": "2월 운영 안내",
  "content": "공지 내용입니다.",
  "is_important": false
}
```

**Response** `201 Created` → [Notice](#notice) 객체

---

### PATCH `/api/v1/notices/{notice_id}` - 공지사항 수정

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |
| 권한 | ADMIN, MANAGER |

**Request Body** (NoticeCreate와 동일)

**Response** `200 OK` → [Notice](#notice) 객체

---

### DELETE `/api/v1/notices/{notice_id}` - 공지사항 삭제

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |
| 권한 | ADMIN, MANAGER |

**Response** `200 OK`
```json
{
  "message": "공지사항이 삭제되었습니다."
}
```

---

## 4. Admin (관리자)

> 모든 엔드포인트: **ADMIN** 또는 **MANAGER** 역할 필요

### 직원 관리

#### GET `/api/v1/admin/staff/pending` - 승인 대기 직원 목록

**Response** `200 OK` → [User](#user)[] 배열

---

#### PATCH `/api/v1/admin/staff/{user_id}/approve` - 직원 승인

**Request Body**
```json
{
  "group_id": "uuid"
}
```

**Response** `200 OK` → [User](#user) 객체

---

#### PATCH `/api/v1/admin/staff/{user_id}/reject` - 직원 거절

**Response** `200 OK` → [User](#user) 객체

---

### 브랜드 관리

#### GET `/api/v1/admin/brands` - 브랜드 목록

**Response** `200 OK` → Brand[] 배열

---

#### POST `/api/v1/admin/brands` - 브랜드 생성

**Request Body**
```json
{
  "name": "브랜드명"
}
```

**Response** `201 Created` → Brand 객체

---

#### PATCH `/api/v1/admin/brands/{brand_id}` - 브랜드 수정

**Request Body**
```json
{
  "name": "수정된 브랜드명"
}
```

**Response** `200 OK` → Brand 객체

---

#### DELETE `/api/v1/admin/brands/{brand_id}` - 브랜드 삭제

**Response** `200 OK`
```json
{
  "message": "브랜드가 삭제되었습니다."
}
```

---

### 지점 관리

#### GET `/api/v1/admin/branches` - 지점 목록

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `brand_id` | string | No | 브랜드 ID로 필터링 |

**Response** `200 OK` → Branch[] 배열

---

#### POST `/api/v1/admin/branches` - 지점 생성

**Request Body**
```json
{
  "brand_id": "uuid",
  "name": "강남점",
  "address": "서울시 강남구 ... (optional)"
}
```

**Response** `201 Created` → Branch 객체

---

#### DELETE `/api/v1/admin/branches/{branch_id}` - 지점 삭제

**Response** `200 OK`
```json
{
  "message": "지점이 삭제되었습니다."
}
```

---

### 그룹 관리

#### GET `/api/v1/admin/groups` - 그룹 목록

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `branch_id` | string | No | 지점 ID로 필터링 |

**Response** `200 OK` → Group[] 배열

---

#### POST `/api/v1/admin/groups` - 그룹 생성

**Request Body**
```json
{
  "branch_id": "uuid",
  "name": "1조"
}
```

**Response** `201 Created` → Group 객체

---

#### DELETE `/api/v1/admin/groups/{group_id}` - 그룹 삭제

**Response** `200 OK`
```json
{
  "message": "그룹이 삭제되었습니다."
}
```

---

### 체크리스트 템플릿

#### GET `/api/v1/admin/checklist-templates` - 템플릿 목록

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `brand_id` | string | No | 브랜드 ID 필터 |
| `group_id` | string | No | 그룹 ID 필터 |

**Response** `200 OK` → ChecklistTemplate[] 배열

---

#### POST `/api/v1/admin/checklist-templates` - 템플릿 생성

**Request Body**
```json
{
  "name": "오픈 체크리스트",
  "brand_id": "uuid",
  "items": [
    { "content": "에어컨 켜기", "verification_type": "none" },
    { "content": "매장 사진 촬영", "verification_type": "photo" }
  ]
}
```

**Response** `201 Created` → ChecklistTemplate 객체

---

### 대시보드 (관리자)

#### GET `/api/v1/admin/dashboard/checklist-compliance` - 체크리스트 이행률

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `branch_id` | string | Yes | 지점 ID |
| `date` | string | Yes | 날짜 (YYYY-MM-DD) |

**Response** `200 OK`
```json
{
  "branch_id": "uuid",
  "date": "2026-02-13",
  "compliance_rate": 85.5,
  "details": [ ... ]
}
```

---

### 피드백

#### GET `/api/v1/admin/feedbacks` - 피드백 목록

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `target_user_id` | string | No | 대상 사용자 ID |
| `task_id` | string | No | 업무 ID |

**Response** `200 OK` → Feedback[] 배열

---

#### POST `/api/v1/admin/feedbacks` - 피드백 작성

**Request Body**
```json
{
  "target_user_id": "uuid",
  "task_id": "uuid",
  "content": "잘 수행했습니다.",
  "rating": 5
}
```

**Response** `201 Created` → Feedback 객체

---

## 5. Users (사용자)

> 모든 엔드포인트 인증 필요

### GET `/api/v1/users/me/profile` - 내 프로필 조회

**Response** `200 OK` → [User](#user) 객체

---

### PATCH `/api/v1/users/me/profile` - 내 프로필 수정

**Request Body** (모든 필드 optional)
```json
{
  "full_name": "홍길동",
  "profile_image": "https://...",
  "language": "ko",
  "group_id": "uuid",
  "branch_id": "uuid"
}
```

**Response** `200 OK` → [User](#user) 객체

---

### POST `/api/v1/users/me/password` - 비밀번호 변경

**Request Body**
```json
{
  "current_password": "현재 비밀번호",
  "new_password": "새 비밀번호"
}
```

**Response** `200 OK`
```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

**Error** `400 Bad Request`
```json
{
  "detail": "현재 비밀번호가 올바르지 않습니다."
}
```

---

## 6. Dashboard (대시보드)

### GET `/api/v1/dashboard/summary` - 대시보드 요약

| 항목 | 내용 |
|------|------|
| 인증 | Bearer Token |

**Response** `200 OK`
```json
{
  "task_summary": {
    "total_tasks": 10,
    "completed_tasks": 7,
    "in_progress_tasks": 2,
    "pending_tasks": 1,
    "completion_rate": 70.0
  },
  "attendance": {
    "status": "on_duty",
    "clock_in": "2026-02-13T09:00:00"
  },
  "recent_notices": [
    {
      "id": "uuid",
      "title": "공지 제목",
      "created_at": "2026-02-13T08:00:00"
    }
  ]
}
```

---

## 7. Attendance (출퇴근)

> 모든 엔드포인트 인증 필요

### GET `/api/v1/attendance/today` - 오늘 출퇴근 상태

**Response** `200 OK` → [AttendanceRecord](#attendancerecord) 객체 또는 `null`

---

### POST `/api/v1/attendance/clock-in` - 출근

**Request Body**
```json
{
  "location": "강남점 (optional)"
}
```

**Response** `201 Created` → [AttendanceRecord](#attendancerecord) 객체

**Error** `400 Bad Request`
```json
{
  "detail": "이미 출근 기록이 있습니다."
}
```

---

### POST `/api/v1/attendance/clock-out` - 퇴근

**Response** `200 OK` → [AttendanceRecord](#attendancerecord) 객체 (work_hours 포함)

**Error** `400 Bad Request`
```json
{
  "detail": "출근 기록이 없습니다."
}
```
```json
{
  "detail": "이미 퇴근 기록이 있습니다."
}
```

---

### GET `/api/v1/attendance/history` - 출퇴근 이력 조회

| Query Parameter | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `year` | int | No | 현재 연도 | 조회 연도 |
| `month` | int | No | 현재 월 | 조회 월 |

**Response** `200 OK`
```json
{
  "month": "2026-02",
  "records": [ /* AttendanceRecord[] */ ],
  "summary": {
    "total_days": 20,
    "completed": 18,
    "incomplete": 2
  }
}
```

---

## 8. Opinions (건의사항)

> 모든 엔드포인트 인증 필요

### POST `/api/v1/opinions/` - 건의사항 작성

**Request Body**
```json
{
  "content": "건의 내용입니다."
}
```

**Response** `201 Created` → [Opinion](#opinion) 객체

---

### GET `/api/v1/opinions/` - 내 건의사항 목록

**Response** `200 OK` → [Opinion](#opinion)[] 배열

---

## 9. Notifications (알림)

> 모든 엔드포인트 인증 필요

### GET `/api/v1/notifications/` - 알림 목록 조회

| Query Parameter | Type | Required | Description |
|-----------------|------|----------|-------------|
| `unread_only` | bool | No | `true`이면 읽지 않은 알림만 |

**Response** `200 OK`
```json
{
  "unread_count": 3,
  "notifications": [ /* Notification[] */ ]
}
```

---

### PATCH `/api/v1/notifications/{notification_id}/read` - 알림 읽음 처리

**Response** `200 OK`
```json
{
  "message": "알림이 읽음 처리되었습니다.",
  "data": { ... }
}
```

---

### PATCH `/api/v1/notifications/read-all` - 전체 알림 읽음 처리

**Response** `200 OK`
```json
{
  "message": "3개의 알림이 읽음 처리되었습니다.",
  "count": 3
}
```

---

## 10. Files (파일)

> 모든 엔드포인트 인증 필요

### POST `/api/v1/files/upload` - 파일 업로드

| 항목 | 내용 |
|------|------|
| Content-Type | `multipart/form-data` |

| Parameter | Type | In | Required | Default | Description |
|-----------|------|-----|----------|---------|-------------|
| `file` | UploadFile | body | Yes | - | 업로드할 파일 |
| `folder` | string | query | No | `uploads` | 저장 폴더 |

**Response** `200 OK`
```json
{
  "file_url": "https://storage.example.com/uploads/abc123.png",
  "file_name": "abc123.png",
  "file_size": 102400,
  "content_type": "application/png"
}
```

---

### POST `/api/v1/files/presigned-url` - Presigned URL 발급

**Request Body**
```json
{
  "file_path": "uploads/abc123.png"
}
```

**Response** `200 OK`
```json
{
  "url": "https://storage.example.com/signed/..."
}
```

---

## Schema 정의

### User

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 사용자 ID (UUID) |
| email | string | No | 이메일 |
| login_id | string | No | 로그인 ID |
| full_name | string | No | 이름 |
| role | UserRole | No | `staff` \| `manager` \| `admin` |
| status | UserStatus | No | `pending` \| `active` \| `inactive` |
| branch_id | string | Yes | 소속 지점 ID |
| group_id | string | Yes | 소속 그룹 ID |
| language | string | No | 언어 (default: `ko`) |
| profile_image | string | Yes | 프로필 이미지 URL |
| join_date | datetime | Yes | 입사일 |
| created_at | datetime | No | 생성일 |
| updated_at | datetime | No | 수정일 |

### Task

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 업무 ID (UUID) |
| title | string | No | 제목 |
| description | string | Yes | 설명 |
| type | TaskType | No | `daily` \| `assigned` |
| priority | TaskPriority | No | `urgent` \| `normal` \| `low` |
| status | TaskStatus | No | `todo` \| `in_progress` \| `done` |
| due_date | datetime | Yes | 마감일 |
| assigned_to | string | Yes | 담당자 ID |
| created_at | datetime | No | 생성일 |
| checklist | ChecklistItem[] | No | 체크리스트 |
| comments | Comment[] | No | 댓글 |

### ChecklistItem

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 항목 ID |
| content | string | No | 내용 |
| is_completed | boolean | No | 완료 여부 (default: false) |
| verification_type | string | No | `none` \| `photo` \| `signature` |
| verification_data | string | Yes | 인증 데이터 (사진 URL 등) |

### Comment

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 댓글 ID |
| user_id | string | No | 작성자 ID |
| user_name | string | Yes | 작성자 이름 |
| is_manager | boolean | No | 관리자 여부 (default: false) |
| content | string | No | 내용 |
| created_at | datetime | No | 작성일 |

### Notice

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 공지 ID |
| title | string | No | 제목 |
| content | string | No | 내용 |
| is_important | boolean | No | 중요 공지 여부 (default: false) |
| author_id | string | Yes | 작성자 ID |
| created_at | datetime | No | 작성일 |

### AttendanceRecord

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 출퇴근 기록 ID |
| user_id | string | No | 사용자 ID |
| clock_in | datetime | No | 출근 시간 |
| clock_out | datetime | Yes | 퇴근 시간 |
| location | string | Yes | 출근 위치 |
| status | AttendanceStatus | No | 출퇴근 상태 |
| work_hours | float | Yes | 근무 시간 (퇴근 시 계산) |

### Notification

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 알림 ID |
| user_id | string | No | 수신자 ID |
| type | NotificationType | No | 알림 유형 |
| title | string | No | 제목 |
| message | string | No | 내용 |
| reference_id | string | Yes | 참조 대상 ID |
| reference_type | string | Yes | 참조 유형 |
| is_read | boolean | No | 읽음 여부 (default: false) |
| created_at | datetime | No | 생성일 |

### Opinion

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | 건의 ID |
| user_id | string | No | 작성자 ID |
| content | string | No | 내용 |
| status | OpinionStatus | No | 처리 상태 |
| created_at | datetime | No | 작성일 |

---

## Enum 정의

### UserRole
| Value | Description |
|-------|-------------|
| `staff` | 일반 직원 |
| `manager` | 매니저 |
| `admin` | 관리자 |

### UserStatus
| Value | Description |
|-------|-------------|
| `pending` | 승인 대기 |
| `active` | 활성 |
| `inactive` | 비활성 |

### TaskType
| Value | Description |
|-------|-------------|
| `daily` | 일일 업무 |
| `assigned` | 배정 업무 |

### TaskStatus
| Value | Description |
|-------|-------------|
| `todo` | 미착수 |
| `in_progress` | 진행중 |
| `done` | 완료 |

### TaskPriority
| Value | Description |
|-------|-------------|
| `urgent` | 긴급 |
| `normal` | 보통 |
| `low` | 낮음 |

### AttendanceStatus
| Value | Description |
|-------|-------------|
| `not_started` | 미출근 |
| `on_duty` | 근무중 |
| `off_duty` | 퇴근 |
| `completed` | 완료 |

### NotificationType
| Value | Description |
|-------|-------------|
| `task_assigned` | 업무 배정 |
| `task_updated` | 업무 변경 |
| `notice` | 공지사항 |
| `feedback` | 피드백 |
| `system` | 시스템 |

### OpinionStatus
| Value | Description |
|-------|-------------|
| `submitted` | 제출됨 |
| `reviewed` | 검토중 |
| `resolved` | 해결됨 |

---

## 에러 응답

### 공통 에러 형식

**400 Bad Request** - 잘못된 요청
```json
{
  "detail": "에러 메시지"
}
```

**401 Unauthorized** - 인증 실패
```json
{
  "detail": "인증 정보가 유효하지 않습니다."
}
```

**403 Forbidden** - 권한 부족
```json
{
  "detail": "접근 권한이 없습니다."
}
```

**404 Not Found** - 리소스 없음
```json
{
  "detail": "리소스를 찾을 수 없습니다."
}
```

**500 Internal Server Error** - 서버 오류 (글로벌 핸들러)
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "서버 내부 오류가 발생했습니다."
  }
}
```
