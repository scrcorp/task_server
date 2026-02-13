# PDCA Plan: Storage Improvement

> **Feature**: storage
> **Created**: 2026-02-13
> **Status**: Plan
> **Priority**: High

---

## 1. Background & Objective

Storage(file upload/download) functionality exists in the codebase but has critical bugs, missing validations, and incomplete API coverage. This plan addresses all storage-related issues found during the analysis phase.

---

## 2. AS-IS vs TO-BE

### AS-IS (Current Problems)

| # | Issue | Severity | File |
|---|-------|----------|------|
| 1 | Content-Type hardcoded as `image/jpeg` for ALL file uploads | Critical | `app/storage/supabase.py:15` |
| 2 | `get_url()` declared as sync `def` but interface declares `async def` | Critical | `app/storage/supabase.py:25` vs `base.py:16` |
| 3 | MIME type incorrectly generated as `application/{ext}` (e.g., `application/png`) | Major | `app/services/file_service.py:18` |
| 4 | No file deletion API endpoint (only upload & presigned-url exist) | Major | `app/api/endpoints/files.py` |
| 5 | No file size limit — unlimited upload allowed | Major | `app/api/endpoints/files.py` |
| 6 | No file type validation — any file type accepted (security risk) | Major | `app/api/endpoints/files.py` |
| 7 | No delete integration in comment attachments | Medium | `app/services/comment_service.py` |

### TO-BE (Target State)

| # | Target | Description |
|---|--------|-------------|
| 1 | Dynamic Content-Type detection | Use `mimetypes` module to detect correct MIME type from file extension |
| 2 | Fix async/sync interface consistency | Make `get_url()` async in implementation to match interface |
| 3 | Correct MIME type in upload response | Use `mimetypes.guess_type()` for accurate MIME type |
| 4 | Add `DELETE /files/{file_path}` endpoint | Expose existing `IStorageProvider.delete()` via API |
| 5 | Add file size limit (10MB default) | Validate `len(content)` before upload, configurable via `Settings` |
| 6 | Add allowed file types whitelist | Validate extension against configurable whitelist |
| 7 | Add file deletion in FileService | `delete_file()` method to wire storage.delete() |

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Detect and apply correct Content-Type from file extension on upload | Must |
| FR-02 | Fix async interface mismatch (`get_url` must be async) | Must |
| FR-03 | Return correct MIME type in upload response (`image/png` not `application/png`) | Must |
| FR-04 | Add `DELETE /files` endpoint with file_path parameter | Must |
| FR-05 | Add `delete_file()` method to FileService | Must |
| FR-06 | Add file size limit validation (configurable, default 10MB) | Must |
| FR-07 | Add allowed file type whitelist validation | Must |
| FR-08 | Add `MAX_FILE_SIZE_MB` and `ALLOWED_FILE_EXTENSIONS` to config | Should |

### 3.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | No new dependencies — use Python stdlib `mimetypes` module |
| NFR-02 | Maintain backward compatibility (existing upload URLs remain valid) |
| NFR-03 | Unit tests with pytest for all changes |

---

## 4. Scope

### In Scope

- Fix `SupabaseStorageProvider` (content-type, async)
- Fix `FileService` (MIME type, add delete)
- Fix `files.py` endpoints (add delete, add validations)
- Add config settings for limits
- Unit tests

### Out of Scope

- Profile image upload integration (separate feature)
- Comment attachment deletion cascade (separate feature)
- Supabase bucket configuration/policy changes
- Image resizing/thumbnail generation

---

## 5. Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `app/core/config.py` | Modify | Add `MAX_FILE_SIZE_MB`, `ALLOWED_FILE_EXTENSIONS` |
| `app/storage/base.py` | Verify | Confirm interface is correct (already async) |
| `app/storage/supabase.py` | Modify | Fix content-type detection, fix async `get_url()` |
| `app/services/file_service.py` | Modify | Fix MIME type, add `delete_file()`, add validation |
| `app/api/endpoints/files.py` | Modify | Add DELETE endpoint, add size/type validation |
| `tests/test_file_service.py` | Create | Unit tests for FileService |
| `tests/test_storage.py` | Create | Unit tests for storage provider |

---

## 6. Implementation Order

| Step | Task | Dependencies |
|------|------|-------------|
| 1 | Add config settings (`MAX_FILE_SIZE_MB`, `ALLOWED_FILE_EXTENSIONS`) | None |
| 2 | Fix `SupabaseStorageProvider.upload()` — dynamic content-type | Step 1 |
| 3 | Fix `SupabaseStorageProvider.get_url()` — make async | Step 2 |
| 4 | Fix `FileService.upload_file()` — correct MIME type | Step 2 |
| 5 | Add `FileService.delete_file()` | Step 3 |
| 6 | Add file size/type validation in `FileService` | Step 1 |
| 7 | Fix `FileService.get_presigned_url()` — await async call | Step 3 |
| 8 | Add `DELETE /files` endpoint | Step 5 |
| 9 | Add validation error responses in upload endpoint | Step 6 |
| 10 | Write unit tests | Step 8 |
| 11 | Update API spec documentation | Step 9 |

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Changing content-type breaks existing files | Low | Only affects new uploads, existing URLs unchanged |
| supabase-py storage API sync vs async | Medium | Check supabase-py docs, wrap sync calls if needed |
| File size limit may reject valid large files | Low | Make configurable, set reasonable default (10MB) |

---

## 8. Acceptance Criteria

- [ ] All file types upload with correct Content-Type header
- [ ] Upload response returns accurate MIME type (e.g., `image/png`, `application/pdf`)
- [ ] `DELETE /files` endpoint works and removes file from storage
- [ ] Files larger than limit are rejected with 413 error
- [ ] Disallowed file types are rejected with 400 error
- [ ] No async/sync mismatch warnings
- [ ] All unit tests pass
- [ ] API documentation updated
