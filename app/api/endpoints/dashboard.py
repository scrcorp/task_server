from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.dependencies import get_dashboard_service
from app.services.dashboard_service import DashboardService
from app.schemas.user import User

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    """현재 사용자의 대시보드 요약 정보를 반환합니다."""
    return await service.get_summary(current_user.id)
