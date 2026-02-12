from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.core.dependencies import get_auth_repo, get_user_repo
from app.repositories.auth import IAuthRepository
from app.schemas.user import User, UserRole


async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 누락되었습니다.")

    token = authorization.replace("Bearer ", "")
    try:
        auth_repo = get_auth_repo()
        user_repo = get_user_repo()

        # 1. Verify token via auth repository
        auth_user = await auth_repo.get_user_from_token(token)
        user_id = auth_user["id"]

        # 2. Get user profile from DB via user repository
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자 프로필을 찾을 수 없습니다.")

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"인증 실패: {str(e)}")


def require_role(roles: list[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"접근 권한이 없습니다. 필요한 역할: {[r.value for r in roles]}",
            )
        return current_user
    return role_checker
