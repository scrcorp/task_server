from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import get_current_user
from app.core.dependencies import get_user_service
from app.services.user_service import UserService
from app.schemas.user import User, UserUpdate

router = APIRouter()


# -- Request Schemas --

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# -- Endpoints --

@router.get("/me/profile", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/profile", response_model=User)
async def update_my_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")
    return await service.update_profile(current_user.id, update_data)


@router.post("/me/password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.change_password(
            user_id=current_user.id,
            current_password=body.current_password,
            new_password=body.new_password,
        )
    except Exception as e:
        if "incorrect" in str(e).lower():
            raise HTTPException(status_code=400, detail="Current password is incorrect.")
        raise HTTPException(status_code=500, detail="Failed to change password.")
