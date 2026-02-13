from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime


class ChecklistItemData(BaseModel):
    item_id: str
    content: str
    verification_type: str = "none"
    is_completed: bool = False
    completed_by: Optional[str] = None
    completed_at: Optional[str] = None
    verification_data: Optional[str] = None


class DailyChecklistBase(BaseModel):
    template_id: str
    branch_id: str
    date: date
    checklist_data: List[ChecklistItemData]
    group_ids: Optional[List[str]] = None


class DailyChecklistCreate(BaseModel):
    template_id: str
    branch_id: str
    date: date
    group_ids: Optional[List[str]] = None


class DailyChecklist(DailyChecklistBase):
    id: str
    created_at: datetime

    class Config: from_attributes = True


class ChecklistItemUpdate(BaseModel):
    is_completed: bool
    verification_data: Optional[str] = None
