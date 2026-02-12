from fastapi import APIRouter, HTTPException, Depends
from app.core.security import get_current_user
from app.core.dependencies import get_task_repo, get_notice_repo
from app.services.dashboard_service import DashboardService
from app.schemas.user import User

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    """현재 사용자의 대시보드 요약 정보를 반환합니다."""
    try:
        service = DashboardService(
            task_repo=get_task_repo(),
            notice_repo=get_notice_repo(),
        )
        return await service.get_summary(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
