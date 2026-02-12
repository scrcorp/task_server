from supabase import Client
from typing import List, Optional
from app.models.enums import TaskStatus

# --- 업무 (Task) 관련 CRUD ---

def get_tasks(db: Client, type: Optional[str] = None, assigned_to: Optional[str] = None):
    """
    업무 목록을 조회합니다.
    필터링 조건: 업무 유형(daily/assigned), 담당자 ID
    """
    query = db.table("tasks").select("*, checklist:checklist_items(*), comments(*)")
    
    if type:
        query = query.eq("type", type)
    if assigned_to:
        query = query.eq("assigned_to", assigned_to)
        
    result = query.execute()
    return result.data

def get_task(db: Client, task_id: str):
    """특정 ID의 업무 상세 정보를 조회합니다 (체크리스트, 댓글 포함)"""
    result = db.table("tasks").select("*, checklist:checklist_items(*), comments(*)").eq("id", task_id).single().execute()
    return result.data

def create_task(db: Client, task_data: dict):
    """새로운 업무를 생성합니다."""
    result = db.table("tasks").insert(task_data).execute()
    return result.data

def update_task(db: Client, task_id: str, task_data: dict):
    """업무의 정보를 수정합니다 (제목, 설명 등)."""
    result = db.table("tasks").update(task_data).eq("id", task_id).execute()
    return result.data

def delete_task(db: Client, task_id: str):
    """특정 업무를 삭제합니다."""
    result = db.table("tasks").delete().eq("id", task_id).execute()
    return result.data

def update_task_status(db: Client, task_id: str, status: TaskStatus):
    """업무의 상태(시작 전, 진행 중, 완료)를 변경합니다."""
    result = db.table("tasks").update({"status": status}).eq("id", task_id).execute()
    return result.data

# --- 체크리스트 (Checklist) 관련 CRUD ---

def toggle_checklist_item(db: Client, item_id: str, is_completed: bool):
    """체크리스트 항목의 완료 여부를 토글합니다."""
    result = db.table("checklist_items").update({"is_completed": is_completed}).eq("id", item_id).execute()
    return result.data

# --- 공지사항 (Notice) 관련 CRUD ---

def get_notices(db: Client):
    """최신 공지사항 목록을 조회합니다."""
    result = db.table("notices").select("*").order("created_at", desc=True).execute()
    return result.data

def get_notice(db: Client, notice_id: str):
    """특정 공지사항의 상세 내용을 조회합니다."""
    result = db.table("notices").select("*").eq("id", notice_id).single().execute()
    return result.data
