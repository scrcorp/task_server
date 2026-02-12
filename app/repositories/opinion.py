from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class IOpinionRepository(ABC):
    @abstractmethod
    async def create(self, data: dict) -> dict: pass

    @abstractmethod
    async def list_by_user(self, user_id: str) -> List[dict]: pass

    @abstractmethod
    async def list_all(self, status: Optional[str] = None) -> List[dict]: pass

    @abstractmethod
    async def update_status(self, opinion_id: str, status: str) -> dict: pass


class OpinionRepository(IOpinionRepository):
    def __init__(self):
        self.table = "opinions"

    async def create(self, data: dict) -> dict:
        res = supabase.table(self.table).insert(data).execute()
        return res.data[0]

    async def list_by_user(self, user_id: str) -> List[dict]:
        res = (
            supabase.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data

    async def list_all(self, status: Optional[str] = None) -> List[dict]:
        query = supabase.table(self.table).select("*").order("created_at", desc=True)
        if status:
            query = query.eq("status", status)
        res = query.execute()
        return res.data

    async def update_status(self, opinion_id: str, status: str) -> dict:
        res = (
            supabase.table(self.table)
            .update({"status": status})
            .eq("id", opinion_id)
            .execute()
        )
        return res.data[0]
