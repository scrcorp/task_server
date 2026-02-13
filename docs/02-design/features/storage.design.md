# PDCA Design: Storage Improvement

> **Feature**: storage
> **Created**: 2026-02-13
> **Phase**: Design
> **Plan Reference**: `docs/01-plan/features/storage.plan.md`

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  API Layer (app/api/endpoints/files.py)                  │
│  POST /upload  |  POST /presigned-url  |  DELETE /delete │
│  ├─ File size validation (MAX_FILE_SIZE_MB)              │
│  └─ File type validation (ALLOWED_FILE_EXTENSIONS)       │
├─────────────────────────────────────────────────────────┤
│  Service Layer (app/services/file_service.py)            │
│  upload_file()  |  get_presigned_url()  |  delete_file() │
│  ├─ MIME type detection (mimetypes.guess_type)           │
│  └─ Unique filename generation (uuid)                    │
├─────────────────────────────────────────────────────────┤
│  Storage Layer (app/storage/)                            │
│  IStorageProvider (base.py) ← interface                  │
│  SupabaseStorageProvider (supabase.py) ← implementation  │
│  ├─ upload() — dynamic content-type                      │
│  ├─ delete() — remove from bucket                        │
│  └─ get_url() — async, return public URL                 │
├─────────────────────────────────────────────────────────┤
│  Config (app/core/config.py)                             │
│  MAX_FILE_SIZE_MB  |  ALLOWED_FILE_EXTENSIONS            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Module Design

### 2.1 `app/core/config.py` — Add Storage Settings

```python
# Storage
MAX_FILE_SIZE_MB: int = 10
ALLOWED_FILE_EXTENSIONS: str = "jpg,jpeg,png,gif,webp,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,csv,zip"
```

- `MAX_FILE_SIZE_MB`: Maximum upload file size in megabytes (default: 10)
- `ALLOWED_FILE_EXTENSIONS`: Comma-separated whitelist of allowed extensions (default: common office + image types)

### 2.2 `app/storage/base.py` — Interface (No Change)

Current interface is correct. All three methods are already `async def`.

```python
class IStorageProvider(ABC):
    async def upload(self, file_content: bytes, filename: str, folder: str) -> str
    async def delete(self, file_path: str) -> bool
    async def get_url(self, file_path: str) -> str
```

### 2.3 `app/storage/supabase.py` — Fix Implementation

#### Change 1: Dynamic content-type in `upload()`

```python
import mimetypes

async def upload(self, file_content: bytes, filename: str, folder: str) -> str:
    file_path = f"{folder}/{filename}"
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    res = supabase.storage.from_(self.bucket_name).upload(
        path=file_path,
        file=file_content,
        file_options={"content-type": content_type}
    )
    return await self.get_url(file_path)
```

**Key**: Use `mimetypes.guess_type()` to detect content-type from filename. Fallback to `application/octet-stream`.

#### Change 2: Make `get_url()` async

```python
async def get_url(self, file_path: str) -> str:
    res = supabase.storage.from_(self.bucket_name).get_public_url(file_path)
    return res
```

**Key**: Change `def get_url` → `async def get_url` to match interface.

### 2.4 `app/services/file_service.py` — Fix & Extend

#### Full redesign:

```python
import uuid
import mimetypes
from app.storage.base import IStorageProvider
from app.core.config import settings


def _get_content_type(filename: str) -> str:
    """Detect MIME type from filename using stdlib mimetypes."""
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


def _get_allowed_extensions() -> set:
    """Parse allowed extensions from config string."""
    return {ext.strip().lower() for ext in settings.ALLOWED_FILE_EXTENSIONS.split(",")}


class FileService:
    def __init__(self, storage_provider: IStorageProvider):
        self.storage = storage_provider

    async def upload_file(self, file_content: bytes, original_filename: str, folder: str) -> dict:
        # Validate file size
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_content) > max_bytes:
            raise ValueError(f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit.")

        # Validate file extension
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        if not ext or ext not in _get_allowed_extensions():
            raise ValueError(f"File type '.{ext}' is not allowed.")

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex}.{ext}"

        # Upload
        url = await self.storage.upload(file_content, unique_name, folder)

        return {
            "file_url": url,
            "file_name": unique_name,
            "file_size": len(file_content),
            "content_type": _get_content_type(original_filename),
        }

    async def delete_file(self, file_path: str) -> bool:
        return await self.storage.delete(file_path)

    async def get_presigned_url(self, file_path: str) -> str:
        return await self.storage.get_url(file_path)
```

**Changes**:
1. `_get_content_type()` — Uses `mimetypes.guess_type()` instead of `f"application/{ext}"`
2. `_get_allowed_extensions()` — Parses config whitelist
3. File size validation — `ValueError` if exceeds `MAX_FILE_SIZE_MB`
4. File type validation — `ValueError` if extension not in whitelist
5. `delete_file()` — New method wrapping `storage.delete()`
6. `get_presigned_url()` — Now awaits async `get_url()`

### 2.5 `app/api/endpoints/files.py` — Add Delete & Validation

