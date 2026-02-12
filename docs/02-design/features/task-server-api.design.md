# Design: Task Server API

## Architecture Overview
- **Pattern**: Layered Architecture (API -> Service -> CRUD -> Model)
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (JWT Verification)

## Data Schema (Supabase / PostgreSQL)

### 1. Users (Supabase Auth 연동)
- `id`: uuid (PK)
- `email`: string
- `full_name`: string
- `role`: enum (admin, staff)
- `created_at`: timestamp

### 2. Tasks
- `id`: uuid (PK)
- `type`: enum (daily, assigned)
- `title`: string
- `description`: text
- `priority`: enum (urgent, normal, low)
- `status`: enum (todo, in_progress, done)
- `due_date`: timestamp
- `assigned_to`: uuid (FK -> Users.id)
- `created_at`: timestamp

### 3. Checklist Items (Daily Tasks 전용)
- `id`: uuid (PK)
- `task_id`: uuid (FK -> Tasks.id)
- `content`: string
- `is_completed`: boolean

### 4. Comments (Assigned Tasks 전용)
- `id`: uuid (PK)
- `task_id`: uuid (FK -> Tasks.id)
- `user_id`: uuid (FK -> Users.id)
- `content`: text
- `created_at`: timestamp

### 5. Notices
- `id`: uuid (PK)
- `title`: string
- `content`: text
- `created_at`: timestamp

## API Endpoints

### Auth
- `POST /auth/login`: Supabase Auth 연동 로그인 (Client-side에서 주로 처리하나 서버 검증 필요시 구현)
- `GET /auth/me`: 현재 로그인한 사용자 정보 조회

### Tasks
- `GET /tasks`: 업무 리스트 조회 (필터: type, status, assigned_to)
- `POST /tasks`: 업무 생성
- `GET /tasks/{task_id}`: 업무 상세 조회
- `PATCH /tasks/{task_id}`: 업무 상태 및 정보 수정
- `DELETE /tasks/{task_id}`: 업무 삭제

### Checklist
- `PATCH /checklist/{item_id}`: 체크리스트 항목 완료 여부 토글

### Notices
- `GET /notices`: 공지사항 리스트 조회
- `GET /notices/{notice_id}`: 공지사항 상세 조회

## Technical Decisions
1. **Supabase SDK**: Python `supabase` 클라이언트를 사용하여 직접 데이터베이스 및 인증 연동.
2. **Environment Variables**: `.env` 파일을 통해 `SUPABASE_URL`, `SUPABASE_KEY` 관리.
3. **Pydantic Schemas**: 요청/응답 데이터 검증을 위한 Pydantic 모델 정의.
4. **CORS**: Flutter Web 시연을 위해 모든 Origin 허용 또는 특정 도메인 설정.

## Success Metrics
- 모든 정의된 엔드포인트가 HTTP 200/201 반환.
- Supabase DB에 데이터가 정확히 적재 및 조회됨.
- JWT 토큰을 통한 보호된 라우트 접근 제어 확인.
