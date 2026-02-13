from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class IAssignmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[dict]: pass
    @abstractmethod
    async def list(self, filters: dict) -> List[dict]: pass
    @abstractmethod
    async def create(self, data: dict) -> dict: pass
    @abstractmethod
    async def update(self, id: str, data: dict) -> dict: pass
    @abstractmethod
    async def delete(self, id: str) -> bool: pass
    @abstractmethod
    async def add_assignees(self, assignment_id: str, user_ids: List[str]) -> List[dict]: pass
    @abstractmethod
    async def remove_assignee(self, assignment_id: str, user_id: str) -> bool: pass
    @abstractmethod
    async def get_assignees(self, assignment_id: str) -> List[dict]: pass


class AssignmentRepository(IAssignmentRepository):
    def __init__(self):
        self.table = "assignments"

    async def get_by_id(self, id: str) -> Optional[dict]:
        res = (
            supabase.table(self.table)
            .select("*, assignees:assignment_assignees(*), comments(*)")
            .eq("id", id)
            .maybe_single()
            .execute()
        )
        return res.data if res else None

    async def list(self, filters: dict) -> List[dict]:
        query = supabase.table(self.table).select("*, assignees:assignment_assignees(*)")
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        res = query.order("created_at", desc=True).execute()
        return res.data

    async def list_by_assignee(self, user_id: str, company_id: str) -> List[dict]:
        assignee_res = (
            supabase.table("assignment_assignees")
            .select("assignment_id")
            .eq("user_id", user_id)
            .execute()
        )
        if not assignee_res.data:
            return []
        assignment_ids = [a["assignment_id"] for a in assignee_res.data]
        res = (
            supabase.table(self.table)
            .select("*, assignees:assignment_assignees(*)")
            .eq("company_id", company_id)
            .in_("id", assignment_ids)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data

    async def create(self, data: dict) -> dict:
        res = supabase.table(self.table).insert(data).execute()
        return res.data[0]

    async def update(self, id: str, data: dict) -> dict:
        res = supabase.table(self.table).update(data).eq("id", id).execute()
        return res.data[0]

    async def delete(self, id: str) -> bool:
        supabase.table(self.table).delete().eq("id", id).execute()
        return True

    async def add_assignees(self, assignment_id: str, user_ids: List[str]) -> List[dict]:
        rows = [{"assignment_id": assignment_id, "user_id": uid} for uid in user_ids]
        res = supabase.table("assignment_assignees").insert(rows).execute()
        return res.data

    async def remove_assignee(self, assignment_id: str, user_id: str) -> bool:
        supabase.table("assignment_assignees").delete().eq("assignment_id", assignment_id).eq("user_id", user_id).execute()
        return True

    async def get_assignees(self, assignment_id: str) -> List[dict]:
        res = supabase.table("assignment_assignees").select("*").eq("assignment_id", assignment_id).execute()
        return res.data
