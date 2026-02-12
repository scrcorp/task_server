from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.core.supabase import supabase
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.crud import task as crud_task
from app.models.enums import TaskStatus

router = APIRouter()

@router.get("/", response_model=List[Task])
def read_tasks(type: Optional[str] = None, assigned_to: Optional[str] = None):
    """
    업무 리스트를 가져옵니다.
    - type: daily 또는 assigned 필터
    - assigned_to: 특정 직원에게 할당된 업무 필터
    """
    try:
        tasks = crud_task.get_tasks(supabase, type=type, assigned_to=assigned_to)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: str):
    """특정 업무의 상세 정보를 가져옵니다 (체크리스트 및 댓글 포함)."""
    try:
        task = crud_task.get_task(supabase, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Task)
def create_new_task(task: TaskCreate):
    """새로운 업무를 생성합니다."""
    try:
        new_task = crud_task.create_task(supabase, task.model_dump())
        return new_task[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{task_id}", response_model=Task)
def update_existing_task(task_id: str, task: TaskUpdate):
    """업무의 상세 정보를 수정합니다 (제목, 설명 등)."""
    try:
        updated_task = crud_task.update_task(supabase, task_id, task.model_dump(exclude_unset=True))
        if not updated_task:
            raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
        return updated_task[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
def delete_existing_task(task_id: str):
    """특정 업무를 삭제합니다."""
    try:
        crud_task.delete_task(supabase, task_id)
        return {"message": "업무가 성공적으로 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{task_id}/status")
def change_task_status(task_id: str, status: TaskStatus):
    """업무의 진행 상태만 별도로 변경합니다 (todo -> in_progress -> done)."""
    try:
        updated_task = crud_task.update_task_status(supabase, task_id, status)
        return {"message": "상태가 업데이트되었습니다.", "data": updated_task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/checklist/{item_id}")
def update_checklist_item(item_id: str, is_completed: bool):
    """체크리스트 항목의 완료 상태(V 체크)를 업데이트합니다."""
    try:
        updated_item = crud_task.toggle_checklist_item(supabase, item_id, is_completed)
        return {"message": "체크리스트 상태가 변경되었습니다.", "data": updated_item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
