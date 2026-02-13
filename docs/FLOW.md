# Staff 사용자 플로우 & API 매핑

> 프로토타입 기반 Staff(직원) 앱의 사용자 흐름과 필요 API 정리
>
> 작성일: 2026-02-12 | Base URL: `/api/v1`
>
> **역할 규칙:** 이 앱에서 가입하는 모든 계정은 `role: staff`. 관리자 기능 없음.

---

## 전체 흐름 요약

```
[로그인] ──→ [홈 대시보드] ──→ [내 업무] ──→ [업무 상세]
   ↑              │                │              ├── 상태 변경
[회원가입]         │                │              ├── 사진 인증
                  │                │              ├── 댓글 작성
                  │                │              └── 관리자 피드백 확인
                  │                │
                  │                └── [일일 체크리스트 (바텀시트)]
                  │                        └── 항목 체크 / 사진 인증
                  │
                  ├── [공지사항] ──→ [공지 상세]
                  │                    ├── 확인 완료
                  │                    └── 댓글 작성
                  │
                  ├── [의견 보내기]
                  ├── [알림]
                  └── [마이페이지] ──→ [로그아웃]
```

---

## 핵심 개념: 체크리스트 시스템

```
[관리자]                              [직원]
체크리스트 템플릿 생성                 본인 brand/group에 맞는
(브랜드/그룹/업무별)                   체크리스트가 task로 배정됨
        │                                     │
        └── 템플릿 기반으로 ──→ daily task 생성 (checklist_items 포함)
                                              │
                                     기존 API로 항목 체크
                                     PATCH /tasks/checklist/{item_id}
                                              │
                                     서버 내부에서 자동으로
                                     checklist_logs 테이블에 기록
                                     (누가, 언제, 어떤 항목, 사진)
                                              │
                              [관리자가 대시보드에서 로그 확인]
                                     준수율 확인 → 피드백 작성
                                              │
                              [직원이 업무 상세에서 피드백 확인]
```

- Staff는 **본인이 배정된 업무의 체크리스트만** 볼 수 있음
- 체크할 때 **기존 API 그대로 사용** (`PATCH /tasks/checklist/{item_id}`)
- **서버가 내부적으로** 체크 시점에 로그를 DB에 자동 저장 (프론트에서 별도 호출 불필요)
- 관리자가 로그를 보고 **피드백**(댓글+사진)을 남기면 직원이 확인

---

## 1. 회원가입 플로우

**경로:** `/signup` (4단계 위자드)

> 가입 시 role은 항상 `staff`. 관리자 승인 후 로그인 가능.
>
> **핵심:** 이메일 인증을 회원가입 **이전**에 진행. 계정이 없는 상태에서 이메일 유효성을 먼저 검증.

```
[Step 1: 약관 동의] → [Step 2: 이메일 인증] → [Step 3: 정보 입력] → [Step 4: 가입 완료]
                         │                                              │
                    send-verification                               signup
                    verify-email                              (이메일 인증 여부 확인)
```

### Step 1: 약관 동의
- UI에서 체크박스 3개 체크
- **API 호출 없음**

### Step 2: 이메일 본인 인증

| 사용자 액션 | API | Method | Body | Response |
|------------|-----|--------|------|----------|
| "인증번호 보내기" 탭 | `/auth/send-verification` | POST | `{ "email": "user@example.com" }` | `{ "message": "Verification code sent." }` |
| 인증번호 입력 후 "인증" 탭 | `/auth/verify-email` | POST | `{ "email": "user@example.com", "code": "123456" }` | `{ "message": "Email verified successfully." }` |

> **에러 처리:**
> - `send-verification` 400: `"Email is already registered."` → 이미 가입된 이메일
> - `send-verification` 429: `"Too many requests."` → 1시간 내 5회 초과
> - `verify-email` 400: `"Invalid or expired verification code."` → 코드 오류 또는 만료 (10분)

### Step 3: 정보 입력

- login_id, password, full_name, company_code, language 입력
- (login_id 중복 확인은 signup API에서 처리)

### Step 4: 가입 완료

