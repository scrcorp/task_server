from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TemplateItemBase(BaseModel):
    content: str
    verification_type: str = "none"
    sort_order: int = 0


class TemplateItemCreate(TemplateItemBase):
    pass


class TemplateItem(TemplateItemBase):
    id: str
    template_id: str
    class Config: from_attributes = True


class TemplateGroupMapping(BaseModel):
    id: str
    template_id: str
    group_id: str
    class Config: from_attributes = True


class ChecklistTemplateBase(BaseModel):
    name: str
    brand_id: Optional[str] = None
    branch_id: Optional[str] = None
    recurrence: dict = {"type": "daily"}
    is_active: bool = True


class ChecklistTemplateCreate(ChecklistTemplateBase):
    items: List[TemplateItemCreate] = []
    group_ids: List[str] = []


class ChecklistTemplateUpdate(BaseModel):
    name: Optional[str] = None
    brand_id: Optional[str] = None
    branch_id: Optional[str] = None
    recurrence: Optional[dict] = None
    is_active: Optional[bool] = None


class ChecklistTemplate(ChecklistTemplateBase):
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime
    items: List[TemplateItem] = []
    groups: List[TemplateGroupMapping] = []

    class Config: from_attributes = True
