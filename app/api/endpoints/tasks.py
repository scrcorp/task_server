from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from app.models.enums import TaskStatus
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()
task_service = TaskService()

@router.get("/", response_model=List[Task])
async def read_tasks(
    type: Optional[str] = None, 
    assigned_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    try:
        filters = {}
        if type: filters["type"] = type
        if assigned_to: 
            filters["assigned_to"] = assigned_to
        else:
            # By default, only show tasks for current user if not specified
            filters["assigned_to"] = current_user.id
            
        return await task_service.task_repo.list(filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=Task)
async def read_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = await task_service.task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
    return task

@router.patch("/checklist/{item_id}")
async def update_checklist_item(
    item_id: str, 
    is_completed: bool, 
    current_user: User = Depends(get_current_user)
):
    """
    체크리스트 항목 상태를 변경하고 서버 내부 로그를 자동 저장합니다.
    """
    try:
        updated_item = await task_service.update_checklist_item(current_user.id, item_id, is_completed)
        return {"message": "체크리스트 상태가 변경되고 로그가 저장되었습니다.", "data": updated_item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ... other endpoints follow similar pattern using task_service.task_repo
