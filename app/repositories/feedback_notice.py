from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class IFeedbackRepository(ABC):
    @abstractmethod
    async def create_feedback(self, data: dict) -> dict: pass
    @abstractmethod
    async def list_feedbacks(self, company_id: str, filters: dict) -> List[dict]: pass
    @abstractmethod
    async def update_feedback(self, id: str, data: dict) -> dict: pass


class FeedbackRepository(IFeedbackRepository):
    async def create_feedback(self, data: dict) -> dict:
        res = supabase.table("feedbacks").insert(data).execute()
        return res.data[0]

    async def list_feedbacks(self, company_id: str, filters: dict) -> List[dict]:
        query = supabase.table("feedbacks").select("*").eq("company_id", company_id)
        for key, value in filters.items():
            if value:
                query = query.eq(key, value)
        res = query.order("created_at", desc=True).execute()
        return res.data

    async def update_feedback(self, id: str, data: dict) -> dict:
        res = supabase.table("feedbacks").update(data).eq("id", id).execute()
        return res.data[0]


class INoticeRepository(ABC):
    @abstractmethod
    async def list_notices(self, company_id: str, limit: Optional[int] = None) -> List[dict]: pass
    @abstractmethod
    async def get_notice(self, id: str) -> Optional[dict]: pass
    @abstractmethod
    async def create_notice(self, data: dict) -> dict: pass
    @abstractmethod
    async def update_notice(self, notice_id: str, data: dict) -> dict: pass
    @abstractmethod
    async def delete_notice(self, notice_id: str) -> bool: pass
    @abstractmethod
    async def confirm_notice(self, notice_id: str, user_id: str) -> dict: pass


class NoticeRepository(INoticeRepository):
    async def list_notices(self, company_id: str, limit: Optional[int] = None) -> List[dict]:
        query = (
            supabase.table("notices")
            .select("*")
            .eq("company_id", company_id)
            .order("created_at", desc=True)
        )
        if limit:
            query = query.limit(limit)
        res = query.execute()
        return res.data

    async def get_notice(self, id: str) -> Optional[dict]:
        res = (
            supabase.table("notices")
            .select("*, confirmations:notice_confirmations(*)")
            .eq("id", id)
            .maybe_single()
            .execute()
        )
        return res.data if res else None

    async def create_notice(self, data: dict) -> dict:
        res = supabase.table("notices").insert(data).execute()
        return res.data[0]

    async def update_notice(self, notice_id: str, data: dict) -> dict:
        res = supabase.table("notices").update(data).eq("id", notice_id).execute()
        return res.data[0]

    async def delete_notice(self, notice_id: str) -> bool:
        supabase.table("notices").delete().eq("id", notice_id).execute()
        return True

    async def confirm_notice(self, notice_id: str, user_id: str) -> dict:
        res = supabase.table("notice_confirmations").insert({
            "notice_id": notice_id,
            "user_id": user_id,
        }).execute()
        return res.data[0]
