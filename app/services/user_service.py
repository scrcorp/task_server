from typing import Optional
from app.repositories.user import SupabaseUserRepository
from app.repositories.auth import IAuthRepository
from app.schemas.user import User, UserUpdate


class UserService:
    def __init__(self, user_repo: SupabaseUserRepository, auth_repo: IAuthRepository):
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def get_profile(self, user_id: str) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def update_profile(self, user_id: str, data: dict) -> User:
        return await self.user_repo.update(user_id, data)

    async def change_password(self, token: str, current_password: str, new_password: str, user_email: str) -> dict:
        # Verify current password by attempting sign-in
        await self.auth_repo.sign_in(user_email, current_password)
        # Update to new password
        await self.auth_repo.update_user_password(token, new_password)
        return {"message": "비밀번호가 변경되었습니다."}
