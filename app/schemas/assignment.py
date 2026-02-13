from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from app.models.enums import Priority, AssignmentStatus, ContentType


# -- Assignment --

class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.NORMAL
    status: AssignmentStatus = AssignmentStatus.TODO
    due_date: Optional[datetime] = None
    branch_id: Optional[str] = None
    recurrence: Optional[dict] = None


class AssignmentCreate(AssignmentBase):
    assignee_ids: List[str] = Field(default_factory=list)


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AssignmentStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    branch_id: Optional[str] = None
    recurrence: Optional[dict] = None


class AssignmentAssignee(BaseModel):
    assignment_id: str
    user_id: str
    assigned_at: datetime
    class Config: from_attributes = True


class Assignment(AssignmentBase):
    id: str
    company_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    assignees: List[AssignmentAssignee] = []
    comments: List[Any] = []

    class Config: from_attributes = True


# -- Comment --

class CommentBase(BaseModel):
    content: Optional[str] = None
    content_type: ContentType = ContentType.TEXT
    attachments: Optional[List[dict]] = None


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: str
    assignment_id: str
    user_id: str
    user_name: Optional[str] = None
    is_manager: bool = False
    created_at: datetime

    class Config: from_attributes = True