| 사용자 액션 | API | Method | Body | Response |
|------------|-----|--------|------|----------|
| "가입" 버튼 탭 | `/auth/signup` | POST | 아래 참조 | `201 { message, access_token, refresh_token, user }` |

```json
{
  "email": "user@example.com",
  "login_id": "hong123",
  "password": "password123",
  "full_name": "홍길동",
  "company_code": "SCR",
  "language": "ko"
}
```

> **서버 동작:**
> 1. 이메일 인증 여부 확인 (`email_verification_codes` 테이블에서 `used=true` 레코드 존재 여부)
> 2. 미인증 시 400: `"Email is not verified. Please verify your email first."`
> 3. login_id/email 중복 확인
> 4. 계정 생성 (`email_verified: true`, `status: pending`)
> 5. access_token + refresh_token 발급
>
> role은 서버에서 강제로 `staff` 설정. status는 `pending` (관리자 승인 대기).

**가입 완료 안내:** "관리자가 승인한 이후 계정을 사용할 수 있어요." → 로그인 화면으로

---

## 2. 로그인 플로우

**경로:** `/login`

| 사용자 액션 | API | Method | Body | Response |
|------------|-----|--------|------|----------|
| ID/PW 입력 후 "로그인" | `/auth/login` | POST | `{ login_id, password }` | `{ access_token, refresh_token, user }` |

**Response user 객체:**
```json
{
  "id": "uuid",
  "login_id": "hong123",
  "full_name": "홍길동",
  "role": "staff",
  "branch": { "id": "uuid", "name": "강남점", "brand_id": "uuid" },
  "group": { "id": "uuid", "name": "1조" }
}
```

**에러 케이스:**
- 401: 아이디/비밀번호 불일치
- 403: 관리자 승인 대기 중 (`status: pending`)

---

## 3. 홈 대시보드 플로우

**경로:** `/`

### 화면 진입 시 데이터 로드

| 데이터 | API | Method | 설명 |
|--------|-----|--------|------|
| 사용자 정보 | `/auth/me` | GET | 프로필, 인사말, branch/group 정보 |
| 내 업무 목록 | `/tasks?assigned_to={user_id}` | GET | 업무 건수, 긴급 알림, 체크리스트 진행률 모두 이 데이터에서 계산 |
| 최근 공지 3건 | `/notices?limit=3` | GET | 하단 공지 미리보기 |
| 미확인 피드백 수 | `/feedbacks/unread-count` | GET | 알림 배지용 |

> 체크리스트 진행률: `/tasks` 응답의 daily 타입 업무들의 checklist 완료 비율을 프론트에서 계산

### 화면 내 사용자 액션

| 사용자 액션 | 동작 | API |
|------------|------|-----|
| 프로필 아이콘 탭 | `/mypage`로 이동 | - |
| 알림 벨 탭 | `/notifications`로 이동 | - |
| 긴급 알림 카드 탭 | `/tasks`로 이동 | - |
| Quick Menu "내 업무" | `/tasks`로 이동 | - |
| Quick Menu "출퇴근/스케줄/OJT" | "준비 중입니다" 스낵바 | 없음 |
| 의견 입력 후 전송 | 의견 전송 | `POST /opinions` |
| 공지 "더보기" | `/notices`로 이동 | - |
| 공지 카드 탭 | `/notices/{id}`로 이동 | - |

### 의견 전송

| API | Method | Body | Response |
|-----|--------|------|----------|
| `/opinions` | POST | `{ content }` | `201 { id, content, created_at }` |

---

## 4. 내 업무 플로우

**경로:** `/tasks`

### 화면 진입 시 데이터 로드

| 데이터 | API | Method | 설명 |
|--------|-----|--------|------|
| 내 업무 목록 | `/tasks?assigned_to={user_id}` | GET | daily + assigned 전부 (체크리스트 포함) |

> 프론트에서 `type` 필터링하여 일일/배정 분리 표시

### 화면 내 사용자 액션

