# Plan: Email Verification (6-digit OTP Code)

> Feature: email-verification
> Created: 2026-02-13
> Status: Plan Phase

---

## 1. Overview

Replace the current JWT token link-based email verification with a 6-digit numeric OTP code system.
Additionally, extract inline HTML email templates into separate template files and add pytest-based unit tests.

### 1.1 Current State (AS-IS)

| Item | Current Implementation |
|------|----------------------|
| Verification method | JWT token embedded in URL link (`GET /verify-email?token=...`) |
| Email template | Inline HTML in `app/core/email.py` (lines 29-47) |
| Code storage | None (stateless JWT) |
| Template location | No separate template files |
| Tests | None (no test files in project) |

### 1.2 Target State (TO-BE)

| Item | Target Implementation |
|------|----------------------|
| Verification method | 6-digit numeric OTP code (`POST /verify-email` with `{email, code}`) |
| Email template | Separate HTML template files in `app/templates/` |
| Code storage | `email_verification_codes` table in Supabase |
| Template location | `app/templates/verify_email.html`, `app/templates/reset_password.html` |
| Tests | `tests/` directory with pytest unit tests |

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Generate random 6-digit numeric code (000000~999999) | HIGH |
| FR-02 | Store code in DB with expiration time (default: 10 minutes) | HIGH |
| FR-03 | Send code via Google SMTP email with HTML template | HIGH |
| FR-04 | Verify code via `POST /verify-email` endpoint | HIGH |
| FR-05 | Rate limit: max 5 verification requests per email per hour | MEDIUM |
| FR-06 | Code is single-use (mark as used after verification) | HIGH |
| FR-07 | Resend code endpoint (`POST /resend-verification`) | HIGH |
| FR-08 | Email HTML templates in separate files with variable substitution | MEDIUM |
| FR-09 | Password reset also uses 6-digit OTP (future, same pattern) | LOW |

### 2.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-01 | OTP code expires after configurable minutes (default 10) | HIGH |
| NFR-02 | pytest test coverage for auth service, email, and endpoints | HIGH |
| NFR-03 | Previous unused codes invalidated when new code is sent | MEDIUM |

---

## 3. Scope

### 3.1 In Scope

- [x] New DB table: `email_verification_codes`
- [x] 6-digit OTP generation and storage
- [x] Email template files (`app/templates/`)
- [x] Modified auth endpoints (verify-email, resend-verification)
- [x] Updated auth service and repository
- [x] Config changes (expiration time)
- [x] pytest test structure and initial test files
- [x] DB spec update
- [x] API spec update

### 3.2 Out of Scope

- SMS-based OTP (email only)
- Password reset OTP (future feature, same pattern)
- Frontend UI changes
- Email delivery monitoring/retry queue

---

## 4. Technical Design Summary

### 4.1 New DB Table

```sql
CREATE TABLE email_verification_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_verification_codes_email ON email_verification_codes(email, used, expires_at);
```

### 4.2 Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `app/core/config.py` | MODIFY | Add `EMAIL_VERIFY_CODE_EXPIRE_MINUTES: int = 10` |
| `app/core/email.py` | REWRITE | Use template files instead of inline HTML |
| `app/core/jwt.py` | MODIFY | Remove `create_email_verification_token()` |
| `app/repositories/auth.py` | MODIFY | Add verification code CRUD methods |
| `app/services/auth_service.py` | MODIFY | 6-digit OTP logic (generate, verify, resend) |
| `app/api/endpoints/auth.py` | MODIFY | `POST /verify-email` body-based, add `VerifyEmailRequest` |
| `docs/DB_SPECIFICATION_V2.md` | UPDATE | Add `email_verification_codes` table |
| `docs/API_SPECIFICATION_V2.md` | UPDATE | Update verify-email endpoint spec |

### 4.3 New Files to Create

| File | Description |
|------|-------------|
| `app/templates/verify_email.html` | Email verification HTML template |
| `app/templates/reset_password.html` | Password reset HTML template |
| `tests/__init__.py` | Test package init |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/test_auth_service.py` | Auth service unit tests |
| `tests/test_email.py` | Email service unit tests |
| `tests/test_auth_endpoints.py` | Auth endpoint integration tests |

### 4.4 API Changes

**Before (current)**:
```
GET /api/v1/auth/verify-email?token=<jwt_token>
POST /api/v1/auth/resend-verification  (auth required)
```

**After (target)**:
```
POST /api/v1/auth/verify-email
Body: { "email": "user@example.com", "code": "123456" }

POST /api/v1/auth/resend-verification
Body: { "email": "user@example.com" }
```

---

## 5. Implementation Order

1. DB table creation (`email_verification_codes`)
2. Config update (expiration setting)
3. Email HTML templates (`app/templates/`)
4. Email service rewrite (use templates)
5. Auth repository (verification code CRUD)
6. Auth service (OTP generate/verify/resend logic)
7. Auth endpoints (new request/response schemas)
8. DB spec + API spec update
9. Test structure and test files
10. Verify & cleanup (remove unused JWT email token function)

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SMTP not configured | Signup works but no email sent | Already handled — try/except in signup, log warning |
| Brute force OTP guessing | 6-digit = 1M combinations | Rate limit (FR-05) + expiration (NFR-01) |
| DB table not migrated | Verification fails | Migration SQL in spec, clear deployment notes |

---

## 7. PDCA Tracking

```
[Plan] -> [Design] -> [Do] -> [Check] -> [Act]
  now
```

**Next**: `/pdca design email-verification`
