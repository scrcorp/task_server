# Infrastructure Migration Guide

> **Project**: Task Server
> **Date**: 2026-02-12
> **Goal**: Guide for migrating from Supabase/Render to AWS/On-premise.

---

## 1. Architectural Foundation: Repository Pattern

The current codebase is built using the **Repository Pattern**. This means the business logic (Services) does not know about the underlying database (Supabase).

To migrate to a different database or infrastructure, you only need to:
1.  Implement a new class for the relevant interfaces in `app/repositories/`.
2.  Swap the implementation in the Service layer or via Dependency Injection.

---

## 2. Database Migration (Postgres)

Supabase uses standard Postgres. To migrate to AWS RDS or On-premise Postgres:

### 2.1 Data Export
```bash
# Export from Supabase
pg_dump -h db.supabase.co -U postgres -d postgres > backup.sql
```

### 2.2 Schema Update
The current implementation uses `supabase-py` which wraps PostgREST. If you migrate to standard SQLAlchemy:
1.  Create `PostgresTaskRepository(ITaskRepository)` in `app/repositories/task.py`.
2.  Use SQLAlchemy/SQLModel to perform queries instead of `supabase.table().select()`.

---

## 3. Storage Migration (Supabase to S3)

The system uses an abstracted `IStorageProvider`.

### 3.1 Implementing S3 Provider
Create `app/storage/s3.py`:
```python
class S3StorageProvider(IStorageProvider):
    async def upload(self, file_content, filename, folder):
        # Use boto3 to upload to S3
        pass
```

### 3.2 Configuration Change
Update `.env`:
```env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## 4. Authentication Migration

Currently, the system depends on Supabase Auth. To migrate to custom JWT/Auth0:
1.  Update `app/api/endpoints/auth.py` to use a custom authentication service.
2.  Update the middleware that verifies JWT tokens.

---

## 5. Summary of Required Code Changes

| Component | Files to Modify | Action |
|-----------|-----------------|--------|
| Database | `app/repositories/*.py` | Implement new repositories using SQLAlchemy/AsyncPG |
| Storage | `app/storage/*.py` | Implement `S3StorageProvider` or `LocalStorageProvider` |
| Auth | `app/core/security.py` | Implement custom JWT verification |
| Config | `.env` | Update connection strings and provider flags |
