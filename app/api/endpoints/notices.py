from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas.notice import Notice
from app.repositories.feedback_notice import NoticeRepository
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()
notice_repo = NoticeRepository()

@router.get("/", response_model=List[Notice])
async def read_notices(limit: Optional[int] = None):
    try:
        return await notice_repo.list_notices(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notice_id}")
async def read_notice(notice_id: str):
    notice = await notice_repo.get_notice(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")
    return notice

@router.post("/{notice_id}/confirm")
async def confirm_notice(notice_id: str, current_user: User = Depends(get_current_user)):
    try:
        return await notice_repo.confirm_notice(notice_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
