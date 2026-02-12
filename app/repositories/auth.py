from abc import ABC, abstractmethod
from typing import Optional, Any


class IAuthRepository(ABC):
    """Authentication provider interface.
    Supabase, custom JWT, Auth0 등 어떤 인증 시스템이든
    이 인터페이스를 구현하면 교체 가능합니다.
    """

    @abstractmethod
    async def sign_up(self, email: str, password: str, user_metadata: Optional[dict] = None) -> dict:
        """Register a new user in the auth system. Returns auth user data."""
        pass

    @abstractmethod
    async def sign_in(self, email: str, password: str) -> dict:
        """Sign in with email/password. Returns tokens + user info."""
        pass

    @abstractmethod
    async def sign_out(self, token: str) -> bool:
        """Sign out (invalidate token)."""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token. Returns new token pair."""
        pass

    @abstractmethod
    async def get_user_from_token(self, token: str) -> dict:
        """Verify token and return the auth user (id, email, etc.)."""
        pass

    @abstractmethod
    async def update_user_password(self, token: str, new_password: str) -> bool:
        """Update user password."""
        pass


class SupabaseAuthRepository(IAuthRepository):
    """Supabase Auth implementation."""

    def __init__(self, client):
        self.client = client

    async def sign_up(self, email: str, password: str, user_metadata: Optional[dict] = None) -> dict:
        options = {}
        if user_metadata:
            options["data"] = user_metadata
        res = self.client.auth.sign_up({"email": email, "password": password, "options": options})
        if not res.user:
            raise Exception("회원가입에 실패했습니다.")
        return {
            "id": res.user.id,
            "email": res.user.email,
            "access_token": res.session.access_token if res.session else None,
            "refresh_token": res.session.refresh_token if res.session else None,
        }

    async def sign_in(self, email: str, password: str) -> dict:
        res = self.client.auth.sign_in_with_password({"email": email, "password": password})
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "user": {
                "id": res.user.id,
                "email": res.user.email,
            },
        }

    async def sign_out(self, token: str) -> bool:
        # Supabase sign_out works on the current session
        self.client.auth.sign_out()
        return True

    async def refresh_token(self, refresh_token: str) -> dict:
        res = self.client.auth.refresh_session(refresh_token)
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
        }

    async def get_user_from_token(self, token: str) -> dict:
        res = self.client.auth.get_user(token)
        if not res.user:
            raise Exception("유효하지 않은 토큰입니다.")
        return {
            "id": res.user.id,
            "email": res.user.email,
        }

    async def update_user_password(self, token: str, new_password: str) -> bool:
        # Supabase requires setting the session first, then updating
        self.client.auth.get_user(token)  # verify token
        self.client.auth.update_user({"password": new_password})
        return True