```python
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from app.services.file_service import FileService
from app.core.dependencies import get_file_service
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


class PresignedUrlRequest(BaseModel):
    file_path: str


class DeleteFileRequest(BaseModel):
    file_path: str


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query(default="uploads"),
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    content = await file.read()
    try:
        result = await service.upload_file(content, file.filename, folder)
    except ValueError as e:
        status = 413 if "size" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e))
    return result


@router.post("/presigned-url")
async def get_presigned_url(
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    url = await service.get_presigned_url(body.file_path)
    return {"url": url}


@router.delete("/delete")
async def delete_file(
    body: DeleteFileRequest,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    await service.delete_file(body.file_path)
    return {"message": "File deleted successfully."}
```

**Changes**:
1. Upload now catches `ValueError` and returns 413 (size) or 400 (type)
2. New `DELETE /files/delete` endpoint with `DeleteFileRequest` body
3. New `DeleteFileRequest` schema

### 2.6 API Specification Updates

#### DELETE `/files/delete` — Delete File (NEW)

| Item | Value |
|------|-------|
| Auth | Required |

**Request Body**
```json
{ "file_path": "uploads/abc123.png" }
```

**Response** `200 OK`
```json
{ "message": "File deleted successfully." }
```

**Error Responses**

| Status | Condition |
|--------|-----------|
| 401 | Not authenticated |

#### POST `/files/upload` — Error Responses (NEW)

| Status | Condition | Detail |
|--------|-----------|--------|
| 413 | File exceeds size limit | `"File size exceeds 10MB limit."` |
| 400 | File type not allowed | `"File type '.exe' is not allowed."` |

---

## 3. Test Design

### 3.1 Test File: `tests/test_file_service.py`

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | `test_upload_file_success` | Returns dict with correct file_url, file_name, file_size, content_type |
| 2 | `test_upload_detects_mime_type_png` | content_type = `image/png` |
| 3 | `test_upload_detects_mime_type_pdf` | content_type = `application/pdf` |
| 4 | `test_upload_file_size_exceeds_limit` | Raises `ValueError` with "size" message |
| 5 | `test_upload_file_type_not_allowed` | Raises `ValueError` with "not allowed" message |
| 6 | `test_upload_no_extension` | Raises `ValueError` |
| 7 | `test_delete_file_success` | Returns `True` |
| 8 | `test_get_presigned_url` | Returns URL string |

### 3.2 Test File: `tests/test_file_endpoints.py`

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | `test_upload_success` | 200 with file_url |
| 2 | `test_upload_too_large` | 413 error |
| 3 | `test_upload_bad_type` | 400 error |
| 4 | `test_delete_success` | 200 with message |
| 5 | `test_presigned_url_success` | 200 with url |

### 3.3 Fake Storage Provider (in `tests/conftest.py`)

```python
class FakeStorageProvider(IStorageProvider):
    def __init__(self):
        self.files = {}

    async def upload(self, file_content, filename, folder):
        path = f"{folder}/{filename}"
        self.files[path] = file_content
        return f"https://storage.example.com/{path}"

    async def delete(self, file_path):
        self.files.pop(file_path, None)
        return True

    async def get_url(self, file_path):
        return f"https://storage.example.com/{file_path}"
```

---

## 4. Implementation Order

| Step | File | Changes | Depends On |
|------|------|---------|-----------|
| 1 | `app/core/config.py` | Add `MAX_FILE_SIZE_MB`, `ALLOWED_FILE_EXTENSIONS` | - |
| 2 | `app/storage/supabase.py` | Fix content-type, make `get_url` async | - |
| 3 | `app/services/file_service.py` | Fix MIME, add validation, add `delete_file`, await `get_url` | Step 1, 2 |
| 4 | `app/api/endpoints/files.py` | Add delete endpoint, catch `ValueError` | Step 3 |
| 5 | `tests/conftest.py` | Add `FakeStorageProvider` fixture | - |
| 6 | `tests/test_file_service.py` | 8 unit tests | Step 3, 5 |
| 7 | `tests/test_file_endpoints.py` | 5 endpoint tests | Step 4, 5 |
| 8 | `docs/API_SPECIFICATION_V2.md` | Update Files section | Step 4 |

---

## 5. Acceptance Checklist

- [ ] `mimetypes.guess_type()` used for content-type detection in storage upload
- [ ] `get_url()` is `async def` in both interface and implementation
- [ ] Upload response returns correct MIME type (`image/png`, `application/pdf`, etc.)
- [ ] `DELETE /files/delete` endpoint removes file from Supabase Storage
- [ ] Upload rejects files > `MAX_FILE_SIZE_MB` with HTTP 413
- [ ] Upload rejects disallowed file types with HTTP 400
- [ ] `ALLOWED_FILE_EXTENSIONS` and `MAX_FILE_SIZE_MB` configurable via `.env`
- [ ] `FakeStorageProvider` added to test fixtures
- [ ] 13 total tests pass (8 service + 5 endpoint)
- [ ] API documentation updated with delete endpoint and error responses
