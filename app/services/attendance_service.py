from typing import Optional
from datetime import datetime, date
from app.repositories.attendance import IAttendanceRepository
from app.schemas.attendance import AttendanceRecord, AttendanceHistoryResponse


class AttendanceService:
    def __init__(self, attendance_repo: IAttendanceRepository):
        self.attendance_repo = attendance_repo

    async def get_today_status(self, user_id: str) -> Optional[AttendanceRecord]:
        today = date.today().isoformat()
        record = await self.attendance_repo.get_today_record(user_id, today)
        if record:
            return AttendanceRecord(**record)
        return None

    async def clock_in(self, user_id: str, location: Optional[str] = None) -> AttendanceRecord:
        today = date.today().isoformat()
        existing = await self.attendance_repo.get_today_record(user_id, today)
        if existing:
            raise ValueError("이미 출근 기록이 있습니다.")

        data = {
            "user_id": user_id,
            "clock_in": datetime.utcnow().isoformat(),
            "status": "on_duty",
        }
        if location:
            data["location"] = location

        record = await self.attendance_repo.clock_in(data)
        return AttendanceRecord(**record)

    async def clock_out(self, user_id: str) -> AttendanceRecord:
        today = date.today().isoformat()
        existing = await self.attendance_repo.get_today_record(user_id, today)
        if not existing:
            raise ValueError("출근 기록이 없습니다.")
        if existing.get("clock_out"):
            raise ValueError("이미 퇴근 기록이 있습니다.")

        clock_out_time = datetime.utcnow()
        clock_in_time = datetime.fromisoformat(existing["clock_in"].replace("Z", "+00:00").replace("+00:00", ""))
        work_hours = round((clock_out_time - clock_in_time).total_seconds() / 3600, 2)

        data = {
            "clock_out": clock_out_time.isoformat(),
            "status": "completed",
        }
        record = await self.attendance_repo.clock_out(existing["id"], data)
        result = AttendanceRecord(**record)
        result.work_hours = work_hours
        return result

    async def get_monthly_history(self, user_id: str, year: int, month: int) -> AttendanceHistoryResponse:
        records = await self.attendance_repo.get_history(user_id, year, month)

        total_days = len(records)
        completed = sum(1 for r in records if r.get("status") == "completed")

        return AttendanceHistoryResponse(
            month=f"{year}-{month:02d}",
            records=records,
            summary={
                "total_days": total_days,
                "completed": completed,
                "incomplete": total_days - completed,
            },
        )
