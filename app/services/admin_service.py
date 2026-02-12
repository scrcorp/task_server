from typing import List, Optional
from app.repositories.user import SupabaseUserRepository
from app.repositories.organization import IOrganizationRepository
from app.repositories.checklist_template import IChecklistTemplateRepository
from app.repositories.task import TaskRepository
from app.repositories.feedback_notice import IFeedbackRepository, INoticeRepository
from app.schemas.organization import Brand, Branch, Group
from app.schemas.user import User, UserStatus


class AdminService:
    def __init__(
        self,
        user_repo: SupabaseUserRepository,
        org_repo: IOrganizationRepository,
        template_repo: IChecklistTemplateRepository,
        task_repo: TaskRepository,
        feedback_repo: IFeedbackRepository,
        notice_repo: INoticeRepository,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.template_repo = template_repo
        self.task_repo = task_repo
        self.feedback_repo = feedback_repo
        self.notice_repo = notice_repo

    # Staff Management
    async def get_pending_staff(self) -> List[User]:
        return await self.user_repo.list(filters={"status": UserStatus.PENDING})

    async def approve_staff(self, user_id: str, group_id: str) -> User:
        return await self.user_repo.update(user_id, {
            "status": UserStatus.ACTIVE,
            "group_id": group_id,
        })

    async def reject_staff(self, user_id: str) -> User:
        return await self.user_repo.update(user_id, {
            "status": UserStatus.INACTIVE,
        })

    # Brand Management
    async def list_brands(self) -> List[Brand]:
        return await self.org_repo.list_brands()

    async def create_brand(self, data: dict) -> Brand:
        return await self.org_repo.create_brand(data)

    async def update_brand(self, brand_id: str, data: dict) -> Brand:
        return await self.org_repo.update_brand(brand_id, data)

    async def delete_brand(self, brand_id: str) -> bool:
        return await self.org_repo.delete_brand(brand_id)

    # Branch Management
    async def list_branches(self, brand_id: Optional[str] = None) -> List[Branch]:
        return await self.org_repo.list_branches(brand_id)

    async def create_branch(self, data: dict) -> Branch:
        return await self.org_repo.create_branch(data)

    async def delete_branch(self, branch_id: str) -> bool:
        return await self.org_repo.delete_branch(branch_id)

    # Group Management
    async def list_groups(self, branch_id: Optional[str] = None) -> List[Group]:
        return await self.org_repo.list_groups(branch_id)

    async def create_group(self, data: dict) -> Group:
        return await self.org_repo.create_group(data)

    async def delete_group(self, group_id: str) -> bool:
        return await self.org_repo.delete_group(group_id)

    # Checklist Templates
    async def create_checklist_template(self, data: dict):
        return await self.template_repo.create_template(data)

    async def list_checklist_templates(self, brand_id: Optional[str] = None, group_id: Optional[str] = None):
        return await self.template_repo.list_templates(brand_id, group_id)

    # Feedbacks
    async def list_feedbacks(self, filters: dict) -> List[dict]:
        return await self.feedback_repo.list_feedbacks(filters)

    async def create_feedback(self, data: dict) -> dict:
        return await self.feedback_repo.create_feedback(data)

    # Dashboard Logic
    async def get_compliance_summary(self, branch_id: str, date: str):
        summary = {
            "date": date,
            "branch_id": branch_id,
            "overall_rate": 0.0,
            "by_group": [],
            "by_template": [],
        }
        return summary
