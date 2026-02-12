# Plan: Task Server API

## Feature Overview
- **Feature**: task-server-api
- **Level**: Dynamic
- **Priority**: High
- **Status**: Active

## Summary
매장 직원 업무 관리 시스템의 백엔드 API 서버 구축. FastAPI 프레임워크를 사용하며, 데이터베이스는 Supabase(PostgreSQL)를 활용합니다.

## Scope

### In Scope
1. **프로젝트 초기화** - FastAPI 폴더 구조 설정, 종속성 관리(requirements.txt), 환경 변수 설정.
2. **Supabase 연동** - Supabase Client 및 Database 연동 (SQLAlchemy 또는 직접 연동).
3. **인증(Auth)** - Supabase Auth 또는 JWT 기반 인증 구현.
4. **업무(Task) API** - 업무 생성, 조회, 수정, 삭제(CRUD), 상태 변경, 체크리스트 관리.
5. **공지사항(Notice) API** - 공지사항 조회 및 상세 정보 제공.
6. **데이터 스키마 정의** - User, Task, Checklist, Comment, Notice 테이블 설계.

### Out of Scope
- 복잡한 정산 시스템
- 실시간 채팅 서버 (우선 RESTful API로 구현)
- 고도의 이미지 처리 (Supabase Storage 활용으로 대체)

## Tech Stack
- **Framework**: FastAPI
- **Language**: Python 3.12+
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth
- **Server**: Uvicorn
- **ORM/Query**: SQLAlchemy 또는 Supabase Python SDK

## Implementation Priority
1. FastAPI 프로젝트 구조 설정 및 Supabase 연동 테스트
2. 데이터 모델링 및 Supabase Table 생성
3. 인증 API 연동
4. 업무(Task) 관련 CRUD API 개발
5. 공지사항(Notice) API 개발
6. API 문서(Swagger) 정리 및 배포 준비

## Success Criteria
- FastAPI 서버 로컬 구동 확인
- Supabase Database 연결 성공 및 CRUD 동작 확인
- Swagger UI(/docs)를 통한 API 테스트 통과
- `../docs/spec.md`에 정의된 데이터 구조와의 정렬
