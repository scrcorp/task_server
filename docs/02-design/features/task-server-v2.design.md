# Task Server V2 Design Document

> **Summary**: Modular API design with Repository Pattern for Staff/Admin flows, decoupled from Supabase for future AWS/On-premise migration.
>
> **Project**: task_server
> **Version**: 1.0.0
> **Author**: Gemini CLI
> **Date**: 2026-02-12
> **Status**: Draft
> **Planning Doc**: [task-server-v2.plan.md](../../01-plan/features/task-server-v2.plan.md)

---

## 1. Overview

### 1.1 Design Goals

- Implement 46+ Admin APIs and new Staff APIs.
- Achieve 100% decoupling of business logic from database-specific implementation (Supabase).
- Ensure file storage is abstracted to allow switching between Supabase Storage and AWS S3/Local Storage.
- Provide a clear migration path to AWS/On-premise.

### 1.2 Design Principles

- **Single Responsibility Principle (SRP)**: Each service handles a specific domain.
- **Dependency Inversion Principle (DIP)**: High-level services depend on abstractions (interfaces), not low-level implementations (Supabase).
- **Interface Segregation**: Repositories define clean interfaces for data access.

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Clients   │────▶│   FastAPI   │────▶│   Services   │────▶│ Repositories │
│(Staff/Admin)│     │  Endpoints  │     │(Business Log)│     │ (Interfaces) │
└─────────────┘     └─────────────┘     └──────────────┘     └──────┬───────┘
                                                                    │
                                            ┌───────────────────────┴────────┐
                                            │ Implementations (Supabase/Postgres)
                                            └────────────────────────────────┘
```

### 2.2 Data Flow

1. **Request**: FastAPI endpoint receives request and validates schema (Pydantic).
2. **Service**: Endpoint calls a Service method. Service orchestrates business logic.
3. **Repository**: Service calls a Repository interface method.
4. **Implementation**: The concrete implementation (e.g., `SupabaseTaskRepository`) executes the actual query.
5. **Response**: Data is mapped back to Pydantic models and returned to the client.

### 2.3 Layer Assignments

| Layer | Responsibility | Location |
|-------|---------------|----------|
| **API/Presentation** | Request routing, auth verification, Pydantic validation | `app/api/` |
| **Application/Service** | Business logic, orchestration, transaction management | `app/services/` |
| **Domain/Model** | Core entities, enums, shared types | `app/models/`, `app/schemas/` |
| **Infrastructure/Repository** | DB queries, storage access, external API calls | `app/repositories/`, `app/storage/` |

---

## 3. Data Model

### 3.1 Entity Relationships (Extended)

```
[Brand] 1 ──── N [Branch] 1 ──── N [Group] 1 ──── N [Staff/User]
   │                │
   │                └─ 1 ── N [Task (type:daily/assigned)]
   │                            │
   └─ 1 ── N [ChecklistTemplate] │
                │               │
                └─ 1 ── N [TemplateItem] ──→ (Copies to) ──→ [ChecklistItem]
                                                                │
                                                                └─ 1 ── N [ChecklistLog]
```

### 3.2 Key New Tables (SQL Preview)

```sql
-- Organization
CREATE TABLE brands (id UUID PRIMARY KEY, name TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE branches (id UUID PRIMARY KEY, brand_id UUID REFERENCES brands(id), name TEXT, address TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE groups (id UUID PRIMARY KEY, branch_id UUID REFERENCES branches(id), name TEXT, created_at TIMESTAMPTZ DEFAULT NOW());

-- Templates
CREATE TABLE checklist_templates (
    id UUID PRIMARY KEY,
    title TEXT,
    brand_id UUID REFERENCES brands(id),
    group_id UUID REFERENCES groups(id), -- nullable
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id)
);

CREATE TABLE checklist_template_items (
    id UUID PRIMARY KEY,
    template_id UUID REFERENCES checklist_templates(id),
    content TEXT,
    verification_type TEXT, -- 'none', 'photo'
    sort_order INT
);

-- Logs & Feedback
CREATE TABLE checklist_logs (
    id UUID PRIMARY KEY,
    item_id UUID REFERENCES checklist_items(id),
    user_id UUID REFERENCES auth.users(id),
    is_completed BOOLEAN,
    verification_data TEXT, -- URL
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE feedbacks (
    id UUID PRIMARY KEY,
    author_id UUID REFERENCES auth.users(id),
    target_user_id UUID REFERENCES auth.users(id),
    task_id UUID REFERENCES tasks(id),
    checklist_log_id UUID REFERENCES checklist_logs(id),
    content TEXT,
    photo_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. Repository Abstraction

### 4.1 Base Repository Interface

```python
# app/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]: pass
    
    @abstractmethod
    async def list(self, filters: dict) -> List[T]: pass
    
    @abstractmethod
    async def create(self, data: T) -> T: pass
    
    @abstractmethod
    async def update(self, id: str, data: dict) -> T: pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool: pass
```

### 4.2 Storage Interface

```python
# app/storage/base.py
class IStorageProvider(ABC):
    @abstractmethod
    async def upload(self, file_content: bytes, filename: str, folder: str) -> str: pass
    
    @abstractmethod
    async def get_url(self, file_path: str) -> str: pass
```

---

## 5. API Specification (Highlights)

### 5.1 Admin Staff Management

- `GET /admin/staff/pending`: Returns list of users with `status='pending'`.
- `PATCH /admin/staff/{id}/approve`: Updates `status='active'` and sets `group_id`.

### 5.2 Checklist Template Flow

- `POST /admin/checklist-templates`: Creates template and its items.
- **Automation Rule**: When a `daily` task is created (manually or by scheduler), the service layer copies items from the relevant `checklist_templates` based on the user's `brand_id` and `group_id`.

---

## 6. Error Handling

Unified Error Handling using FastAPI Exception Handlers.

| Code | Type | Description |
|------|------|-------------|
| 403 | Forbidden | User role (staff) attempting to access `/admin/*` |
| 404 | NotFound | Resource (branch, group, task) does not exist |
| 422 | ValidationError | Invalid Pydantic model |

---

## 7. Migration Strategy (Preparation)

To migrate from Supabase to AWS/On-premise:
1. **DB Migration**: Use `pg_dump` to move data from Supabase Postgres to RDS/On-premise Postgres.
2. **Repository Swap**: Create `PostgresTaskRepository` using SQLAlchemy or AsyncPG, implementing the same `ITaskRepository` interface.
3. **Storage Swap**: Create `S3StorageProvider` implementing `IStorageProvider`.
4. **Auth Swap**: Replace Supabase Auth middleware with custom JWT/OAuth2 middleware.
5. **Config Update**: Change `DATABASE_URL` and `STORAGE_TYPE` in `.env`.

---

## 8. Implementation Order

1. **Phase 1: Interfaces & Models**: Define all Pydantic schemas and ABC interfaces.
2. **Phase 2: Database Expansion**: Apply SQL scripts to Supabase to create new tables.
3. **Phase 3: Supabase Implementations**: Implement the repositories using `supabase-py`.
4. **Phase 4: Services**: Implement business logic for Staff/Admin flows.
5. **Phase 6: Endpoints**: Connect services to FastAPI routes.
6. **Phase 7: Docs & Migration Guide**: Generate documentation.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-02-12 | Initial design with Repository Pattern | Gemini CLI |
