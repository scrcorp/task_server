from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Notification(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: List[Notification]
