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
    return await service.get_summary(current_user.id, current_user.company_id)
