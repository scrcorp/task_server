# API 명세서 - 매장 직원 업무 관리 시스템

> 프로토타입 분석 기반, task_server에 필요한 전체 API 명세
>
> 작성일: 2026-02-12
> Base URL: `/api/v1`

---

## 목차

1. [현황 요약](#1-현황-요약)
2. [인증 (Auth)](#2-인증-auth)
3. [사용자 (Users)](#3-사용자-users)
4. [업무 (Tasks)](#4-업무-tasks)
5. [체크리스트 (Checklist)](#5-체크리스트-checklist)
6. [댓글 (Comments)](#6-댓글-comments)
7. [공지사항 (Notices)](#7-공지사항-notices)
8. [대시보드 (Dashboard)](#8-대시보드-dashboard)
9. [출퇴근 (Attendance)](#9-출퇴근-attendance)
10. [의견 (Opinions)](#10-의견-opinions)
11. [알림 (Notifications)](#11-알림-notifications)
12. [파일 업로드 (File Upload)](#12-파일-업로드-file-upload)
13. [DB 스키마 요약](#13-db-스키마-요약)

---

## 1. 현황 요약

### 구현 완료 (v0.1.0)

| 영역 | 엔드포인트 | 상태 |
|------|-----------|------|
| Auth | `POST /auth/login`, `GET /auth/me` | 완료 |
| Tasks | CRUD 5개 + 상태변경 + 체크리스트 토글 | 완료 |
| Notices | `GET /notices`, `GET /notices/{id}` | 완료 |

### 신규 구현 필요

| 영역 | 엔드포인트 수 | 우선순위 |
|------|-------------|---------|
| Auth 확장 (회원가입, 로그아웃) | 3개 | P0 - 필수 |
| 사용자 프로필 | 3개 | P0 - 필수 |
| 댓글 CRUD | 3개 | P0 - 필수 |
| 대시보드 통계 | 1개 | P1 - 높음 |
| 출퇴근 | 4개 | P1 - 높음 |
| 의견/피드백 | 2개 | P2 - 보통 |
| 알림 | 3개 | P2 - 보통 |
| 파일 업로드 | 2개 | P1 - 높음 |
| 공지사항 관리 (관리자) | 3개 | P2 - 보통 |

---

## 2. 인증 (Auth)

### 2.1 로그인 (구현 완료)

```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "v1.MQ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

### 2.2 회원가입 (신규)

```
POST /api/v1/auth/signup
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "홍길동",
  "role": "staff",
  "branch": "강남점"
}
```

**Response 201:**
```json
{
  "message": "회원가입이 완료되었습니다.",
  "user": {
    "id": "uuid",
    "email": "newuser@example.com",
    "full_name": "홍길동"
  }
}
```

**Error 400:** `이미 등록된 이메일입니다.`
**Error 422:** 유효성 검증 실패

### 2.3 로그아웃 (신규)

```
POST /api/v1/auth/logout
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "message": "로그아웃되었습니다."
}
```

### 2.4 토큰 갱신 (신규)

```
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "v1.MQ..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "v1.NEW..."
}
```

### 2.5 현재 사용자 조회 (구현 완료)

```
GET /api/v1/auth/me
```

**Headers:** `Authorization: Bearer <token>`

---

## 3. 사용자 (Users)

### 3.1 내 프로필 조회 (신규)

```
GET /api/v1/users/me/profile
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "박성민",
  "role": "manager",
  "branch": "강남점",
  "profile_image": "https://storage.supabase.co/...",
  "join_date": "2025-03-15T00:00:00Z"
}
```

### 3.2 프로필 수정 (신규)

```
PATCH /api/v1/users/me/profile
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "박성민",
  "profile_image": "https://storage.supabase.co/..."
}
```

**Response 200:** 수정된 프로필 객체

### 3.3 비밀번호 변경 (신규)

```
POST /api/v1/users/me/password
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "old_password",
  "new_password": "new_password123"
}
```

**Response 200:**
```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

---

## 4. 업무 (Tasks)

> 기존 구현 완료. 아래는 현재 엔드포인트 정리.

### 4.1 업무 목록 조회 (완료)

```
GET /api/v1/tasks?type={daily|assigned}&assigned_to={user_id}
```

**Response 200:**
```json
[
  {
    "id": "uuid",
    "type": "daily",
    "title": "개점 준비",
    "description": "매장 개점 전 준비사항",
    "priority": "normal",
    "status": "todo",
    "due_date": "2026-02-12T18:00:00Z",
    "assigned_to": "user_uuid",
    "created_at": "2026-02-12T09:00:00Z",
    "checklist": [...],
    "comments": [...]
  }
]
```

### 4.2 업무 상세 조회 (완료)

```
GET /api/v1/tasks/{task_id}
```

### 4.3 업무 생성 (완료)

```
POST /api/v1/tasks
```

**Request Body:**
```json
{
  "title": "신규 업무",
  "description": "업무 설명",
  "type": "assigned",
  "priority": "urgent",
  "status": "todo",
  "due_date": "2026-02-15T18:00:00Z",
  "assigned_to": "user_uuid"
}
```

### 4.4 업무 수정 (완료)

```
PATCH /api/v1/tasks/{task_id}
```

### 4.5 업무 삭제 (완료)

```
DELETE /api/v1/tasks/{task_id}
```

### 4.6 업무 상태 변경 (완료)

```
PATCH /api/v1/tasks/{task_id}/status?status={todo|in_progress|done}
```

---

## 5. 체크리스트 (Checklist)

### 5.1 체크리스트 항목 토글 (완료)

```
PATCH /api/v1/tasks/checklist/{item_id}?is_completed={true|false}
```

### 5.2 체크리스트 항목 추가 (신규)

```
POST /api/v1/tasks/{task_id}/checklist
```

**Request Body:**
```json
{
  "content": "새 체크리스트 항목",
  "verification_type": "photo"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "task_id": "task_uuid",
  "content": "새 체크리스트 항목",
  "is_completed": false,
  "verification_type": "photo"
}
```

### 5.3 체크리스트 항목 삭제 (신규)

```
DELETE /api/v1/tasks/checklist/{item_id}
```

---

## 6. 댓글 (Comments)

> 스키마는 존재하지만 CRUD 엔드포인트가 없음. 전부 신규 구현 필요.

### 6.1 댓글 목록 조회 (신규)

```
GET /api/v1/tasks/{task_id}/comments
```

**Response 200:**
```json
[
  {
    "id": "uuid",
    "task_id": "task_uuid",
    "user_id": "user_uuid",
    "user_name": "박성민",
    "content": "작업 진행 상황 공유합니다.",
    "is_manager": true,
    "created_at": "2026-02-12T10:30:00Z"
  }
]
```

### 6.2 댓글 작성 (신규)

```
POST /api/v1/tasks/{task_id}/comments
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content": "확인했습니다. 잘 진행해주세요."
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "task_id": "task_uuid",
  "user_id": "user_uuid",
  "user_name": "박성민",
  "content": "확인했습니다. 잘 진행해주세요.",
  "is_manager": true,
  "created_at": "2026-02-12T10:35:00Z"
}
```

### 6.3 댓글 삭제 (신규)

```
DELETE /api/v1/tasks/{task_id}/comments/{comment_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "message": "댓글이 삭제되었습니다."
}
```

---

## 7. 공지사항 (Notices)

### 7.1 공지사항 목록 조회 (완료)

```
GET /api/v1/notices
```

### 7.2 공지사항 상세 조회 (완료)

```
GET /api/v1/notices/{notice_id}
```

### 7.3 공지사항 작성 (신규 - 관리자)

```
POST /api/v1/notices
```

**Headers:** `Authorization: Bearer <token>` (role: manager/admin만 가능)

**Request Body:**
```json
{
  "title": "운영 시간 변경 안내",
  "content": "2월 15일부터 운영 시간이 변경됩니다...",
  "is_important": true
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "title": "운영 시간 변경 안내",
  "content": "...",
  "author": "박성민",
  "is_important": true,
  "created_at": "2026-02-12T09:00:00Z"
}
```

### 7.4 공지사항 수정 (신규 - 관리자)

```
PATCH /api/v1/notices/{notice_id}
```

### 7.5 공지사항 삭제 (신규 - 관리자)

```
DELETE /api/v1/notices/{notice_id}
```

---

## 8. 대시보드 (Dashboard)

### 8.1 홈 대시보드 요약 (신규)

```
GET /api/v1/dashboard/summary
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "user": {
    "full_name": "박성민",
    "role": "manager",
    "branch": "강남점"
  },
  "task_summary": {
    "total_tasks": 7,
    "pending_tasks": 4,
    "in_progress_tasks": 2,
    "completed_tasks": 1,
    "completion_rate": 14.3
  },
  "urgent_alerts": [
    {
      "task_id": "uuid",
      "title": "긴급 재고 확인",
      "priority": "urgent",
      "due_date": "2026-02-12T12:00:00Z"
    }
  ],
  "daily_progress": {
    "total_checklist_items": 12,
    "completed_items": 5,
    "completion_rate": 41.7
  },
  "recent_notices": [
    {
      "id": "uuid",
      "title": "운영 시간 변경",
      "is_important": true,
      "created_at": "2026-02-11T09:00:00Z"
    }
  ]
}
```

---

## 9. 출퇴근 (Attendance)

### 9.1 출근 기록 (신규)

```
POST /api/v1/attendance/clock-in
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "location": "강남점"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "user_id": "user_uuid",
  "clock_in": "2026-02-12T08:55:00Z",
  "clock_out": null,
  "location": "강남점",
  "status": "on_duty"
}
```

### 9.2 퇴근 기록 (신규)

```
POST /api/v1/attendance/clock-out
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "user_id": "user_uuid",
  "clock_in": "2026-02-12T08:55:00Z",
  "clock_out": "2026-02-12T18:05:00Z",
  "location": "강남점",
  "status": "off_duty",
  "work_hours": 9.17
}
```

### 9.3 오늘의 출퇴근 상태 (신규)

```
GET /api/v1/attendance/today
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "clock_in": "2026-02-12T08:55:00Z",
  "clock_out": null,
  "status": "on_duty"
}
```

**Response 200 (미출근):**
```json
{
  "status": "not_started"
}
```

### 9.4 출퇴근 이력 조회 (신규)

```
GET /api/v1/attendance/history?month=2026-02
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "month": "2026-02",
  "records": [
    {
      "date": "2026-02-11",
      "clock_in": "2026-02-11T08:50:00Z",
      "clock_out": "2026-02-11T18:00:00Z",
      "work_hours": 9.17,
      "status": "completed"
    }
  ],
  "summary": {
    "total_days": 8,
    "total_hours": 72.5,
    "late_count": 1
  }
}
```

---

## 10. 의견 (Opinions)

### 10.1 의견 제출 (신규)

```
POST /api/v1/opinions
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content": "매장 조명이 너무 어두워요. 교체 부탁드립니다."
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "user_id": "user_uuid",
  "content": "매장 조명이 너무 어두워요. 교체 부탁드립니다.",
  "created_at": "2026-02-12T14:00:00Z",
  "status": "submitted"
}
```

### 10.2 내 의견 목록 조회 (신규)

```
GET /api/v1/opinions/me
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
[
  {
    "id": "uuid",
    "content": "매장 조명이 너무 어두워요.",
    "created_at": "2026-02-12T14:00:00Z",
    "status": "submitted"
  }
]
```

---

## 11. 알림 (Notifications)

### 11.1 알림 목록 조회 (신규)

```
GET /api/v1/notifications?unread_only=true
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "unread_count": 3,
  "notifications": [
    {
      "id": "uuid",
      "type": "task_assigned",
      "title": "새 업무가 배정되었습니다",
      "message": "긴급 재고 확인 업무가 배정되었습니다.",
      "reference_id": "task_uuid",
      "reference_type": "task",
      "is_read": false,
      "created_at": "2026-02-12T10:00:00Z"
    }
  ]
}
```

**알림 타입 (`type`):**
| 값 | 설명 |
|----|------|
| `task_assigned` | 새 업무 배정 |
| `task_status_changed` | 업무 상태 변경 |
| `comment_added` | 새 댓글 |
| `notice_posted` | 새 공지사항 |
| `attendance_reminder` | 출퇴근 알림 |

### 11.2 알림 읽음 처리 (신규)

```
PATCH /api/v1/notifications/{notification_id}/read
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "message": "읽음 처리되었습니다."
}
```

### 11.3 전체 알림 읽음 처리 (신규)

```
PATCH /api/v1/notifications/read-all
```

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "message": "모든 알림이 읽음 처리되었습니다.",
  "updated_count": 3
}
```

---

## 12. 파일 업로드 (File Upload)

> 업무 사진 인증(Photo Verification)에 사용. Supabase Storage 활용.

### 12.1 이미지 업로드 (신규)

```
POST /api/v1/files/upload
```

**Headers:** `Authorization: Bearer <token>`
**Content-Type:** `multipart/form-data`

**Request:**
- `file`: 이미지 파일 (jpg, png, webp)
- `bucket`: `task-proofs` (기본값)

**Response 200:**
```json
{
  "file_url": "https://soptzocbzpkhtlmcsbdm.supabase.co/storage/v1/object/public/task-proofs/uuid.jpg",
  "file_name": "uuid.jpg",
  "file_size": 245678,
  "content_type": "image/jpeg"
}
```

### 12.2 Presigned URL 발급 (신규)

```
POST /api/v1/files/presigned-url
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "file_name": "proof_photo.jpg",
  "content_type": "image/jpeg",
  "bucket": "task-proofs"
}
```

**Response 200:**
```json
{
  "upload_url": "https://soptzocbzpkhtlmcsbdm.supabase.co/storage/v1/upload/sign/...",
  "file_url": "https://soptzocbzpkhtlmcsbdm.supabase.co/storage/v1/object/public/task-proofs/proof_photo.jpg",
  "expires_in": 3600
}
```

---

## 13. DB 스키마 요약

### 기존 테이블

```
tasks              checklist_items       comments           notices
├── id (PK)        ├── id (PK)           ├── id (PK)        ├── id (PK)
├── type           ├── task_id (FK)      ├── task_id (FK)   ├── title
├── title          ├── content           ├── user_id (FK)   ├── content
├── description    ├── is_completed      ├── content        ├── author
├── priority       └── created_at        ├── is_manager     ├── is_important
├── status                               └── created_at     └── created_at
├── due_date
├── assigned_to
└── created_at
```

### 신규 테이블 (추가 필요)

```
users          attendance             opinions            notifications
├── id (PK)            ├── id (PK)            ├── id (PK)         ├── id (PK)
├── user_id (FK)       ├── user_id (FK)       ├── user_id (FK)    ├── user_id (FK)
├── full_name          ├── clock_in           ├── content         ├── type
├── role               ├── clock_out          ├── status          ├── title
├── branch             ├── location           └── created_at      ├── message
├── profile_image      ├── status                                 ├── reference_id
├── join_date          └── created_at                             ├── reference_type
└── updated_at                                                    ├── is_read
                                                                  └── created_at
```

### checklist_items 컬럼 추가

```
+ verification_type    -- "none" | "photo"
+ verification_data    -- 인증 사진 URL
```

---

## 구현 우선순위 로드맵

### Phase 1 (P0 - 필수, 즉시)
1. `POST /auth/signup` - 회원가입
2. `POST /auth/logout` - 로그아웃
3. 사용자 프로필 CRUD (3개)
4. 댓글 CRUD (3개)

### Phase 2 (P1 - 높음)
5. `GET /dashboard/summary` - 대시보드
6. 파일 업로드 (2개)
7. 출퇴근 CRUD (4개)
8. `POST /auth/refresh` - 토큰 갱신

### Phase 3 (P2 - 보통)
9. 의견/피드백 (2개)
10. 알림 시스템 (3개)
11. 공지사항 관리자 CRUD (3개)

---

## 공통 사항

### 인증
- 모든 보호된 엔드포인트는 `Authorization: Bearer <token>` 헤더 필요
- Supabase Auth JWT 토큰 사용

### 에러 응답 형식
```json
{
  "detail": "에러 메시지"
}
```

| Status Code | 설명 |
|-------------|------|
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 422 | 유효성 검증 실패 |
| 500 | 서버 내부 오류 |

### Enum 값

| Enum | 값 |
|------|----|
| TaskType | `daily`, `assigned` |
| Priority | `urgent`, `normal`, `low` |
| TaskStatus | `todo`, `in_progress`, `done` |
| UserRole | `admin`, `manager`, `staff` |
| AttendanceStatus | `not_started`, `on_duty`, `off_duty`, `completed` |
| NotificationType | `task_assigned`, `task_status_changed`, `comment_added`, `notice_posted`, `attendance_reminder` |
| OpinionStatus | `submitted`, `reviewed`, `resolved` |
