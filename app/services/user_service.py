from typing import Optional
from app.repositories.user import SupabaseUserRepository
from app.repositories.auth import IAuthRepository
from app.core.password import hash_password, verify_password
from app.schemas.user import User


class UserService:
    def __init__(self, user_repo: SupabaseUserRepository, auth_repo: IAuthRepository):
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def get_profile(self, user_id: str) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def update_profile(self, user_id: str, data: dict) -> User:
        return await self.user_repo.update(user_id, data)

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        user_data = await self.auth_repo.get_user_by_id(user_id)
        if not user_data or not user_data.get("password_hash"):
            raise Exception("User not found.")
        if not verify_password(current_password, user_data["password_hash"]):
            raise Exception("Current password is incorrect.")
        new_hash = hash_password(new_password)
        await self.auth_repo.update_password(user_id, new_hash)
        return {"message": "Password changed successfully."}
