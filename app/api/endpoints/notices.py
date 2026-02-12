from fastapi import APIRouter, HTTPException
from typing import List
from app.core.supabase import supabase
from app.schemas.notice import Notice
from app.crud import task as crud_task

router = APIRouter()

@router.get("/", response_model=List[Notice])
def read_notices():
    """전체 공지사항 목록을 가져옵니다."""
    try:
        notices = crud_task.get_notices(supabase)
        return notices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notice_id}", response_model=Notice)
def read_notice(notice_id: str):
    """특정 공지사항의 상세 내용을 가져옵니다."""
    try:
        notice = crud_task.get_notice(supabase, notice_id)
        if not notice:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")
        return notice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
