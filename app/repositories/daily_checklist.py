from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class IDailyChecklistRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[dict]: pass
    @abstractmethod
    async def list_by_branch_date(self, branch_id: str, date: str) -> List[dict]: pass
    @abstractmethod
    async def create(self, data: dict) -> dict: pass
    @abstractmethod
    async def update_checklist_data(self, id: str, checklist_data: list) -> dict: pass


class DailyChecklistRepository(IDailyChecklistRepository):
    def __init__(self):
        self.table = "daily_checklists"

    async def get_by_id(self, id: str) -> Optional[dict]:
        res = supabase.table(self.table).select("*").eq("id", id).maybe_single().execute()
        return res.data if res else None

    async def list_by_branch_date(self, branch_id: str, date: str) -> List[dict]:
        res = (
            supabase.table(self.table)
            .select("*")
            .eq("branch_id", branch_id)
            .eq("date", date)
            .execute()
        )
        return res.data

    async def get_by_template_branch_date(self, template_id: str, branch_id: str, date: str) -> Optional[dict]:
        res = (
            supabase.table(self.table)
            .select("*")
            .eq("template_id", template_id)
            .eq("branch_id", branch_id)
            .eq("date", date)
            .maybe_single()
            .execute()
        )
        return res.data if res else None

    async def create(self, data: dict) -> dict:
        res = supabase.table(self.table).insert(data).execute()
        return res.data[0]

    async def update_checklist_data(self, id: str, checklist_data: list) -> dict:
        res = (
            supabase.table(self.table)
            .update({"checklist_data": checklist_data})
            .eq("id", id)
            .execute()
        )
        return res.data[0]
