from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas.notice import Notice, NoticeCreate
from app.services.notice_service import NoticeService
from app.core.dependencies import get_notice_service
from app.core.security import get_current_user, require_role
from app.schemas.user import User, UserRole

router = APIRouter()


# ── Public endpoints ────────────────────────────────

@router.get("/", response_model=List[Notice])
async def read_notices(
    limit: Optional[int] = None,
    service: NoticeService = Depends(get_notice_service),
):
    return await service.list_notices(limit=limit)


@router.get("/{notice_id}")
async def read_notice(
    notice_id: str,
    service: NoticeService = Depends(get_notice_service),
):
    notice = await service.get_notice(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")
    return notice


@router.post("/{notice_id}/confirm")
async def confirm_notice(
    notice_id: str,
    current_user: User = Depends(get_current_user),
    service: NoticeService = Depends(get_notice_service),
):
    return await service.confirm_notice(notice_id, current_user.id)


# ── Admin CRUD endpoints ────────────────────────────

@router.post("/", response_model=dict, status_code=201)
async def create_notice(
    body: NoticeCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    service: NoticeService = Depends(get_notice_service),
):
    return await service.create_notice(body, current_user.id)


@router.patch("/{notice_id}")
async def update_notice(
    notice_id: str,
    body: NoticeCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    service: NoticeService = Depends(get_notice_service),
):
    data = body.model_dump(exclude_unset=True)
    return await service.update_notice(notice_id, data)


@router.delete("/{notice_id}")
async def delete_notice(
    notice_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    service: NoticeService = Depends(get_notice_service),
):
    await service.delete_notice(notice_id)
    return {"message": "공지사항이 삭제되었습니다."}
