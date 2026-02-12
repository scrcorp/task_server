from typing import List, Optional
from app.repositories.user import SupabaseUserRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.checklist_template import ChecklistTemplateRepository
from app.repositories.task import TaskRepository
from app.repositories.feedback_notice import FeedbackRepository, NoticeRepository
from app.schemas.user import User, UserStatus

class AdminService:
    def __init__(self):
        self.user_repo = SupabaseUserRepository()
        self.org_repo = OrganizationRepository()
        self.template_repo = ChecklistTemplateRepository()
        self.task_repo = TaskRepository()
        self.feedback_repo = FeedbackRepository()
        self.notice_repo = NoticeRepository()

    # Staff Management
    async def get_pending_staff(self) -> List[User]:
        return await self.user_repo.list(filters={"status": UserStatus.PENDING})

    async def approve_staff(self, user_id: str, group_id: str) -> User:
        return await self.user_repo.update(user_id, {
            "status": UserStatus.ACTIVE,
            "group_id": group_id
        })

    # Dashboard Logic
    async def get_compliance_summary(self, branch_id: str, date: str):
        # 1. Fetch all checklist logs for the branch on the specific date
        # This requires a more complex query in a real repository, 
        # but here we'll simulate the aggregation logic.
        
        # In a real repository implementation:
        # logs = await self.task_repo.get_logs_by_branch_and_date(branch_id, date)
        
        # For now, we'll implement the structure of the compliance data
        summary = {
            "date": date,
            "branch_id": branch_id,
            "overall_rate": 0.0,
            "by_group": [],
            "by_template": []
        }
        
        # Example logic for calculation:
        # total_items = len(logs)
        # completed_items = len([l for l in logs if l.is_completed])
        # summary["overall_rate"] = (completed_items / total_items * 100) if total_items > 0 else 0
        
        return summary

    async def create_checklist_template(self, data: dict):
        return await self.template_repo.create_template(data)
