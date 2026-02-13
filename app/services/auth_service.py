import uuid
import secrets
from datetime import datetime, timedelta, timezone

from app.repositories.auth import IAuthRepository
from app.repositories.organization import IOrganizationRepository
from app.core.password import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.email import send_verification_code
from app.core.config import settings
from app.schemas.user import UserCreate


def _generate_otp() -> str:
    """Generate a 6-digit numeric OTP code."""
    return f"{secrets.randbelow(1_000_000):06d}"


class AuthService:
    def __init__(self, auth_repo: IAuthRepository, org_repo: IOrganizationRepository):
        self.auth_repo = auth_repo
        self.org_repo = org_repo

    async def login(self, login_id: str, password: str) -> dict:
        user = await self.auth_repo.sign_in(login_id, password)
        access_token = create_access_token(user["id"])
        refresh_token = create_refresh_token(user["id"])
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user["id"],
                "login_id": user["login_id"],
                "email": user.get("email"),
                "full_name": user.get("full_name"),
                "role": user.get("role"),
                "company_id": user.get("company_id"),
                "email_verified": user.get("email_verified", False),
            },
        }

    async def signup(self, data: UserCreate, company_code: str) -> dict:
        # 1. Resolve company_id from company_code
        company = await self.org_repo.get_company_by_code(company_code)
        if not company:
            raise Exception(f"Invalid company code: {company_code}")

        # 2. Check email is verified
        verified = await self.auth_repo.is_email_verified(data.email)
        if not verified:
            raise Exception("Email is not verified. Please verify your email first.")

        # 3. Check duplicate login_id / email
        dup = await self.auth_repo.check_duplicate(data.login_id, data.email)
        if dup:
            raise Exception(dup)

        # 4. Hash password and create account
        profile_data = {
            "id": str(uuid.uuid4()),
            "email": data.email,
            "login_id": data.login_id,
            "password_hash": hash_password(data.password),
            "full_name": data.full_name,
            "company_id": company.id,
            "role": data.role.value,
            "status": data.status.value,
            "language": data.language,
            "email_verified": True,
        }
        user = await self.auth_repo.sign_up(profile_data)

        # 5. Issue tokens
        access_token = create_access_token(user["id"])
        refresh_token = create_refresh_token(user["id"])

        return {
            "message": "Signup successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user["id"],
                "login_id": user["login_id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "company_id": company.id,
            },
        }

    async def logout(self) -> dict:
        return {"message": "Successfully logged out."}

    async def refresh(self, refresh_token_str: str) -> dict:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise Exception("Invalid refresh token.")
        user_id = payload["sub"]
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
        }

    async def verify_email(self, email: str, code: str) -> dict:
        # Look up valid (unused, not expired) verification code
        record = await self.auth_repo.get_valid_verification_code(email, code)
        if not record:
            raise Exception("Invalid or expired verification code.")
        # Mark code as used
        await self.auth_repo.mark_verification_code_used(record["id"])
        return {"message": "Email verified successfully."}

    async def send_verification_email(self, email: str) -> dict:
        # Rate limiting: max 5 codes per hour
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        count = await self.auth_repo.count_recent_codes(email, since)
        if count >= 5:
            raise Exception("Too many requests. Please try again later.")

        # Check if email is already registered
        user = await self.auth_repo.get_user_by_email(email)
        if user:
            raise Exception("Email is already registered.")

        # Invalidate previous codes
        await self.auth_repo.invalidate_previous_codes(email)

        # Generate and save new code (no user_id yet)
        code = _generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.EMAIL_VERIFY_CODE_EXPIRE_MINUTES
        )
        await self.auth_repo.save_verification_code(email, code, expires_at)
        await send_verification_code(email, code)

        return {"message": "Verification code sent."}
