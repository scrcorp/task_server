from typing import List, Optional
from datetime import datetime
from app.repositories.daily_checklist import IDailyChecklistRepository
from app.repositories.checklist_template import IChecklistTemplateRepository


class DailyChecklistService:
    def __init__(
        self,
        checklist_repo: IDailyChecklistRepository,
        template_repo: IChecklistTemplateRepository,
    ):
        self.checklist_repo = checklist_repo
        self.template_repo = template_repo

    async def list_by_branch_date(self, branch_id: str, date: str) -> List[dict]:
        return await self.checklist_repo.list_by_branch_date(branch_id, date)

    async def get_checklist(self, checklist_id: str) -> Optional[dict]:
        return await self.checklist_repo.get_by_id(checklist_id)

    async def generate_from_template(
        self,
        template_id: str,
        branch_id: str,
        date: str,
        group_ids: Optional[List[str]] = None,
    ) -> dict:
        # Check if already exists
        existing = await self.checklist_repo.get_by_template_branch_date(template_id, branch_id, date)
        if existing:
            return existing

        # Get template with items
        template = await self.template_repo.get_template_by_id(template_id)
        if not template:
            raise ValueError("Template not found.")

        # Build JSONB checklist_data from template items
        items = template.get("items", [])
        checklist_data = []
        for item in items:
            checklist_data.append({
                "item_id": item["id"],
                "content": item["content"],
                "verification_type": item.get("verification_type", "none"),
                "is_completed": False,
                "completed_by": None,
                "completed_at": None,
                "verification_data": None,
            })

        data = {
            "template_id": template_id,
            "branch_id": branch_id,
            "date": date,
            "checklist_data": checklist_data,
            "group_ids": group_ids,
        }
        return await self.checklist_repo.create(data)

    async def update_checklist_item(
        self,
        checklist_id: str,
        item_index: int,
        user_id: str,
        is_completed: bool,
        verification_data: Optional[str] = None,
    ) -> dict:
        checklist = await self.checklist_repo.get_by_id(checklist_id)
        if not checklist:
            raise ValueError("Checklist not found.")

        items = checklist["checklist_data"]
        if item_index < 0 or item_index >= len(items):
            raise ValueError(f"Invalid item index: {item_index}")

        items[item_index]["is_completed"] = is_completed
        items[item_index]["completed_by"] = user_id if is_completed else None
        items[item_index]["completed_at"] = datetime.utcnow().isoformat() if is_completed else None
        if verification_data:
            items[item_index]["verification_data"] = verification_data

        return await self.checklist_repo.update_checklist_data(checklist_id, items)
