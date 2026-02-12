from abc import ABC, abstractmethod
from typing import List, Optional, Any
from app.repositories.base import IRepository
from app.schemas.organization import Brand, Branch, Group
from app.core.supabase import supabase


class IOrganizationRepository(ABC):
    @abstractmethod
    async def list_brands(self) -> List[Brand]: pass

    @abstractmethod
    async def create_brand(self, data: dict) -> Brand: pass

    @abstractmethod
    async def update_brand(self, id: str, data: dict) -> Brand: pass

    @abstractmethod
    async def delete_brand(self, id: str) -> bool: pass

    @abstractmethod
    async def list_branches(self, brand_id: Optional[str] = None) -> List[Branch]: pass

    @abstractmethod
    async def create_branch(self, data: dict) -> Branch: pass

    @abstractmethod
    async def delete_branch(self, id: str) -> bool: pass

    @abstractmethod
    async def list_groups(self, branch_id: Optional[str] = None) -> List[Group]: pass

    @abstractmethod
    async def create_group(self, data: dict) -> Group: pass

    @abstractmethod
    async def delete_group(self, id: str) -> bool: pass


class OrganizationRepository(IOrganizationRepository):
    """Handles Brands, Branches, and Groups."""
    
    # Brands
    async def list_brands(self) -> List[Brand]:
        res = supabase.table("brands").select("*").execute()
        return [Brand(**item) for item in res.data]
    
    async def create_brand(self, data: dict) -> Brand:
        res = supabase.table("brands").insert(data).execute()
        return Brand(**res.data[0])

    async def update_brand(self, id: str, data: dict) -> Brand:
        res = supabase.table("brands").update(data).eq("id", id).execute()
        return Brand(**res.data[0])

    async def delete_brand(self, id: str) -> bool:
        supabase.table("brands").delete().eq("id", id).execute()
        return True

    # Branches
    async def delete_branch(self, id: str) -> bool:
        supabase.table("branches").delete().eq("id", id).execute()
        return True

    async def list_branches(self, brand_id: Optional[str] = None) -> List[Branch]:
        query = supabase.table("branches").select("*")
        if brand_id:
            query = query.eq("brand_id", brand_id)
        res = query.execute()
        return [Branch(**item) for item in res.data]
    
    async def create_branch(self, data: dict) -> Branch:
        res = supabase.table("branches").insert(data).execute()
        return Branch(**res.data[0])

    # Groups
    async def list_groups(self, branch_id: Optional[str] = None) -> List[Group]:
        query = supabase.table("groups").select("*")
        if branch_id:
            query = query.eq("branch_id", branch_id)
        res = query.execute()
        return [Group(**item) for item in res.data]
    
    async def create_group(self, data: dict) -> Group:
        res = supabase.table("groups").insert(data).execute()
        return Group(**res.data[0])

    async def delete_group(self, id: str) -> bool:
        supabase.table("groups").delete().eq("id", id).execute()
        return True
