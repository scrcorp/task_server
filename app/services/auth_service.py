from typing import Optional
from app.repositories.auth import IAuthRepository
from app.repositories.user import SupabaseUserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, auth_repo: IAuthRepository, user_repo: SupabaseUserRepository):
        self.auth_repo = auth_repo
        self.user_repo = user_repo

    async def login(self, email: str, password: str) -> dict:
        return await self.auth_repo.sign_in(email, password)

    async def signup(self, data: UserCreate) -> dict:
        # 1. Create auth user
        auth_result = await self.auth_repo.sign_up(
            email=data.email,
            password=data.password,
            user_metadata={"full_name": data.full_name, "login_id": data.login_id},
        )

        # 2. Create user profile in DB
        profile_data = {
            "id": auth_result["id"],
            "email": data.email,
            "login_id": data.login_id,
            "full_name": data.full_name,
            "role": data.role.value,
            "status": data.status.value,
            "branch_id": data.branch_id,
            "language": data.language,
        }
        await self.user_repo.create(profile_data)

        return {
            "message": "회원가입이 완료되었습니다.",
            "user": {
                "id": auth_result["id"],
                "email": data.email,
                "full_name": data.full_name,
            },
        }

    async def logout(self, token: str) -> dict:
        await self.auth_repo.sign_out(token)
        return {"message": "로그아웃되었습니다."}

    async def refresh(self, refresh_token: str) -> dict:
        return await self.auth_repo.refresh_token(refresh_token)

    async def get_current_auth_user(self, token: str) -> dict:
        return await self.auth_repo.get_user_from_token(token)

    async def change_password(self, token: str, new_password: str) -> dict:
        await self.auth_repo.update_user_password(token, new_password)
        return {"message": "비밀번호가 변경되었습니다."}
