# Admin 관리자 플로우 & API 매핑

> 관리자(manager/admin)용 기능 흐름과 API 명세
>
> 작성일: 2026-02-12 | Base URL: `/api/v1/admin`
>
> **참고:** Staff 앱에는 관리자 화면이 없음.
> 관리자 기능은 별도 웹 대시보드 또는 관리자 전용 앱에서 사용.

---

## 전체 흐름 요약

```
[관리자 로그인]
      │
      ├── [직원 관리] ──→ 가입 승인 / 그룹 배정
      │
      ├── [조직 관리] ──→ 브랜드 / 지점 / 그룹(조) 관리
      │
      ├── [체크리스트 관리] ──→ 템플릿 생성 (브랜드/그룹/업무별)
      │                          └── 항목 추가/수정/삭제
      │
      ├── [업무 관리] ──→ 업무 생성 / 배정 / 상태 확인
      │
      ├── [모니터링 대시보드] ──→ 체크리스트 준수율 확인
      │                           ├── 직원별 / 지점별 / 그룹별
      │                           └── 미준수 항목 → 피드백 작성
      │
      ├── [공지사항 관리] ──→ CRUD + 확인 현황
      │
      └── [의견 관리] ──→ 직원 의견 조회 / 상태 변경
```

---

## 1. 관리자 인증

> 관리자 계정은 앱 가입이 아닌 시스템에서 직접 생성.
> Staff 앱의 `/auth/login`을 공유하되, role 기반으로 접근 권한 분리.

| API | Method | 설명 |
|-----|--------|------|
| `/auth/login` | POST | 공용 로그인 (response에 role 포함) |
| `/auth/me` | GET | 현재 사용자 정보 (role: manager/admin) |

> `/api/v1/admin/*` 엔드포인트는 role이 `manager` 또는 `admin`인 경우만 접근 가능.

---

## 2. 직원 관리

### 2-1. 가입 승인 대기 목록 조회

```
GET /api/v1/admin/staff/pending
```

Staff가 앱에서 가입하면 `status: pending`으로 생성됨.
관리자가 확인 후 승인/거절.

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "hong@example.com",
    "login_id": "hong123",
    "full_name": "홍길동",
    "branch_id": "uuid",
    "branch_name": "강남점",
    "status": "pending",
    "created_at": "2026-02-12T10:00:00Z"
  }
]
```

### 2-2. 가입 승인/거절

```
PATCH /api/v1/admin/staff/{user_id}/approve
```

**Request Body:**
```json
{
  "approved": true,          // false면 거절
  "group_id": "uuid"         // 승인 시 그룹(조) 배정
}
```

**Response:**
```json
{
  "message": "승인되었습니다.",
  "user": { "id": "uuid", "status": "active", "group": { "id": "uuid", "name": "1조" } }
}
```

### 2-3. 직원 목록 조회

```
GET /api/v1/admin/staff?branch_id={uuid}&group_id={uuid}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "full_name": "홍길동",
    "login_id": "hong123",
    "role": "staff",
    "status": "active",
    "branch": { "id": "uuid", "name": "강남점" },
    "group": { "id": "uuid", "name": "1조" },
    "join_date": "2026-02-01"
  }
]
```

### 2-4. 직원 그룹 변경

```
PATCH /api/v1/admin/staff/{user_id}/group
```

**Request Body:**
```json
{
  "group_id": "uuid"
}
```

### 2-5. 직원 비활성화

```
PATCH /api/v1/admin/staff/{user_id}/deactivate
```

---

## 3. 조직 관리 (브랜드 / 지점 / 그룹)

### 3-1. 브랜드

| API | Method | Body | 설명 |
|-----|--------|------|------|
| `/admin/brands` | GET | - | 브랜드 목록 |
| `/admin/brands` | POST | `{ name }` | 브랜드 생성 |
| `/admin/brands/{id}` | PATCH | `{ name }` | 브랜드 수정 |
| `/admin/brands/{id}` | DELETE | - | 브랜드 삭제 |

### 3-2. 지점 (브랜드 하위)

| API | Method | Body | 설명 |
|-----|--------|------|------|
| `/admin/branches?brand_id={uuid}` | GET | - | 지점 목록 |
| `/admin/branches` | POST | `{ brand_id, name, address }` | 지점 생성 |
| `/admin/branches/{id}` | PATCH | `{ name, address }` | 지점 수정 |
| `/admin/branches/{id}` | DELETE | - | 지점 삭제 |

### 3-3. 그룹/조 (지점 하위)

| API | Method | Body | 설명 |
|-----|--------|------|------|
| `/admin/groups?branch_id={uuid}` | GET | - | 그룹 목록 |
| `/admin/groups` | POST | `{ branch_id, name }` | 그룹 생성 |
| `/admin/groups/{id}` | PATCH | `{ name }` | 그룹 수정 |
| `/admin/groups/{id}` | DELETE | - | 그룹 삭제 |

**조직 구조:**
```
Brand (브랜드)
└── Branch (지점: 강남점, 홍대점...)
    └── Group (조: 1조, 2조...)
        └── Staff (직원)
