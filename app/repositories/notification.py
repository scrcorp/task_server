from abc import ABC, abstractmethod
from typing import List
from app.core.supabase import supabase


class INotificationRepository(ABC):
    @abstractmethod
    async def list_by_user(self, user_id: str, limit: int = 50) -> List[dict]: pass

    @abstractmethod
    async def count_unread(self, user_id: str) -> int: pass

    @abstractmethod
    async def mark_as_read(self, notification_id: str, user_id: str) -> dict: pass

    @abstractmethod
    async def mark_all_as_read(self, user_id: str) -> int: pass

    @abstractmethod
    async def create(self, data: dict) -> dict: pass


class NotificationRepository(INotificationRepository):
    def __init__(self):
        self.table = "notifications"

    async def list_by_user(self, user_id: str, limit: int = 50) -> List[dict]:
        res = (
            supabase.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data

    async def count_unread(self, user_id: str) -> int:
        res = (
            supabase.table(self.table)
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        return res.count or 0

    async def mark_as_read(self, notification_id: str, user_id: str) -> dict:
        res = (
            supabase.table(self.table)
            .update({"is_read": True})
            .eq("id", notification_id)
            .eq("user_id", user_id)
            .execute()
        )
        return res.data[0] if res.data else {}

    async def mark_all_as_read(self, user_id: str) -> int:
        res = (
            supabase.table(self.table)
            .update({"is_read": True})
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        return len(res.data) if res.data else 0

    async def create(self, data: dict) -> dict:
        res = supabase.table(self.table).insert(data).execute()
        return res.data[0]
