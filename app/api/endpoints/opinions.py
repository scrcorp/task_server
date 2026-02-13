from fastapi import APIRouter, Depends
from typing import List
from app.schemas.opinion import Opinion, OpinionCreate
from app.services.opinion_service import OpinionService
from app.core.dependencies import get_opinion_service
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


@router.post("/", response_model=Opinion, status_code=201)
async def create_opinion(
    body: OpinionCreate,
    current_user: User = Depends(get_current_user),
    service: OpinionService = Depends(get_opinion_service),
):
    return await service.create_opinion(current_user.id, current_user.company_id, body)


@router.get("/", response_model=List[Opinion])
async def list_my_opinions(
    current_user: User = Depends(get_current_user),
    service: OpinionService = Depends(get_opinion_service),
):
    return await service.get_my_opinions(current_user.id, current_user.company_id)
