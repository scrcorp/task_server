# Design: Email Verification (6-digit OTP Code)

> Feature: email-verification
> Plan: `docs/01-plan/features/email-verification.plan.md`
> Created: 2026-02-13
> Status: Design Phase

---

## 1. Architecture

### 1.1 Flow Diagram

```
[Signup / Resend]
       │
       ▼
┌──────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│ AuthService  │────▶│ AuthRepository      │────▶│ email_verification│
│ generate_otp │     │ save_verification   │     │ _codes (DB)       │
│ (6-digit)    │     │ _code()             │     └───────────────────┘
└──────┬───────┘     └─────────────────────┘
       │
       ▼
┌──────────────┐     ┌─────────────────────┐
│ EmailService │────▶│ app/templates/      │
│ send_email() │     │ verify_email.html   │
└──────────────┘     └─────────────────────┘
       │
       ▼
   [Google SMTP] ──▶ [User Inbox]

[Verify Code]
       │
       ▼
┌──────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│ POST         │────▶│ AuthService         │────▶│ AuthRepository    │
│ /verify-email│     │ verify_email(       │     │ get_valid_code()  │
│ {email,code} │     │   email, code)      │     │ mark_code_used()  │
└──────────────┘     └─────────────────────┘     │ verify_email()    │
                                                  └───────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `AuthService` | OTP generation, verification logic, rate limiting |
| `IAuthRepository` | DB operations for verification codes |
| `EmailService` (`app/core/email.py`) | Template loading, SMTP sending |
| `app/templates/` | HTML email templates with `{variable}` placeholders |

---

## 2. Database Design

### 2.1 New Table: `email_verification_codes`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Primary key |
| `user_id` | `UUID` | NOT NULL, FK → users(id) ON DELETE CASCADE | Owner |
| `email` | `VARCHAR(255)` | NOT NULL | Target email |
| `code` | `VARCHAR(6)` | NOT NULL | 6-digit numeric code |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | Expiration timestamp |
| `used` | `BOOLEAN` | DEFAULT FALSE | Whether code has been used |
| `created_at` | `TIMESTAMPTZ` | DEFAULT NOW() | Creation timestamp |

### 2.2 Indexes

```sql
CREATE INDEX idx_verification_codes_email_active
ON email_verification_codes(email, used, expires_at DESC);
```

### 2.3 Migration SQL

```sql
-- email_verification_codes table
CREATE TABLE email_verification_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_verification_codes_email_active
ON email_verification_codes(email, used, expires_at DESC);
```

---

## 3. API Design

### 3.1 POST `/auth/verify-email`

**Auth**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response 200**:
```json
{
  "message": "Email verified successfully."
}
```

**Error Responses**:
| Status | Detail |
|--------|--------|
| 400 | "Invalid or expired verification code." |
| 429 | "Too many verification attempts. Please try again later." |

### 3.2 POST `/auth/resend-verification`

**Auth**: Not required (uses email to identify user)

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response 200**:
```json
{
  "message": "Verification code sent."
}
```

**Error Responses**:
| Status | Detail |
|--------|--------|
| 400 | "Email is already verified." |
| 404 | "No account found with this email." |
| 429 | "Too many requests. Please try again later." |

### 3.3 Signup Response Change

Signup response message changes to:
```json
{
  "message": "Signup successful. A 6-digit verification code has been sent to your email."
}
```

---

## 4. Detailed Module Design

### 4.1 `app/core/config.py` — Changes

```python
# Add new setting
EMAIL_VERIFY_CODE_EXPIRE_MINUTES: int = 10
# Remove: EMAIL_VERIFY_TOKEN_EXPIRE_HOURS (no longer needed)
```

### 4.2 `app/core/email.py` — Rewrite

```python
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def _load_template(name: str, **kwargs) -> str:
    """Load HTML template and substitute variables."""
    path = TEMPLATE_DIR / name
    html = path.read_text(encoding="utf-8")
    for key, value in kwargs.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))
    return html


async def send_email(to: str, subject: str, html_body: str) -> bool:
    """Send an email via Google SMTP."""
    # ... (same as current)


async def send_verification_code(to: str, code: str) -> bool:
    """Send 6-digit verification code email."""
    html = _load_template(
        "verify_email.html",
        code=code,
        expire_minutes=settings.EMAIL_VERIFY_CODE_EXPIRE_MINUTES,
        app_name=settings.SMTP_FROM_NAME,
    )
    return await send_email(to, "Your verification code", html)


async def send_password_reset_code(to: str, code: str) -> bool:
    """Send 6-digit password reset code email."""
    html = _load_template(
        "reset_password.html",
        code=code,
        app_name=settings.SMTP_FROM_NAME,
    )
    return await send_email(to, "Your password reset code", html)
```

### 4.3 `app/templates/verify_email.html`

```html
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
  <div style="max-width: 480px; margin: 0 auto; background: white; border-radius: 8px; padding: 40px;">
    <h2 style="color: #333; text-align: center;">Email Verification</h2>
    <p style="color: #666; text-align: center;">Enter the following code to verify your email:</p>
    <div style="text-align: center; margin: 30px 0;">
      <span style="
        font-size: 32px;
        font-weight: bold;
        letter-spacing: 8px;
        color: #4CAF50;
        background: #f0f0f0;
        padding: 16px 32px;
        border-radius: 8px;
      ">{{code}}</span>
    </div>
    <p style="color: #999; text-align: center; font-size: 14px;">
      This code expires in {{expire_minutes}} minutes.
    </p>
    <p style="color: #999; text-align: center; font-size: 12px;">
      If you did not request this, please ignore this email.
    </p>
  </div>