```

---

## 4. 체크리스트 템플릿 관리

### 4-1. 템플릿 목록 조회

```
GET /api/v1/admin/checklist-templates?brand_id={uuid}&group_id={uuid}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "개점 준비",
    "brand": { "id": "uuid", "name": "A브랜드" },
    "group": null,                    // null이면 해당 브랜드 전체 적용
    "item_count": 5,
    "is_active": true,
    "created_by": "김매니저",
    "created_at": "2026-01-15"
  }
]
```

### 4-2. 템플릿 생성

```
POST /api/v1/admin/checklist-templates
```

**Request Body:**
```json
{
  "title": "개점 준비",
  "description": "매장 오픈 전 필수 점검 사항",
  "brand_id": "uuid",
  "group_id": null,                   // null이면 브랜드 전체
  "items": [
    { "content": "조명 점검", "verification_type": "none", "sort_order": 1 },
    { "content": "청소 상태 확인", "verification_type": "photo", "sort_order": 2 },
    { "content": "POS 부팅 확인", "verification_type": "none", "sort_order": 3 }
  ]
}
```

### 4-3. 템플릿 수정

```
PATCH /api/v1/admin/checklist-templates/{template_id}
```

**Request Body:**
```json
{
  "title": "개점 준비 (수정)",
  "is_active": true
}
```

### 4-4. 템플릿 삭제

```
DELETE /api/v1/admin/checklist-templates/{template_id}
```

### 4-5. 템플릿 항목 추가

```
POST /api/v1/admin/checklist-templates/{template_id}/items
```

**Request Body:**
```json
{
  "content": "신규 점검 항목",
  "verification_type": "photo",
  "sort_order": 4
}
```

### 4-6. 템플릿 항목 수정

```
PATCH /api/v1/admin/checklist-templates/items/{item_id}
```

### 4-7. 템플릿 항목 삭제

```
DELETE /api/v1/admin/checklist-templates/items/{item_id}
```

---

## 5. 업무 관리

### 5-1. 업무 생성 및 배정

> 기존 `POST /tasks`를 관리자가 사용. 특정 직원에게 업무 배정.

```
POST /api/v1/admin/tasks
```

**Request Body:**
```json
{
  "title": "매대 정리",
  "description": "2번 매대 상품 재배치",
  "type": "assigned",
  "priority": "urgent",
  "assigned_to": "staff_user_id",
  "due_date": "2026-02-13T18:00:00Z",
  "labels": ["매대", "정리"]
}
```

### 5-2. 업무 목록 조회 (전체)

```
GET /api/v1/admin/tasks?branch_id={uuid}&status={status}&assigned_to={user_id}
```

> Staff용 API와 달리 전체 직원의 업무를 조회 가능.

### 5-3. 업무 수정

```
PATCH /api/v1/admin/tasks/{task_id}
```

### 5-4. 업무 삭제

```
DELETE /api/v1/admin/tasks/{task_id}
```

---

## 6. 모니터링 대시보드

### 6-1. 체크리스트 준수율 요약

```
GET /api/v1/admin/dashboard/checklist-compliance?branch_id={uuid}&date={2026-02-12}
```

**Response:**
```json
{
  "date": "2026-02-12",
  "branch": { "id": "uuid", "name": "강남점" },
  "overall_rate": 78.5,
  "by_group": [
    { "group": "1조", "rate": 92.0, "total": 12, "completed": 11 },
    { "group": "2조", "rate": 65.0, "total": 12, "completed": 8 }
  ],
  "by_template": [
    { "template": "개점 준비", "rate": 100.0 },
    { "template": "중간 점검", "rate": 60.0 },
    { "template": "마감 정리", "rate": 75.0 }
  ]
}
```

### 6-2. 직원별 체크리스트 로그 조회

```
GET /api/v1/admin/dashboard/checklist-logs?user_id={uuid}&date_from={date}&date_to={date}
```

**Response:**
```json
{
  "user": { "id": "uuid", "full_name": "홍길동", "group": "1조" },
  "period": { "from": "2026-02-01", "to": "2026-02-12" },
  "daily_logs": [
    {
      "date": "2026-02-12",
      "total_items": 12,
      "completed_items": 11,
      "rate": 91.7,
      "missed_items": [
        { "item_id": "uuid", "content": "마감 청소", "template": "마감 정리" }
      ]
    }
  ]
}
```

### 6-3. 특정 로그 상세 조회

```
GET /api/v1/admin/dashboard/checklist-logs/{log_id}
```

**Response:**
```json
{
  "id": "uuid",
  "item": { "content": "청소 상태 확인", "verification_type": "photo" },
  "template": { "title": "개점 준비" },
  "user": { "full_name": "홍길동" },
  "is_completed": true,
  "verification_data": "https://storage.../proof.jpg",
  "checked_at": "2026-02-12T09:15:00Z"
}
```

### 6-4. 업무 완료율 요약

```
GET /api/v1/admin/dashboard/task-completion?branch_id={uuid}&date={2026-02-12}
```

**Response:**
```json
{
  "date": "2026-02-12",
  "total_tasks": 15,
  "completed": 8,
  "in_progress": 4,
  "todo": 3,
  "completion_rate": 53.3,
  "overdue": 2,
  "by_staff": [
    { "user": "홍길동", "total": 5, "completed": 3, "rate": 60.0 }
  ]
}
```

---

## 7. 피드백

### 7-1. 피드백 작성

관리자가 특정 업무 또는 체크리스트 로그에 대해 피드백 작성.

```
POST /api/v1/admin/feedbacks
```

**Request Body:**
```json
{
  "target_user_id": "staff_uuid",
  "task_id": "uuid",                    // 업무에 대한 피드백 (택1)
  "checklist_log_id": "uuid",           // 체크리스트 로그에 대한 피드백 (택1)
  "content": "청소 상태가 미흡합니다. 사진을 확인해주세요.",
  "photo_url": "https://..."            // 선택. 사진 첨부 시
}
```

> `task_id`와 `checklist_log_id` 중 하나만 필수.

### 7-2. 피드백 목록 조회

```
GET /api/v1/admin/feedbacks?target_user_id={uuid}&task_id={uuid}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "target_user": { "id": "uuid", "full_name": "홍길동" },
    "task": { "id": "uuid", "title": "매대 정리" },
    "checklist_log": null,
    "content": "청소 상태가 미흡합니다.",
    "photo_url": "https://...",
    "is_read": false,
    "created_at": "2026-02-12T14:00:00Z"
  }
]
```

### 7-3. 피드백 수정

```
PATCH /api/v1/admin/feedbacks/{feedback_id}
```

### 7-4. 피드백 삭제

```
DELETE /api/v1/admin/feedbacks/{feedback_id}
```

---

## 8. 공지사항 관리

| API | Method | Body | 설명 |
|-----|--------|------|------|
| `/admin/notices` | GET | - | 공지 목록 + 확인 현황 |
| `/admin/notices` | POST | `{ title, content, is_important }` | 공지 작성 |
| `/admin/notices/{id}` | PATCH | `{ title, content, is_important }` | 공지 수정 |
| `/admin/notices/{id}` | DELETE | - | 공지 삭제 |
| `/admin/notices/{id}/confirmations` | GET | - | 공지 확인한 직원 목록 |

### 공지 확인 현황

```
GET /api/v1/admin/notices/{id}/confirmations
```

**Response:**
```json
{
  "notice_id": "uuid",
  "title": "운영 시간 변경 안내",
  "total_staff": 12,
  "confirmed_count": 8,
  "unconfirmed_count": 4,
  "confirmations": [
    { "user": "홍길동", "confirmed_at": "2026-02-12T10:30:00Z" }
  ],
  "unconfirmed": [
    { "user": "김직원", "group": "2조" }
  ]
}
```

---

## 9. 의견 관리

| API | Method | Body | 설명 |
|-----|--------|------|------|
| `/admin/opinions` | GET | `?status={submitted/reviewed/resolved}` | 의견 목록 |
| `/admin/opinions/{id}` | GET | - | 의견 상세 |
| `/admin/opinions/{id}/status` | PATCH | `{ status }` | 상태 변경 |

**OpinionStatus:** `submitted` → `reviewed` → `resolved`

---

## Admin API 전체 목록

| # | Method | Endpoint | 설명 |
|---|--------|----------|------|
| **인증** | | | |
| 1 | POST | `/auth/login` | 공용 로그인 |
| 2 | GET | `/auth/me` | 현재 사용자 |
| **직원 관리** | | | |
| 3 | GET | `/admin/staff/pending` | 가입 승인 대기 목록 |
| 4 | PATCH | `/admin/staff/{id}/approve` | 가입 승인/거절 |
| 5 | GET | `/admin/staff` | 직원 목록 |
| 6 | PATCH | `/admin/staff/{id}/group` | 직원 그룹 변경 |
| 7 | PATCH | `/admin/staff/{id}/deactivate` | 직원 비활성화 |
| **조직 관리** | | | |
| 8 | GET | `/admin/brands` | 브랜드 목록 |
| 9 | POST | `/admin/brands` | 브랜드 생성 |
| 10 | PATCH | `/admin/brands/{id}` | 브랜드 수정 |
| 11 | DELETE | `/admin/brands/{id}` | 브랜드 삭제 |
| 12 | GET | `/admin/branches` | 지점 목록 |
| 13 | POST | `/admin/branches` | 지점 생성 |
| 14 | PATCH | `/admin/branches/{id}` | 지점 수정 |
| 15 | DELETE | `/admin/branches/{id}` | 지점 삭제 |
| 16 | GET | `/admin/groups` | 그룹 목록 |
| 17 | POST | `/admin/groups` | 그룹 생성 |
| 18 | PATCH | `/admin/groups/{id}` | 그룹 수정 |
| 19 | DELETE | `/admin/groups/{id}` | 그룹 삭제 |
| **체크리스트 템플릿** | | | |
| 20 | GET | `/admin/checklist-templates` | 템플릿 목록 |
| 21 | POST | `/admin/checklist-templates` | 템플릿 생성 (항목 포함) |
| 22 | PATCH | `/admin/checklist-templates/{id}` | 템플릿 수정 |
| 23 | DELETE | `/admin/checklist-templates/{id}` | 템플릿 삭제 |
| 24 | POST | `/admin/checklist-templates/{id}/items` | 항목 추가 |
| 25 | PATCH | `/admin/checklist-templates/items/{id}` | 항목 수정 |
| 26 | DELETE | `/admin/checklist-templates/items/{id}` | 항목 삭제 |
| **업무 관리** | | | |
| 27 | GET | `/admin/tasks` | 전체 업무 목록 |
| 28 | POST | `/admin/tasks` | 업무 생성/배정 |
| 29 | PATCH | `/admin/tasks/{id}` | 업무 수정 |
| 30 | DELETE | `/admin/tasks/{id}` | 업무 삭제 |
| **대시보드** | | | |
| 31 | GET | `/admin/dashboard/checklist-compliance` | 체크리스트 준수율 |
| 32 | GET | `/admin/dashboard/checklist-logs` | 직원별 로그 조회 |
| 33 | GET | `/admin/dashboard/checklist-logs/{id}` | 로그 상세 |
| 34 | GET | `/admin/dashboard/task-completion` | 업무 완료율 |
| **피드백** | | | |
| 35 | POST | `/admin/feedbacks` | 피드백 작성 |
| 36 | GET | `/admin/feedbacks` | 피드백 목록 |
| 37 | PATCH | `/admin/feedbacks/{id}` | 피드백 수정 |
| 38 | DELETE | `/admin/feedbacks/{id}` | 피드백 삭제 |
| **공지사항 관리** | | | |
| 39 | GET | `/admin/notices` | 공지 목록 + 확인 현황 |
| 40 | POST | `/admin/notices` | 공지 작성 |
| 41 | PATCH | `/admin/notices/{id}` | 공지 수정 |
| 42 | DELETE | `/admin/notices/{id}` | 공지 삭제 |
| 43 | GET | `/admin/notices/{id}/confirmations` | 확인 현황 |
| **의견 관리** | | | |
| 44 | GET | `/admin/opinions` | 의견 목록 |
| 45 | GET | `/admin/opinions/{id}` | 의견 상세 |
| 46 | PATCH | `/admin/opinions/{id}/status` | 의견 상태 변경 |

**합계: 46개 API** (공용 인증 2개 + 관리자 전용 44개)

---

## DB 스키마 (신규 테이블)

```
brands                 branches               groups
├── id (PK)            ├── id (PK)            ├── id (PK)
├── name               ├── brand_id (FK)      ├── branch_id (FK)
├── created_at         ├── name               ├── name
                       ├── address            └── created_at
                       └── created_at

