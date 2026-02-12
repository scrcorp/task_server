from typing import List, Optional, Any
from app.repositories.task import TaskRepository
from app.schemas.task import Task, ChecklistItem
from datetime import datetime


class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def list_tasks(self, filters: Optional[dict] = None) -> List[Task]:
        return await self.task_repo.list(filters=filters)

    async def get_task(self, task_id: str) -> Optional[Task]:
        return await self.task_repo.get_by_id(task_id)

    async def create_task(self, data: dict) -> Task:
        return await self.task_repo.create(data)

    async def update_task(self, task_id: str, data: dict) -> Task:
        return await self.task_repo.update(task_id, data)

    async def delete_task(self, task_id: str) -> bool:
        return await self.task_repo.delete(task_id)

    async def update_task_status(self, task_id: str, status: str) -> Task:
        return await self.task_repo.update(task_id, {"status": status})

    async def get_my_tasks(self, user_id: str) -> List[Task]:
        return await self.task_repo.list(filters={"assigned_to": user_id})

    async def update_checklist_item(self, user_id: str, item_id: str, is_completed: bool, verification_data: Optional[str] = None):
        # 1. Update the item status
        update_data = {"is_completed": is_completed}
        if verification_data:
            update_data["verification_data"] = verification_data

        updated_item = await self.task_repo.update_checklist_item(item_id, update_data)

        # 2. Automatically create a log record (Business Requirement)
        log_data = {
            "item_id": item_id,
            "user_id": user_id,
            "is_completed": is_completed,
            "verification_data": verification_data,
            "checked_at": datetime.utcnow().isoformat()
        }
        await self.task_repo.create_checklist_log(log_data)

        return updated_item

    async def create_checklist_item(self, task_id: str, content: str, is_completed: bool = False) -> dict:
        data = {
            "task_id": task_id,
            "content": content,
            "is_completed": is_completed,
        }
        return await self.task_repo.create_checklist_item(data)

    async def delete_checklist_item(self, item_id: str) -> bool:
        return await self.task_repo.delete_checklist_item(item_id)