</body>
</html>
```

### 4.4 `app/repositories/auth.py` — New Methods

Add to `IAuthRepository` interface:
```python
@abstractmethod
async def save_verification_code(self, user_id: str, email: str, code: str, expires_at: datetime) -> dict:
    pass

@abstractmethod
async def get_valid_verification_code(self, email: str, code: str) -> Optional[dict]:
    pass

@abstractmethod
async def mark_verification_code_used(self, code_id: str) -> bool:
    pass

@abstractmethod
async def invalidate_previous_codes(self, email: str) -> bool:
    pass

@abstractmethod
async def count_recent_codes(self, email: str, since: datetime) -> int:
    pass
```

Add implementations in `CustomAuthRepository`:
- `save_verification_code`: INSERT into `email_verification_codes`
- `get_valid_verification_code`: SELECT WHERE email=, code=, used=false, expires_at > now
- `mark_verification_code_used`: UPDATE used=true
- `invalidate_previous_codes`: UPDATE used=true WHERE email= AND used=false
- `count_recent_codes`: SELECT COUNT WHERE email= AND created_at > since

### 4.5 `app/services/auth_service.py` — Logic Changes

```python
import secrets

def _generate_otp() -> str:
    """Generate a 6-digit numeric OTP code."""
    return f"{secrets.randbelow(1_000_000):06d}"

async def signup(self, data, company_code):
    # ... create user ...
    # Generate and save OTP instead of JWT token
    code = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFY_CODE_EXPIRE_MINUTES)
    await self.auth_repo.save_verification_code(user["id"], data.email, code, expires_at)
    await send_verification_code(data.email, code)

async def verify_email(self, email: str, code: str) -> dict:
    # Get valid code from DB
    record = await self.auth_repo.get_valid_verification_code(email, code)
    if not record:
        raise Exception("Invalid or expired verification code.")
    # Mark code as used
    await self.auth_repo.mark_verification_code_used(record["id"])
    # Set email_verified = true
    await self.auth_repo.verify_email(record["user_id"])
    return {"message": "Email verified successfully."}

async def resend_verification_email(self, email: str) -> dict:
    # Rate limiting: max 5 per hour
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    count = await self.auth_repo.count_recent_codes(email, since)
    if count >= 5:
        raise Exception("Too many requests. Please try again later.")
    # Find user by email
    user = await self.auth_repo.get_user_by_email(email)
    if not user:
        raise Exception("No account found with this email.")
    if user.get("email_verified"):
        raise Exception("Email is already verified.")
    # Invalidate previous codes
    await self.auth_repo.invalidate_previous_codes(email)
    # Generate and save new code
    code = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFY_CODE_EXPIRE_MINUTES)
    await self.auth_repo.save_verification_code(user["id"], email, code, expires_at)
    await send_verification_code(email, code)
    return {"message": "Verification code sent."}
```

### 4.6 `app/api/endpoints/auth.py` — Endpoint Changes

```python
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str  # 6-digit

class ResendVerificationRequest(BaseModel):
    email: EmailStr

@router.post("/verify-email")  # Changed from GET to POST
async def verify_email(body: VerifyEmailRequest, service = Depends(get_auth_service)):
    return await service.verify_email(body.email, body.code)

@router.post("/resend-verification")  # No longer requires auth
async def resend_verification(body: ResendVerificationRequest, service = Depends(get_auth_service)):
    return await service.resend_verification_email(body.email)
```

### 4.7 `app/core/jwt.py` — Remove

Remove `create_email_verification_token()` function (no longer needed).

---

## 5. Test Design

### 5.1 Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures (mock repos, mock email)
├── test_auth_service.py     # AuthService unit tests
├── test_email.py            # Email template loading tests
└── test_auth_endpoints.py   # FastAPI TestClient integration tests
```

### 5.2 Test Cases

**test_auth_service.py**:
| Test | Description |
|------|-------------|
| `test_generate_otp_is_6_digits` | OTP is exactly 6 digits |
| `test_verify_email_success` | Valid code → email_verified=true |
| `test_verify_email_invalid_code` | Wrong code → raises exception |
| `test_verify_email_expired_code` | Expired code → raises exception |
| `test_resend_rate_limit` | >5 requests/hour → raises exception |
| `test_resend_already_verified` | Already verified → raises exception |
| `test_signup_sends_code` | Signup triggers code generation + email |

**test_email.py**:
| Test | Description |
|------|-------------|
| `test_load_template` | Template file loads and substitutes variables |
| `test_template_contains_code` | Rendered HTML contains the 6-digit code |

**test_auth_endpoints.py**:
| Test | Description |
|------|-------------|
| `test_verify_email_endpoint_200` | Valid request returns 200 |
| `test_verify_email_endpoint_400` | Invalid code returns 400 |
| `test_resend_verification_200` | Valid email returns 200 |
| `test_resend_verification_429` | Rate limited returns 429 |

---

## 6. Implementation Order

| # | Task | Files | Depends On |
|---|------|-------|------------|
| 1 | Config update | `app/core/config.py` | - |
| 2 | Email templates | `app/templates/*.html` | - |
| 3 | Email service rewrite | `app/core/email.py` | #2 |
| 4 | Auth repository (verification code methods) | `app/repositories/auth.py` | - |
| 5 | Auth service (OTP logic) | `app/services/auth_service.py` | #1, #3, #4 |
| 6 | Auth endpoints | `app/api/endpoints/auth.py` | #5 |
| 7 | Remove JWT email token | `app/core/jwt.py` | #5 |
| 8 | Test structure + tests | `tests/` | #5, #6 |
| 9 | DB spec + API spec update | `docs/` | #6 |

---

## 7. PDCA Tracking

```
[Plan] -> [Design] -> [Do] -> [Check] -> [Act]
  done       now
```

**Next**: `/pdca do email-verification`