users                     checklist_templates
├── id (PK)                       ├── id (PK)
├── user_id (FK → auth.users)     ├── title
├── full_name                     ├── description
├── login_id (unique)             ├── brand_id (FK)
├── role (staff/manager/admin)    ├── group_id (FK, nullable)
├── status (pending/active/       ├── is_active
│          inactive)              ├── created_by (FK)
├── branch_id (FK)                └── created_at
├── group_id (FK, nullable)
├── language                      checklist_template_items
├── join_date                     ├── id (PK)
└── updated_at                    ├── template_id (FK)
                                  ├── content
                                  ├── verification_type (none/photo)
                                  ├── sort_order
                                  └── created_at
```

### 기존 테이블 수정

```
checklist_items (기존 — 컬럼 추가)
├── id (PK)
├── task_id (FK → tasks)
├── content
├── is_completed
├── verification_type (none/photo)      ← 추가
├── verification_data (URL, nullable)   ← 추가
├── template_item_id (FK, nullable)     ← 추가: 어떤 템플릿 항목에서 생성되었는지 추적
└── created_at
```

> 관리자가 템플릿 기반으로 daily task를 생성하면, template_items가 checklist_items로 복사됨.
> `template_item_id`를 통해 원본 템플릿 항목 추적 가능.

### 신규 테이블

```
checklist_logs (체크 시 서버가 자동 생성)
├── id (PK)
├── item_id (FK → checklist_items)      ← task 소속 항목 참조
├── user_id (FK)
├── is_completed
├── verification_data (URL, nullable)
├── checked_at
└── created_at

