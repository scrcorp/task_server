from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from app.services.daily_checklist_service import DailyChecklistService
from app.core.security import get_current_user
from app.core.dependencies import get_daily_checklist_service
from app.schemas.user import User

router = APIRouter()


# ── Request Schemas ──────────────────────────────────

class GenerateChecklistRequest(BaseModel):
    template_id: str
    branch_id: str
    date: str
    group_ids: Optional[List[str]] = None

class ChecklistItemUpdateRequest(BaseModel):
    is_completed: bool
    verification_data: Optional[str] = None


# ── Endpoints ────────────────────────────────────────

@router.get("/")
async def list_daily_checklists(
    branch_id: str,
    date: str,
    current_user: User = Depends(get_current_user),
    service: DailyChecklistService = Depends(get_daily_checklist_service),
):
    return await service.list_by_branch_date(branch_id, date)


@router.get("/{checklist_id}")
async def get_daily_checklist(
    checklist_id: str,
    current_user: User = Depends(get_current_user),
    service: DailyChecklistService = Depends(get_daily_checklist_service),
):
    checklist = await service.get_checklist(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found.")
    return checklist


@router.post("/generate", status_code=201)
async def generate_daily_checklist(
    body: GenerateChecklistRequest,
    current_user: User = Depends(get_current_user),
    service: DailyChecklistService = Depends(get_daily_checklist_service),
):
    try:
        return await service.generate_from_template(
            template_id=body.template_id,
            branch_id=body.branch_id,
            date=body.date,
            group_ids=body.group_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{checklist_id}/items/{item_index}")
async def update_checklist_item(
    checklist_id: str,
    item_index: int,
    body: ChecklistItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: DailyChecklistService = Depends(get_daily_checklist_service),
):
    try:
        return await service.update_checklist_item(
            checklist_id=checklist_id,
            item_index=item_index,
            user_id=current_user.id,
            is_completed=body.is_completed,
            verification_data=body.verification_data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