| 사용자 액션 | 동작 | API |
|------------|------|-----|
| 일일 체크리스트 카드 탭 | 바텀시트 열기 | - |
| 필터 "#전체" / "#완료제거" | 프론트 필터링 | - |
| 업무 카드 탭 | `/tasks/{id}`로 이동 | - |

---

## 5. 일일 체크리스트 바텀시트 플로우

**위치:** 내 업무 화면에서 바텀시트로 열림

### 데이터

- 이미 로드된 daily 타입 업무의 `checklist` 필드 사용 (추가 API 호출 없음)

### 사용자 액션

| 사용자 액션 | API | Method | Body | Response |
|------------|-----|--------|------|----------|
| 일반 항목 체크/해제 | `/tasks/checklist/{item_id}` | PATCH | `{ is_completed: bool }` | `{ data }` |
| 사진 인증 항목 체크 | `/files/upload` | POST | `multipart (file)` | `{ file_url }` |
| ↳ 업로드 후 | `/tasks/checklist/{item_id}` | PATCH | `{ is_completed: true, verification_data: file_url }` | `{ data }` |

> **서버 내부 동작:** `PATCH /tasks/checklist/{item_id}` 호출 시 서버가 자동으로 `checklist_logs` 테이블에 기록 저장.
> 프론트에서는 기존과 동일하게 체크리스트 토글 API만 호출하면 됨.

**checklist_logs에 저장되는 데이터:**
```
- log_id, item_id, user_id
- is_completed (체크 여부)
- verification_data (사진 URL, 있을 경우)
- checked_at (체크 시각)
```

---

## 6. 업무 상세 플로우

**경로:** `/tasks/{id}`

### 화면 진입 시 데이터 로드

| 데이터 | API | Method | 설명 |
|--------|-----|--------|------|
| 업무 상세 | `/tasks/{id}` | GET | 업무 정보, 체크리스트, 댓글, 피드백 포함 |

```json
// GET /tasks/{id} Response
{
  "id": "uuid",
  "title": "매대 정리",
  "description": "...",
  "type": "assigned",
  "priority": "urgent",
  "status": "in_progress",
  "due_date": "...",
  "assigned_to": "user_uuid",
  "assigned_by": "admin_uuid",
  "proof_image": null,
  "created_at": "...",
  "checklist": [
    {
      "id": "uuid",
      "content": "조명 점검",
      "is_completed": false,
      "verification_type": "none",
      "verification_data": null
    }
  ],
  "comments": [...],
  "feedbacks": [
    {
      "id": "uuid",
      "author_name": "김매니저",
      "content": "이 부분 다시 확인해주세요",
      "photo_url": "https://...",
      "is_read": false,
      "created_at": "2026-02-12T14:00:00Z"
    }
  ]
}
```

### 6-1. 상태 변경

| 사용자 액션 | API | Method | Body |
|------------|-----|--------|------|
| "시작 전" / "진행 중" / "완료" 탭 | `/tasks/{id}/status` | PATCH | `{ status }` |
| 하단 "작업 시작" 버튼 | `/tasks/{id}/status` | PATCH | `{ status: "in_progress" }` |
| 하단 "작업 완료" 버튼 | `/tasks/{id}/status` | PATCH | `{ status: "done" }` |

### 6-2. 사진 인증

| 사용자 액션 | API | Method | Body |
|------------|-----|--------|------|
| 카메라 아이콘 탭 | `/files/upload` | POST | `multipart (file)` |
| "DONE" 버튼 탭 | `/tasks/{id}` | PATCH | `{ proof_image: file_url }` |

### 6-3. 댓글

| 사용자 액션 | API | Method | Body |
|------------|-----|--------|------|
| 댓글 전송 | `/tasks/{id}/comments` | POST | `{ content }` |

### 6-4. 피드백 확인 (관리자가 남긴 피드백 열람)

| 사용자 액션 | API | Method | 설명 |
|------------|-----|--------|------|
| 피드백 섹션 진입 시 | `/feedbacks/{id}/read` | PATCH | 읽음 처리 |

> 피드백은 업무 상세 조회 시 `feedbacks` 필드에 포함되어 옴.
> 직원은 피드백을 읽기만 가능. 작성/수정/삭제 불가.

