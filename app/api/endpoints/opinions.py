from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.opinion import Opinion, OpinionCreate
from app.services.opinion_service import OpinionService
from app.core.dependencies import get_opinion_repo
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


def _get_service() -> OpinionService:
    return OpinionService(opinion_repo=get_opinion_repo())


@router.post("/", response_model=Opinion, status_code=201)
async def create_opinion(body: OpinionCreate, current_user: User = Depends(get_current_user)):
    service = _get_service()
    try:
        return await service.create_opinion(current_user.id, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Opinion])
async def list_my_opinions(current_user: User = Depends(get_current_user)):
    service = _get_service()
    return await service.get_my_opinions(current_user.id)
