from typing import List, Optional, Any
from app.repositories.base import IRepository
from app.schemas.user import User
from app.core.supabase import supabase


class SupabaseUserRepository(IRepository[User]):
    def __init__(self):
        self.table = "users"

    async def get_by_id(self, id: str) -> Optional[User]:
        res = supabase.table(self.table).select("*").eq("id", id).maybe_single().execute()
        if res.data:
            return User(**res.data)
        return None

    async def get_by_login_id(self, login_id: str) -> Optional[User]:
        res = supabase.table(self.table).select("*").eq("login_id", login_id).maybe_single().execute()
        if res.data:
            return User(**res.data)
        return None

    async def list(self, filters: Optional[dict] = None) -> List[User]:
        query = supabase.table(self.table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        res = query.execute()
        return [User(**item) for item in res.data]

    async def create(self, data: Any) -> User:
        res = supabase.table(self.table).insert(data).execute()
        return User(**res.data[0])

    async def update(self, id: str, data: dict) -> User:
        res = supabase.table(self.table).update(data).eq("id", id).execute()
        return User(**res.data[0])

    async def delete(self, id: str) -> bool:
        supabase.table(self.table).delete().eq("id", id).execute()
        return True
