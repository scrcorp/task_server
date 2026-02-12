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

## Known Issues (as of 2026-02-12, v1.0 analysis)
- Overall match rate: 79.8%
- 9/11 repositories lack ABC interfaces
- 9/10 endpoint files bypass FastAPI Depends() for service injection
- Endpoints leak into repository layer (tasks.py, admin.py, notices.py, users.py)
- No global exception handler registered
- Missing schema fields: is_important, verification_type, profile_image, work_hours
- Enums split: TaskType in models/enums.py, UserRole in schemas/user.py
- Empty `app/crud/` directory is legacy leftover

## Analysis Methodology
- Always grep for `supabase` imports to verify decoupling
- Check all endpoint files for direct repo access (should go through service)
- Compare every endpoint URL + method + response fields against spec
- Verify all repositories extend IRepository or have custom ABC interface
- Check constructor injection vs module-level imports in repositories