feedbacks                         notice_confirmations
├── id (PK)                       ├── id (PK)
├── author_id (FK → manager)      ├── notice_id (FK)
├── target_user_id (FK → staff)   ├── user_id (FK)
├── task_id (FK, nullable)        └── confirmed_at
├── checklist_log_id (FK, nullable)
├── content                       opinions
├── photo_url                     ├── id (PK)
├── is_read                       ├── user_id (FK)
└── created_at                    ├── content
                                  ├── status (submitted/reviewed/resolved)
                                  └── created_at
```

### 데이터 흐름

```
[관리자]                                      [직원]
checklist_templates                           tasks (type: daily)
├── template_items ──── task 생성 시 복사 ──→ ├── checklist_items
                                              │    └── template_item_id로 원본 추적
                                              │
                                              └── PATCH /tasks/checklist/{item_id}
                                                   └── 서버 내부: checklist_logs 자동 생성

[관리자 대시보드]
checklist_logs ← JOIN → checklist_items ← JOIN → template_items ← JOIN → templates
→ 준수율 계산, 직원별/그룹별/템플릿별 집계
```

---

## 구현 우선순위

### Phase 1: 조직/직원 기반 구축
- 브랜드/지점/그룹 CRUD (12개)
- 직원 관리 — 승인, 목록, 그룹 배정 (5개)

### Phase 2: 체크리스트 시스템
- 템플릿 CRUD + 항목 관리 (7개)
- 대시보드 — 준수율, 로그 조회 (4개)

### Phase 3: 피드백 & 소통
- 피드백 CRUD (4개)
- 공지사항 관리 + 확인 현황 (5개)
- 의견 관리 (3개)

### Phase 4: 업무 관리
- 업무 CRUD (4개) — 기존 Staff API 활용 가능
