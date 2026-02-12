from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.enums import TaskType, Priority, TaskStatus

# --- 체크리스트 (Checklist) 스키마 ---

class ChecklistItemBase(BaseModel):
    content: str = Field(..., description="체크리스트 내용")
    is_completed: bool = Field(False, description="완료 여부")
    verification_type: str = Field("none", description="검증 유형 (none, photo, signature)")
    verification_data: Optional[str] = Field(None, description="검증 데이터")

class ChecklistItemCreate(ChecklistItemBase):
    task_id: str

class ChecklistItem(ChecklistItemBase):
    id: str

    class Config:
        from_attributes = True

# --- 댓글 (Comment) 스키마 ---

class CommentBase(BaseModel):
    content: str = Field(..., description="댓글 내용")

class CommentCreate(CommentBase):
    task_id: str
    user_id: str

class Comment(CommentBase):
    id: str
    user_id: str
    user_name: Optional[str] = Field(None, description="작성자 이름")
    is_manager: bool = Field(False, description="관리자 여부")
    created_at: datetime

    class Config:
        from_attributes = True

# --- 업무 (Task) 스키마 ---

class TaskBase(BaseModel):
    title: str = Field(..., description="업무 제목")
    description: Optional[str] = Field(None, description="업무 상세 설명")
    type: TaskType = Field(..., description="업무 유형 (daily/assigned)")
    priority: Priority = Field(Priority.NORMAL, description="우선순위")
    status: TaskStatus = Field(TaskStatus.TODO, description="진행 상태")
    due_date: Optional[datetime] = Field(None, description="마감 기한")
    assigned_to: Optional[str] = Field(None, description="담당자 ID")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None

class Task(TaskBase):
    id: str
    created_at: datetime
    checklist: Optional[List[ChecklistItem]] = []
    comments: Optional[List[Comment]] = []

    class Config:
        from_attributes = True
