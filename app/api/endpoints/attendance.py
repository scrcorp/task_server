from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import date
from app.schemas.attendance import AttendanceRecord, ClockInRequest, AttendanceHistoryResponse
from app.services.attendance_service import AttendanceService
from app.core.dependencies import get_attendance_repo
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


def _get_service() -> AttendanceService:
    return AttendanceService(attendance_repo=get_attendance_repo())


@router.get("/today", response_model=Optional[AttendanceRecord])
async def get_today_status(current_user: User = Depends(get_current_user)):
    service = _get_service()
    return await service.get_today_status(current_user.id)


@router.post("/clock-in", response_model=AttendanceRecord, status_code=201)
async def clock_in(body: ClockInRequest, current_user: User = Depends(get_current_user)):
    service = _get_service()
    try:
        return await service.clock_in(current_user.id, body.location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clock-out", response_model=AttendanceRecord)
async def clock_out(current_user: User = Depends(get_current_user)):
    service = _get_service()
    try:
        return await service.clock_out(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=AttendanceHistoryResponse)
async def get_history(
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    service = _get_service()
    today = date.today()
    y = year or today.year
    m = month or today.month
    return await service.get_monthly_history(current_user.id, y, m)
