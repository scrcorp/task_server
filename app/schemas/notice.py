from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NoticeBase(BaseModel):
    title: str = Field(..., description="공지사항 제목")
    content: str = Field(..., description="공지사항 본문")
    is_important: bool = Field(False, description="중요 공지 여부")

class NoticeCreate(NoticeBase):
    pass

class Notice(NoticeBase):
    id: str
    author_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
