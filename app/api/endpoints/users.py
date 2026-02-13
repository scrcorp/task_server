from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from app.core.security import get_current_user
from app.core.dependencies import get_user_service
from app.services.user_service import UserService
from app.schemas.user import User, UserUpdate

router = APIRouter()


# ── Request Schemas ──────────────────────────────────

class ChangePasswordRequest(BaseModel):
    current_password: str
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
    service: UserService = Depends(get_user_service),
):
    """현재 로그인한 사용자의 프로필을 수정합니다."""
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 항목이 없습니다.")
    return await service.update_profile(current_user.id, update_data)


@router.post("/me/password")
async def change_password(
    body: ChangePasswordRequest,
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """현재 로그인한 사용자의 비밀번호를 변경합니다."""
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 누락되었습니다.")
    token = authorization.replace("Bearer ", "")
    try:
        return await service.change_password(
            token=token,
            current_password=body.current_password,
            new_password=body.new_password,
            user_email=current_user.email,
        )
    except Exception as e:
        if "로그인" in str(e) or "password" in str(e).lower():
            raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
        raise HTTPException(status_code=500, detail="비밀번호 변경에 실패했습니다.")
