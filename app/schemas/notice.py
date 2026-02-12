from pydantic import BaseModel, Field
from datetime import DateTime

class NoticeBase(BaseModel):
    title: str = Field(..., description="공지사항 제목")
    content: str = Field(..., description="공지사항 본문")

class NoticeCreate(NoticeBase):
    pass

class Notice(NoticeBase):
    id: str
    created_at: DateTime

    class Config:
        from_attributes = True
