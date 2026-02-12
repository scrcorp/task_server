# Task Server API (매장 직원 업무 관리 시스템)

이 프로젝트는 매장 직원 업무 관리 B2B SaaS 솔루션의 백엔드 API 서버입니다. FastAPI 프레임워크와 Supabase를 사용하여 구축되었습니다.

## 🚀 주요 기능
- **인증 (Auth)**: Supabase Auth 연동 로그인 및 사용자 정보 조회.
- **업무 관리 (Tasks)**: 데일리 루틴 및 할당된 업무의 생성, 조회, 수정, 삭제(CRUD).
- **상세 업무 처리**: 업무 상태 변경(진행 중/완료) 및 체크리스트 항목 토글.
- **공지사항 (Notices)**: 전체 공지사항 목록 및 상세 내용 조회.
- **배포 최적화**: Render와 같은 클라우드 환경에서 `$PORT` 환경 변수 대응.

## 🛠 기술 스택
- **Framework**: FastAPI (Python 3.12+)
- **Database/Auth**: Supabase (PostgreSQL)
- **Server**: Uvicorn
- **Documentation**: Swagger UI, ReDoc

## ⚙️ 설정 및 실행 방법

### 1. 가상환경 설정
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 Supabase 정보를 입력합니다.
```bash
cp .env.example .env
```
- `SUPABASE_URL`: 본인의 Supabase 프로젝트 URL
- `SUPABASE_KEY`: 본인의 Supabase Anon Key

### 4. 서버 실행
```bash
# 로컬 테스트
uvicorn app.main:app --reload

# 배포 환경 (Render 등)
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📖 API 문서 확인
서버 실행 후 아래 주소에서 대화형 API 문서를 확인할 수 있습니다.
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📁 폴더 구조
- `app/api/`: API 엔드포인트 정의
- `app/crud/`: 데이터베이스 조작 로직 (CRUD)
- `app/schemas/`: Pydantic 데이터 모델 (입출력 검증)
- `app/core/`: 설정 및 Supabase 클라이언트 초기화
- `docs/`: 프로젝트 PDCA 관리 문서
