from pydantic import BaseModel
from datetime import datetime


class Opinion(BaseModel):
    id: str
    company_id: str
    user_id: str
    content: str
    status: str = "submitted"
    created_at: datetime

    class Config: from_attributes = True


class OpinionCreate(BaseModel):
    content: str
