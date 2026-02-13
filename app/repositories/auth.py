from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional


class IAuthRepository(ABC):
    @abstractmethod
    async def sign_up(self, data: dict) -> dict:
        pass

    @abstractmethod
    async def sign_in(self, login_id: str, password: str) -> dict:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_user_by_login_id(self, login_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        pass

    @abstractmethod
    async def verify_email(self, user_id: str) -> bool:
        pass

    @abstractmethod
    async def check_duplicate(self, login_id: str, email: str) -> Optional[str]:
        pass

    # -- Verification code methods --

    @abstractmethod
    async def save_verification_code(
        self, user_id: str, email: str, code: str, expires_at: datetime
    ) -> dict:
        pass

    @abstractmethod
    async def get_valid_verification_code(
        self, email: str, code: str
    ) -> Optional[dict]:
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


class CustomAuthRepository(IAuthRepository):
    """Auth repository backed by users table + bcrypt + custom JWT."""

    def __init__(self, client):
        self.client = client
        self.table = "users"
        self.codes_table = "email_verification_codes"

    async def sign_up(self, data: dict) -> dict:
        res = self.client.table(self.table).insert(data).execute()
        if not res.data:
            raise Exception("Failed to create user.")
        return res.data[0]

    async def sign_in(self, login_id: str, password: str) -> dict:
        from app.core.password import verify_password

        user = await self.get_user_by_login_id(login_id)
        if not user:
            raise Exception("Invalid login ID or password.")
        if not user.get("password_hash"):
            raise Exception("Invalid login ID or password.")
        if not verify_password(password, user["password_hash"]):
            raise Exception("Invalid login ID or password.")
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        res = (
            self.client.table(self.table)
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        return res.data

    async def get_user_by_login_id(self, login_id: str) -> Optional[dict]:
        res = (
            self.client.table(self.table)
            .select("*")
            .eq("login_id", login_id)
            .maybe_single()
            .execute()
        )
        return res.data

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        res = (
            self.client.table(self.table)
            .select("*")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        return res.data

    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        self.client.table(self.table).update(
            {"password_hash": new_password_hash}
        ).eq("id", user_id).execute()
        return True

    async def verify_email(self, user_id: str) -> bool:
        self.client.table(self.table).update(
            {"email_verified": True}
        ).eq("id", user_id).execute()
        return True

    async def check_duplicate(self, login_id: str, email: str) -> Optional[str]:
        """Return an error message if login_id or email is already taken, else None."""
        existing = (
            self.client.table(self.table)
            .select("id, login_id, email")
            .or_(f"login_id.eq.{login_id},email.eq.{email}")
            .execute()
        )
        if existing.data:
            for row in existing.data:
                if row["login_id"] == login_id:
                    return "Login ID is already taken."
                if row["email"] == email:
                    return "Email is already registered."
        return None

    # -- Verification code methods --

    async def save_verification_code(
        self, user_id: str, email: str, code: str, expires_at: datetime
    ) -> dict:
        res = (
            self.client.table(self.codes_table)
            .insert(
                {
                    "user_id": user_id,
                    "email": email,
                    "code": code,
                    "expires_at": expires_at.isoformat(),
                }
            )
            .execute()
        )
        if not res.data:
            raise Exception("Failed to save verification code.")
        return res.data[0]

    async def get_valid_verification_code(
        self, email: str, code: str
    ) -> Optional[dict]:
        res = (
            self.client.table(self.codes_table)
            .select("*")
            .eq("email", email)
            .eq("code", code)
            .eq("used", False)
            .gte("expires_at", datetime.now(timezone.utc).isoformat())
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    async def mark_verification_code_used(self, code_id: str) -> bool:
        self.client.table(self.codes_table).update(
            {"used": True}
        ).eq("id", code_id).execute()
        return True

    async def invalidate_previous_codes(self, email: str) -> bool:
        self.client.table(self.codes_table).update(
            {"used": True}
        ).eq("email", email).eq("used", False).execute()
        return True

    async def count_recent_codes(self, email: str, since: datetime) -> int:
        res = (
            self.client.table(self.codes_table)
            .select("id", count="exact")
            .eq("email", email)
            .gte("created_at", since.isoformat())
            .execute()
        )
        return res.count or 0
