from pydantic import BaseModel
from datetime import datetime


class Opinion(BaseModel):
    id: str
    user_id: str
    content: str
    status: str = "submitted"  # submitted, reviewed, resolved
    created_at: datetime

    class Config:
        from_attributes = True


class OpinionCreate(BaseModel):
    content: str