---

## 7. 공지사항 플로우

**경로:** `/notices` → `/notices/{id}`

### 7-1. 공지 목록

| API | Method | 설명 |
|-----|--------|------|
| `/notices` | GET | 전체 목록 (최신순) |

### 7-2. 공지 상세

| API | Method | 설명 |
|-----|--------|------|
| `/notices/{id}` | GET | 상세 내용 + 댓글 |

### 사용자 액션

| 사용자 액션 | API | Method | Body |
|------------|-----|--------|------|
| "확인 완료" 버튼 탭 | `/notices/{id}/confirm` | POST | - |
| 댓글 전송 | `/notices/{id}/comments` | POST | `{ content }` |

---

## 8. 알림 플로우

**경로:** `/notifications`

| API | Method | 설명 |
|-----|--------|------|
| `/notifications` | GET | 알림 목록 (현재 빈 화면) |

---

## 9. 마이페이지 플로우

**경로:** `/mypage`

- 이미 로드된 사용자 정보 표시 (이름, 지점, 그룹)

| 사용자 액션 | API | Method |
|------------|-----|--------|
| "로그아웃" 탭 | `/auth/logout` | POST |

---

## Staff API 전체 목록

### 구현 완료 (기존 — 유지)

| # | Method | Endpoint | 설명 |
|---|--------|----------|------|
| 1 | POST | `/auth/login` | 로그인 |
| 2 | GET | `/auth/me` | 현재 사용자 조회 |
| 3 | GET | `/tasks` | 업무 목록 (필터: type, assigned_to) |
| 4 | GET | `/tasks/{id}` | 업무 상세 (체크리스트, 댓글, 피드백 포함) |
| 5 | POST | `/tasks` | 업무 생성 |
| 6 | PATCH | `/tasks/{id}` | 업무 수정 |
| 7 | DELETE | `/tasks/{id}` | 업무 삭제 |
| 8 | PATCH | `/tasks/{id}/status` | 업무 상태 변경 |
| 9 | PATCH | `/tasks/checklist/{item_id}` | 체크리스트 토글 (+ 서버 내부 로그 자동 저장) |
| 10 | GET | `/notices` | 공지 목록 |
| 11 | GET | `/notices/{id}` | 공지 상세 |

> **#9 변경점:** 기존 API 형태 유지. 서버 내부에서 `checklist_logs` 테이블에 로그 자동 기록 추가.
> Request에 `verification_data` (사진 URL) 필드 추가 지원.

### 신규 구현 필요

| # | Method | Endpoint | 설명 | Phase |
|---|--------|----------|------|-------|
| 12 | POST | `/auth/signup` | 회원가입 (role=staff 고정, 이메일 인증 필수) | 2 |
| 13 | POST | `/auth/send-verification` | 이메일 인증번호 발송 (가입 전) | 2 |
| 14 | POST | `/auth/verify-email` | 인증번호 확인 | 2 |
| 16 | POST | `/auth/logout` | 로그아웃 | 1 |
| 17 | POST | `/tasks/{id}/comments` | 업무 댓글 작성 | 1 |
| 18 | GET | `/feedbacks/unread-count` | 미확인 피드백 수 | 1 |
| 19 | PATCH | `/feedbacks/{id}/read` | 피드백 읽음 처리 | 1 |
| 20 | POST | `/notices/{id}/confirm` | 공지 확인 완료 | 3 |
| 21 | POST | `/notices/{id}/comments` | 공지 댓글 작성 | 3 |
| 22 | POST | `/opinions` | 의견 제출 | 1 |
| 23 | POST | `/files/upload` | 파일(사진) 업로드 | 1 |
| 24 | GET | `/notifications` | 알림 목록 | 4 |

### 기존 API 수정 필요

| # | Endpoint | 수정 내용 |
|---|----------|----------|
| 9 | `PATCH /tasks/checklist/{item_id}` | `verification_data` 필드 추가 + 서버 내부 로그 저장 로직 추가 |
| 4 | `GET /tasks/{id}` | Response에 `feedbacks` 필드 추가 |
