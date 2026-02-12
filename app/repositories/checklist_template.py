from typing import List, Optional, Any
from app.core.supabase import supabase

class ChecklistTemplateRepository:
    async def list_templates(self, brand_id: Optional[str] = None, group_id: Optional[str] = None) -> List[dict]:
        query = supabase.table("checklist_templates").select("*, items:checklist_template_items(*)")
        if brand_id:
            query = query.eq("brand_id", brand_id)
        if group_id:
            query = query.eq("group_id", group_id)
        res = query.execute()
        return res.data

    async def get_template_by_id(self, id: str) -> Optional[dict]:
        res = supabase.table("checklist_templates").select("*, items:checklist_template_items(*)").eq("id", id).maybe_single().execute()
        return res.data

    async def create_template(self, data: dict) -> dict:
        items = data.pop("items", [])
        res = supabase.table("checklist_templates").insert(data).execute()
        template = res.data[0]
        
        if items:
            for item in items:
                item["template_id"] = template["id"]
            supabase.table("checklist_template_items").insert(items).execute()
            
        return await self.get_template_by_id(template["id"])

    async def update_template(self, id: str, data: dict) -> dict:
        res = supabase.table("checklist_templates").update(data).eq("id", id).execute()
        return res.data[0]

    async def delete_template(self, id: str) -> bool:
        supabase.table("checklist_templates").delete().eq("id", id).execute()
        return True
