# Gap Detector Memory - task_server

## Project Architecture
- **Stack**: Python FastAPI + Supabase (PostgreSQL + Auth + Storage)
- **Pattern**: Repository Pattern with DI (API -> Service -> Repository)
- **DI Container**: `app/core/dependencies.py` (single point for swapping implementations)
- **Supabase client**: `app/core/supabase.py` (module-level singleton)

## Key File Locations
- Design doc: `docs/02-design/features/task-server-v2.design.md`
- Email verification design: `docs/02-design/features/email-verification.design.md`
- API spec: `docs/API_SPECIFICATION_V2.md`
- DB spec: `docs/DB_SPECIFICATION_V2.md`
- Analysis output: `docs/03-analysis/task-server-v2.analysis.md`
- Email verification analysis: `docs/03-analysis/email-verification.analysis.md`
- Base interfaces: `app/repositories/base.py`, `app/storage/base.py`
- Auth interface: `app/repositories/auth.py` (IAuthRepository - best example of proper DI)
- Email templates: `app/templates/` (verify_email.html, reset_password.html)

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

## Email Verification Feature (2026-02-13)
- Match rate: **100%** (97/97 design items)
- All 5 IAuthRepository verification code methods implemented
- FakeAuthRepository in tests/conftest.py covers all interface methods
- 26 total tests (13 designed + 13 bonus)
- No gaps found; 5 positive additions (SMTP guard, extra tests, template polish)

## Storage Improvement Feature (2026-02-13)
- Match rate: **100%** (66/66 design items)
- Config: MAX_FILE_SIZE_MB + ALLOWED_FILE_EXTENSIONS in Settings
- IStorageProvider interface: 3 async methods (upload, delete, get_url)
- SupabaseStorageProvider: mimetypes.guess_type(), async get_url()
- FileService: _get_content_type(), _get_allowed_extensions(), upload_file() with validation, delete_file(), get_presigned_url()
- Endpoints: POST /upload (413/400 error mapping), POST /presigned-url, DELETE /delete
- FakeStorageProvider in tests/conftest.py
- 14 total tests (13 designed + 1 bonus: test_upload_detects_mime_type_jpeg)
- No gaps found; 1 positive addition (extra MIME type test)
- Note: R-06 from v2.0 gaps (presigned URL response) may still apply to API spec

## Notification Channel Feature (2026-02-13)
- Match rate: **94.7%** (90/95 design items), effective **97.9%**
- Architecture: INotificationChannel ABC -> EmailNotificationChannel, NotificationDispatcher (Strategy)
- Services: NotificationService.notify(), CommentService._notify_assignees(), AdminService.create_feedback()
- DI: get_notification_dispatcher() in dependencies.py
- 2 gaps (same root cause): action_url template variable removed from channel.py + template
- 3 changed tests: substituted higher-value edge-case tests for lower-value ones
- 1 missing test: test_feedback_creates_notification_for_target (MEDIUM priority)
- 8 bonus items: FakeCommentRepo, FakeAssignmentRepo, should_fail param, extra test
- New modules: app/notifications/ (channel.py, dispatcher.py), app/templates/notification_email.html

## Analysis Methodology
- Always grep for `supabase` imports to verify decoupling
- Check all endpoint files for direct repo access (should go through service)
- Compare every endpoint URL + method + response fields against spec
- Verify all repositories extend IRepository or have custom ABC interface
- Check constructor injection vs module-level imports in repositories
- Verify `str(e)` leaks in endpoint error handlers
- Confirm Depends() usage in all endpoint function signatures
