from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class IAttendanceRepository(ABC):
    @abstractmethod
    async def clock_in(self, data: dict) -> dict: pass
    @abstractmethod
    async def clock_out(self, record_id: str, data: dict) -> dict: pass
    @abstractmethod
    async def get_today_record(self, user_id: str, company_id: str, date: str) -> Optional[dict]: pass
    @abstractmethod
    async def get_history(self, user_id: str, company_id: str, year: int, month: int) -> List[dict]: pass


class AttendanceRepository(IAttendanceRepository):
    def __init__(self):
        self.table = "attendance"

    async def clock_in(self, data: dict) -> dict:
        res = supabase.table(self.table).insert(data).execute()
        return res.data[0]

    async def clock_out(self, record_id: str, data: dict) -> dict:
        res = supabase.table(self.table).update(data).eq("id", record_id).execute()
        return res.data[0]

    async def get_today_record(self, user_id: str, company_id: str, date: str) -> Optional[dict]:
        query = (
            supabase.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .eq("company_id", company_id)
        )
        # clock_in can be NULL now, so filter by created_at or use date-based approach
        # Use gte/lte on the record creation window for the day
        res = (
            query
            .gte("clock_in", f"{date}T00:00:00")
            .lte("clock_in", f"{date}T23:59:59")
            .maybe_single()
            .execute()
        )
        return res.data if res else None

    async def get_history(self, user_id: str, company_id: str, year: int, month: int) -> List[dict]:
        start = f"{year}-{month:02d}-01T00:00:00"
        if month == 12:
            end = f"{year + 1}-01-01T00:00:00"
        else:
            end = f"{year}-{month + 1:02d}-01T00:00:00"

        res = (
            supabase.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .eq("company_id", company_id)
            .gte("clock_in", start)
            .lt("clock_in", end)
            .order("clock_in", desc=True)
            .execute()
        )
        return res.data
