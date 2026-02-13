from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.enums import AttendanceStatus


class AttendanceRecord(BaseModel):
    id: str
    user_id: str
    clock_in: datetime
    clock_out: Optional[datetime] = None
    location: Optional[str] = None
    status: AttendanceStatus = AttendanceStatus.NOT_STARTED
    work_hours: Optional[float] = None

    class Config:
        from_attributes = True


class ClockInRequest(BaseModel):
    location: Optional[str] = None


class AttendanceHistoryResponse(BaseModel):
    month: str
    records: List[dict]
    summary: dict
