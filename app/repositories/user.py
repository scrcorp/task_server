from typing import List, Optional, Any
from app.repositories.base import IRepository
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.supabase import supabase

class SupabaseUserRepository(IRepository[User]):
    def __init__(self):
        self.table = "user_profiles" # Assuming user profiles table linked to auth.users

    async def get_by_id(self, id: str) -> Optional[User]:
        res = supabase.table(self.table).select("*").eq("id", id).maybe_single().execute()
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
        # User creation usually happens via Auth service, 
        # but this repository handles the profile part.
        res = supabase.table(self.table).insert(data).execute()
        return User(**res.data[0])

    async def update(self, id: str, data: dict) -> User:
        res = supabase.table(self.table).update(data).eq("id", id).execute()
        return User(**res.data[0])

    async def delete(self, id: str) -> bool:
        res = supabase.table(self.table).delete().eq("id", id).execute()
        return True
