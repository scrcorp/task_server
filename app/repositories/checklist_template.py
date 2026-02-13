from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.supabase import supabase


class IChecklistTemplateRepository(ABC):
    @abstractmethod
    async def list_templates(self, company_id: str, branch_id: Optional[str] = None) -> List[dict]: pass
    @abstractmethod
    async def get_template_by_id(self, id: str) -> Optional[dict]: pass
    @abstractmethod
    async def create_template(self, data: dict) -> dict: pass
    @abstractmethod
    async def update_template(self, id: str, data: dict) -> dict: pass
    @abstractmethod
    async def delete_template(self, id: str) -> bool: pass


class ChecklistTemplateRepository(IChecklistTemplateRepository):

    async def list_templates(self, company_id: str, branch_id: Optional[str] = None) -> List[dict]:
        query = (
            supabase.table("checklist_templates")
            .select("*, items:template_items(*), groups:template_groups(*)")
            .eq("company_id", company_id)
        )
        if branch_id:
            query = query.eq("branch_id", branch_id)
        res = query.execute()
        return res.data

    async def get_template_by_id(self, id: str) -> Optional[dict]:
        res = (
            supabase.table("checklist_templates")
            .select("*, items:template_items(*), groups:template_groups(*)")
            .eq("id", id)
            .maybe_single()
            .execute()
        )
        return res.data

    async def create_template(self, data: dict) -> dict:
        items = data.pop("items", [])
        group_ids = data.pop("group_ids", [])

        res = supabase.table("checklist_templates").insert(data).execute()
        template = res.data[0]
        template_id = template["id"]

        if items:
            for item in items:
                item["template_id"] = template_id
            supabase.table("template_items").insert(items).execute()

        if group_ids:
            group_rows = [{"template_id": template_id, "group_id": gid} for gid in group_ids]
            supabase.table("template_groups").insert(group_rows).execute()

        return await self.get_template_by_id(template_id)

    async def update_template(self, id: str, data: dict) -> dict:
        res = supabase.table("checklist_templates").update(data).eq("id", id).execute()
        return res.data[0]

    async def delete_template(self, id: str) -> bool:
        supabase.table("checklist_templates").delete().eq("id", id).execute()
        return True
