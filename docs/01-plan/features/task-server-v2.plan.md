# Task Server V2 Planning Document

> **Summary**: Implementation of Staff/Admin API suite with modular architecture for future AWS/On-premise migration.
>
> **Project**: task_server
> **Version**: 1.0.0
> **Author**: Gemini CLI
> **Date**: 2026-02-12
> **Status**: Draft

---

## 1. Overview

### 1.1 Purpose

Expand the existing Task Server to support full Staff and Admin flows as defined in `FLOW.md` and `ADMIN_FLOW.md`, while ensuring the system architecture is decoupled from specific infrastructure providers (Supabase/Render) to facilitate future migration to AWS or On-premise.

### 1.2 Background

The current system relies on Supabase and Render free tiers. As the project scales, a migration to more robust infrastructure like AWS or On-premise is anticipated. Implementing APIs now with a modular "Repository" pattern will minimize the refactoring effort during migration.

### 1.3 Related Documents

- Staff Flow: `FLOW.md`
- Admin Flow: `ADMIN_FLOW.md`
- Existing API Docs: `docs/01-plan/api-specification.md`

---

## 2. Scope

### 2.1 In Scope

- [ ] Implementation of 46+ Admin APIs
- [ ] Implementation of new Staff APIs (Signup, Verification, etc.)
- [ ] Refactoring existing APIs to follow the modular architecture
- [ ] Database schema expansion (Brands, Branches, Groups, Templates, Logs, Feedbacks, etc.)
- [ ] Storage abstraction layer for file uploads
- [ ] Migration Guide documentation
- [ ] Comprehensive API Documentation

### 2.2 Out of Scope

- Frontend implementation
- Real-time notification system (Socket.io/Push) - to be handled in Phase 4
- Actual migration to AWS/On-premise (only preparation)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | Staff Signup & Verification Flow | High | Pending |
| FR-02 | Admin Staff Management (Approval/Groups) | High | Pending |
| FR-03 | Organization Management (Brand/Branch/Group) | High | Pending |
| FR-04 | Checklist Template System (CRUD & Copy to Tasks) | High | Pending |
| FR-05 | Checklist Logging System (Automatic log on check) | High | Pending |
| FR-06 | Monitoring Dashboard (Compliance/Completion) | High | Pending |
| FR-07 | Feedback & Communication (Feedback/Notice/Opinion) | Medium | Pending |
| FR-08 | File Upload Support for Verification | Medium | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| Scalability | Modular architecture (Repository pattern) | Code review |
| Extensibility | Infrastructure-agnostic interfaces | Code review |
| Security | Role-based Access Control (RBAC) | Unit tests / Integration tests |
| Performance | Response time < 500ms for most APIs | Manual testing |

---

## 4. Success Criteria

### 4.1 Definition of Done

- [ ] All functional requirements implemented
- [ ] Unit tests written for core logic
- [ ] Migration guide and API documentation generated
- [ ] Build succeeds on Render

### 4.2 Quality Criteria

- [ ] Clear separation between business logic and DB logic
- [ ] Environment variables used for all configuration
- [ ] Consistent error handling across all endpoints

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Supabase Free Tier Limits | Medium | Medium | Optimize queries and monitor usage |
| Complex Schema Changes | High | Low | Use migrations or structured SQL scripts |
| Future Migration Overhead | High | Low | Strict adherence to Repository pattern |

---

## 6. Architecture Considerations

### 6.1 Project Level Selection

| Level | Characteristics | Recommended For | Selected |
|-------|-----------------|-----------------|:--------:|
| **Dynamic** | Feature-based modules, services layer | Web apps with backend, SaaS MVPs | ☑ |

### 6.2 Key Architectural Decisions

| Decision | Options | Selected | Rationale |
|----------|---------|----------|-----------|
| Architecture | Layered / Repository Pattern | **Repository Pattern** | Decouple DB implementation (Supabase) from Business Logic. |
| DB Layer | Supabase-py / SQLAlchemy | **Supabase-py (Current)** | Use Supabase for now but wrap in a generic interface. |
| Storage | Supabase Storage / AWS S3 | **Abstracted Storage** | Interface `StorageProvider` with Supabase implementation. |
| Auth | Supabase Auth | **Supabase Auth** | Use existing auth but ensure role checking is centralized. |

### 6.3 Clean Architecture Approach

```
Folder Structure Preview:
app/
├── api/          # Route handlers (FastAPI)
├── core/         # Config, security, base interfaces
├── models/       # Pydantic schemas (not DB specific)
├── services/     # Business logic
├── repositories/ # DB implementation details (Supabase, etc.)
└── storage/      # File storage implementations
```

---

## 7. Convention Prerequisites

### 7.1 Existing Project Conventions

- [ ] `GEMINI.md` has coding conventions section
- [ ] `docs/01-plan/conventions.md` exists
- [ ] ESLint configuration (N/A for Python)
- [ ] Prettier configuration (N/A for Python - use Ruff/Black)
- [ ] TypeScript configuration (N/A)

### 7.2 Conventions to Define/Verify

| Category | Current State | To Define | Priority |
|----------|---------------|-----------|:--------:|
| **Naming** | Mixed | Snake_case for Python | High |
| **Folder structure** | Basic | Refined for Repository pattern | High |
| **Error handling** | Basic | Unified HTTP Exception handling | Medium |

### 7.3 Environment Variables Needed

| Variable | Purpose | Scope | To Be Created |
|----------|---------|-------|:-------------:|
| `SUPABASE_URL` | DB Connection | Server | ☑ |
| `SUPABASE_KEY` | DB Connection | Server | ☑ |
| `STORAGE_PROVIDER` | 'supabase' or 's3' | Server | ☑ |

---

## 8. Next Steps

1. [ ] Write design document (`task-server-v2.design.md`)
2. [ ] Expand DB Schema in Supabase
3. [ ] Implement Core Repositories and Services

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-02-12 | Initial draft | Gemini CLI |
