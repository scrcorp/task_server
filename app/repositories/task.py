from typing import List, Optional, Any
from app.repositories.base import IRepository
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.core.supabase import supabase

class TaskRepository(IRepository[Task]):
    def __init__(self):
        self.table = "tasks"

    async def get_by_id(self, id: str) -> Optional[Task]:
        res = supabase.table(self.table).select("*, checklist:checklist_items(*), comments(*)").eq("id", id).maybe_single().execute()
        if res.data:
            return Task(**res.data)
        return None

    async def list(self, filters: Optional[dict] = None) -> List[Task]:
        query = supabase.table(self.table).select("*, checklist:checklist_items(*), comments(*)")
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.eq(key, value)
        res = query.execute()
        return [Task(**item) for item in res.data]

    async def create(self, data: Any) -> Task:
        res = supabase.table(self.table).insert(data).execute()
        return Task(**res.data[0])

    async def update(self, id: str, data: dict) -> Task:
        res = supabase.table(self.table).update(data).eq("id", id).execute()
        # Refresh to get full object with joins if needed
        return await self.get_by_id(id)

    async def delete(self, id: str) -> bool:
        supabase.table(self.table).delete().eq("id", id).execute()
        return True

    # Checklist specific
    async def update_checklist_item(self, item_id: str, data: dict) -> dict:
        res = supabase.table("checklist_items").update(data).eq("id", item_id).execute()
        return res.data[0]

    async def create_checklist_log(self, log_data: dict) -> dict:
        res = supabase.table("checklist_logs").insert(log_data).execute()
        return res.data[0]
