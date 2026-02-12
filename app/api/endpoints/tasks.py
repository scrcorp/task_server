from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.task import Task, TaskCreate, TaskUpdate, Comment
from app.services.task_service import TaskService
from app.services.comment_service import CommentService
from app.models.enums import TaskStatus
from app.core.security import get_current_user
from app.core.dependencies import get_task_service, get_comment_service
from app.schemas.user import User

router = APIRouter()


# ── Request Schemas ──────────────────────────────────

class ChecklistItemCreateRequest(BaseModel):
    content: str
    verification_type: str = "none"

class CommentCreateRequest(BaseModel):
    content: str


# ── Task CRUD ────────────────────────────────────────

@router.get("/", response_model=List[Task])
async def read_tasks(
    type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    try:
        filters = {}
        if type:
            filters["type"] = type
        if assigned_to:
            filters["assigned_to"] = assigned_to
        else:
            filters["assigned_to"] = current_user.id
        return await service.task_repo.list(filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    task = await service.task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
    return task


@router.post("/", response_model=Task, status_code=201)
async def create_task(
    body: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    try:
        data = body.model_dump()
        if not data.get("assigned_to"):
            data["assigned_to"] = current_user.id
        return await service.task_repo.create(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    body: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    try:
        data = body.model_dump(exclude_unset=True)
        return await service.task_repo.update(task_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    try:
        await service.task_repo.delete(task_id)
        return {"message": "업무가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{task_id}/status")
async def update_task_status(
    task_id: str,
    status: TaskStatus,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    try:
        return await service.task_repo.update(task_id, {"status": status.value})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Checklist ────────────────────────────────────────

@router.patch("/checklist/{item_id}")
async def update_checklist_item(
    item_id: str,
    is_completed: bool,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """체크리스트 항목 상태를 변경하고 서버 내부 로그를 자동 저장합니다."""
    try:
        updated_item = await service.update_checklist_item(current_user.id, item_id, is_completed)
        return {"message": "체크리스트 상태가 변경되고 로그가 저장되었습니다.", "data": updated_item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/checklist", status_code=201)
async def create_checklist_item(
    task_id: str,
    body: ChecklistItemCreateRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """체크리스트 항목을 추가합니다."""
    try:
        item = await service.create_checklist_item(task_id, body.content)
        return {"message": "체크리스트 항목이 추가되었습니다.", "data": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/checklist/{item_id}")
async def delete_checklist_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """체크리스트 항목을 삭제합니다."""
    try:
        await service.delete_checklist_item(item_id)
        return {"message": "체크리스트 항목이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Comments ─────────────────────────────────────────

@router.get("/{task_id}/comments", response_model=List[Comment])
async def list_comments(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    """특정 업무의 댓글 목록을 반환합니다."""
    try:
        return await service.list_comments(task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/comments", status_code=201)
async def create_comment(
    task_id: str,
    body: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    """특정 업무에 댓글을 추가합니다."""
    try:
        return await service.create_comment(task_id, current_user.id, body.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}/comments/{comment_id}")
async def delete_comment(
    task_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    """댓글을 삭제합니다."""
    try:
        await service.delete_comment(comment_id)
        return {"message": "댓글이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
