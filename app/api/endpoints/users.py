from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from app.core.security import get_current_user
from app.core.dependencies import get_auth_repo, get_user_repo
from app.services.auth_service import AuthService
from app.schemas.user import User, UserUpdate

router = APIRouter()


# ── Request Schemas ──────────────────────────────────

class ChangePasswordRequest(BaseModel):
    new_password: str


# ── Endpoints ────────────────────────────────────────

@router.get("/me/profile", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 프로필을 반환합니다."""
    return current_user


@router.patch("/me/profile", response_model=User)
async def update_my_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """현재 로그인한 사용자의 프로필을 수정합니다."""
    try:
        user_repo = get_user_repo()
        update_data = body.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 항목이 없습니다.")
        updated_user = await user_repo.update(current_user.id, update_data)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/me/password")
async def change_password(
    body: ChangePasswordRequest,
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
):
    """현재 로그인한 사용자의 비밀번호를 변경합니다."""
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 누락되었습니다.")
    token = authorization.replace("Bearer ", "")
    try:
        auth_service = AuthService(
            auth_repo=get_auth_repo(), user_repo=get_user_repo()
        )
        return await auth_service.change_password(token, body.new_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
