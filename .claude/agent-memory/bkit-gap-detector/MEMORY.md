# Gap Detector Memory - task_server

## Project Architecture
- **Stack**: Python FastAPI + Supabase (PostgreSQL + Auth + Storage)
- **Pattern**: Repository Pattern with DI (API -> Service -> Repository)
- **DI Container**: `app/core/dependencies.py` (single point for swapping implementations)
- **Supabase client**: `app/core/supabase.py` (module-level singleton)

## Key File Locations
- Design doc: `docs/02-design/features/task-server-v2.design.md`
- API spec: `docs/01-plan/api-specification.md`
- Analysis output: `docs/03-analysis/task-server-v2.analysis.md`
- Base interfaces: `app/repositories/base.py`, `app/storage/base.py`
- Auth interface: `app/repositories/auth.py` (IAuthRepository - best example of proper DI)

## Current Status (v2.0 analysis, 2026-02-12)
- Overall match rate: **93.5%** (up from 79.8%)
- 11/11 repositories have ABC interfaces
- 10/10 endpoint files use FastAPI Depends()
- All endpoint-to-repo leaks fixed
- Global exception handler registered in main.py
- All schema fields added (is_important, verification_type, profile_image, work_hours, etc.)
- 6/8 enums in models/enums.py (UserRole/UserStatus still in schemas/user.py)
- Empty `app/crud/` removed

## Remaining Gaps (10 items, all LOW/MEDIUM)
- R-01: unread_only param accepted but not wired to service/repo
- R-02: Opinions URL /opinions/ vs spec /opinions/me
- R-03/R-04: Dashboard missing user object + field name diffs
- R-05: Attendance history summary missing total_hours, late_count
- R-06: Presigned URL response missing upload_url, file_url, expires_in
- R-07: NotificationType enum values differ from spec
- R-08: UserRole/UserStatus still in schemas/user.py
- R-09: OpinionStatus enum exists but not used in schema
- R-10: 10/11 repos use module-level supabase import (not constructor)

## Analysis Methodology
- Always grep for `supabase` imports to verify decoupling
- Check all endpoint files for direct repo access (should go through service)
- Compare every endpoint URL + method + response fields against spec
- Verify all repositories extend IRepository or have custom ABC interface
- Check constructor injection vs module-level imports in repositories
- Verify `str(e)` leaks in endpoint error handlers
- Confirm Depends() usage in all endpoint function signatures
