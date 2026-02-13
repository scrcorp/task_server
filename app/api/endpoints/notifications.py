from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.schemas.notification import NotificationListResponse
from app.services.notification_service import NotificationService
from app.core.dependencies import get_notification_service
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    return await service.get_notifications(current_user.id)


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    result = await service.mark_as_read(notification_id, current_user.id)
    return {"message": "알림이 읽음 처리되었습니다.", "data": result}


@router.patch("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    count = await service.mark_all_as_read(current_user.id)
    return {"message": f"{count}개의 알림이 읽음 처리되었습니다.", "count": count}
