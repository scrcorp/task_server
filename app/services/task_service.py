from typing import List, Optional
from app.repositories.task import TaskRepository
from app.schemas.task import Task
from datetime import datetime

class TaskService:
    def __init__(self):
        self.task_repo = TaskRepository()

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
