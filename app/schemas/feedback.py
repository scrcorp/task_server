from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackBase(BaseModel):
    content: str
    assignment_id: Optional[str] = None
    branch_id: Optional[str] = None
    target_user_id: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: str
    company_id: str
    author_id: str
    status: Optional[str] = None
    created_at: datetime

    class Config: from_attributes = True
