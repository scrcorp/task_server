from fastapi import APIRouter, HTTPException, Depends
from app.schemas.notification import NotificationListResponse
from app.services.notification_service import NotificationService
from app.core.dependencies import get_notification_repo
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


def _get_service() -> NotificationService:
    return NotificationService(notification_repo=get_notification_repo())


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(current_user: User = Depends(get_current_user)):
    service = _get_service()
    return await service.get_notifications(current_user.id)


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: str, current_user: User = Depends(get_current_user)):
    service = _get_service()
    try:
        result = await service.mark_as_read(notification_id, current_user.id)
        return {"message": "알림이 읽음 처리되었습니다.", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/read-all")
async def mark_all_as_read(current_user: User = Depends(get_current_user)):
    service = _get_service()
    count = await service.mark_all_as_read(current_user.id)
    return {"message": f"{count}개의 알림이 읽음 처리되었습니다.", "count": count}
