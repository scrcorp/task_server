from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas.notice import Notice, NoticeCreate
from app.services.notice_service import NoticeService
from app.core.dependencies import get_notice_repo
from app.core.security import get_current_user, require_role
from app.schemas.user import User, UserRole

router = APIRouter()


def _get_service() -> NoticeService:
    return NoticeService(notice_repo=get_notice_repo())


# ── Public endpoints ────────────────────────────────

@router.get("/", response_model=List[Notice])
async def read_notices(limit: Optional[int] = None):
    notice_repo = get_notice_repo()
    try:
        return await notice_repo.list_notices(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notice_id}")
async def read_notice(notice_id: str):
    notice_repo = get_notice_repo()
    notice = await notice_repo.get_notice(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")
    return notice


@router.post("/{notice_id}/confirm")
async def confirm_notice(notice_id: str, current_user: User = Depends(get_current_user)):
    notice_repo = get_notice_repo()
    try:
        return await notice_repo.confirm_notice(notice_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Admin CRUD endpoints ────────────────────────────

@router.post("/", response_model=dict, status_code=201)
async def create_notice(
    body: NoticeCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    service = _get_service()
    try:
        return await service.create_notice(body, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{notice_id}")
async def update_notice(
    notice_id: str,
    body: NoticeCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    service = _get_service()
    try:
        data = body.model_dump(exclude_unset=True)
        return await service.update_notice(notice_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notice_id}")
async def delete_notice(
    notice_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    service = _get_service()
    try:
        await service.delete_notice(notice_id)
        return {"message": "공지사항이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
