from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.organization import Company, Brand, Branch, GroupType, Group
from app.core.supabase import supabase


class IOrganizationRepository(ABC):
    # Company
    @abstractmethod
    async def get_company_by_id(self, id: str) -> Optional[Company]: pass
    @abstractmethod
    async def get_company_by_code(self, code: str) -> Optional[Company]: pass
    @abstractmethod
    async def create_company(self, data: dict) -> Company: pass
    @abstractmethod
    async def update_company(self, id: str, data: dict) -> Company: pass

    # Brand
    @abstractmethod
    async def list_brands(self, company_id: str) -> List[Brand]: pass
    @abstractmethod
    async def create_brand(self, data: dict) -> Brand: pass
    @abstractmethod
    async def update_brand(self, id: str, data: dict) -> Brand: pass
    @abstractmethod
    async def delete_brand(self, id: str) -> bool: pass

    # Branch
    @abstractmethod
    async def list_branches(self, brand_id: Optional[str] = None) -> List[Branch]: pass
    @abstractmethod
    async def create_branch(self, data: dict) -> Branch: pass
    @abstractmethod
    async def delete_branch(self, id: str) -> bool: pass

    # GroupType
    @abstractmethod
    async def list_group_types(self, branch_id: str) -> List[GroupType]: pass
    @abstractmethod
    async def create_group_type(self, data: dict) -> GroupType: pass
    @abstractmethod
    async def delete_group_type(self, id: str) -> bool: pass

    # Group
    @abstractmethod
    async def list_groups(self, group_type_id: Optional[str] = None) -> List[Group]: pass
    @abstractmethod
    async def create_group(self, data: dict) -> Group: pass
    @abstractmethod
    async def delete_group(self, id: str) -> bool: pass


class OrganizationRepository(IOrganizationRepository):

    # ── Company ─────────────────────────────────────
    async def get_company_by_id(self, id: str) -> Optional[Company]:
        res = supabase.table("companies").select("*").eq("id", id).maybe_single().execute()
        return Company(**res.data) if res and res.data else None

    async def get_company_by_code(self, code: str) -> Optional[Company]:
        res = supabase.table("companies").select("*").eq("code", code).maybe_single().execute()
        return Company(**res.data) if res and res.data else None

    async def create_company(self, data: dict) -> Company:
        res = supabase.table("companies").insert(data).execute()
        return Company(**res.data[0])

    async def update_company(self, id: str, data: dict) -> Company:
        res = supabase.table("companies").update(data).eq("id", id).execute()
        return Company(**res.data[0])

    # ── Brand ───────────────────────────────────────
    async def list_brands(self, company_id: str) -> List[Brand]:
        res = supabase.table("brands").select("*").eq("company_id", company_id).execute()
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

    # ── Branch ──────────────────────────────────────
    async def list_branches(self, brand_id: Optional[str] = None) -> List[Branch]:
        query = supabase.table("branches").select("*")
        if brand_id:
            query = query.eq("brand_id", brand_id)
        res = query.execute()
        return [Branch(**item) for item in res.data]

    async def create_branch(self, data: dict) -> Branch:
        res = supabase.table("branches").insert(data).execute()
        return Branch(**res.data[0])

    async def delete_branch(self, id: str) -> bool:
        supabase.table("branches").delete().eq("id", id).execute()
        return True

    # ── GroupType ────────────────────────────────────
    async def list_group_types(self, branch_id: str) -> List[GroupType]:
        res = (
            supabase.table("group_types")
            .select("*")
            .eq("branch_id", branch_id)
            .order("priority")
            .execute()
        )
        return [GroupType(**item) for item in res.data]

    async def create_group_type(self, data: dict) -> GroupType:
        res = supabase.table("group_types").insert(data).execute()
        return GroupType(**res.data[0])

    async def delete_group_type(self, id: str) -> bool:
        supabase.table("group_types").delete().eq("id", id).execute()
        return True

    # ── Group ───────────────────────────────────────
    async def list_groups(self, group_type_id: Optional[str] = None) -> List[Group]:
        query = supabase.table("groups").select("*")
        if group_type_id:
            query = query.eq("group_type_id", group_type_id)
        res = query.execute()
        return [Group(**item) for item in res.data]

    async def create_group(self, data: dict) -> Group:
        res = supabase.table("groups").insert(data).execute()
        return Group(**res.data[0])

    async def delete_group(self, id: str) -> bool:
        supabase.table("groups").delete().eq("id", id).execute()
        return True
