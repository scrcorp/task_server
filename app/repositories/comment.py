from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class ICommentRepository(ABC):
    @abstractmethod
    async def list_by_task(self, task_id: str) -> List[dict]: pass

    @abstractmethod
    async def create(self, data: dict) -> dict: pass

    @abstractmethod
    async def delete(self, id: str) -> bool: pass


class CommentRepository(ICommentRepository):
    def __init__(self):
        self.table = "comments"

    async def list_by_task(self, task_id: str) -> List[dict]:
        res = (
            supabase.table(self.table)
            .select("*")
            .eq("task_id", task_id)
            .order("created_at", desc=False)
            .execute()
        )
        return res.data

    async def create(self, data: dict) -> dict:
        res = supabase.table(self.table).insert(data).execute()
        return res.data[0]

    async def delete(self, id: str) -> bool:
        supabase.table(self.table).delete().eq("id", id).execute()
        return True
