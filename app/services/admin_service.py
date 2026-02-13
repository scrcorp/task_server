from typing import List, Optional
from app.repositories.user import SupabaseUserRepository
from app.repositories.organization import IOrganizationRepository
from app.repositories.checklist_template import IChecklistTemplateRepository
from app.repositories.assignment import IAssignmentRepository
from app.repositories.feedback_notice import IFeedbackRepository, INoticeRepository
from app.services.notification_service import NotificationService
from app.schemas.organization import Company, Brand, Branch, GroupType, Group
from app.schemas.user import User, UserStatus


class AdminService:
    def __init__(
        self,
        user_repo: SupabaseUserRepository,
        org_repo: IOrganizationRepository,
        template_repo: IChecklistTemplateRepository,
        assignment_repo: IAssignmentRepository,
        feedback_repo: IFeedbackRepository,
        notice_repo: INoticeRepository,
        notification_service: NotificationService,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.template_repo = template_repo
        self.assignment_repo = assignment_repo
        self.feedback_repo = feedback_repo
        self.notice_repo = notice_repo
        self.notification_service = notification_service

    # ── Staff Management ────────────────────────────
    async def get_pending_staff(self, company_id: str) -> List[User]:
        return await self.user_repo.list(filters={"status": "pending", "company_id": company_id})

    async def approve_staff(self, user_id: str) -> User:
        return await self.user_repo.update(user_id, {"status": "active"})

    async def reject_staff(self, user_id: str) -> User:
        return await self.user_repo.update(user_id, {"status": "inactive"})

    # ── Company Management ──────────────────────────
    async def get_company(self, company_id: str) -> Optional[Company]:
        return await self.org_repo.get_company_by_id(company_id)

    async def update_company(self, company_id: str, data: dict) -> Company:
        return await self.org_repo.update_company(company_id, data)

    # ── Brand Management ────────────────────────────
    async def list_brands(self, company_id: str) -> List[Brand]:
        return await self.org_repo.list_brands(company_id)

    async def create_brand(self, data: dict) -> Brand:
        return await self.org_repo.create_brand(data)

    async def update_brand(self, brand_id: str, data: dict) -> Brand:
        return await self.org_repo.update_brand(brand_id, data)

    async def delete_brand(self, brand_id: str) -> bool:
        return await self.org_repo.delete_brand(brand_id)

    # ── Branch Management ───────────────────────────
    async def list_branches(self, brand_id: Optional[str] = None) -> List[Branch]:
        return await self.org_repo.list_branches(brand_id)

    async def create_branch(self, data: dict) -> Branch:
        return await self.org_repo.create_branch(data)

    async def delete_branch(self, branch_id: str) -> bool:
        return await self.org_repo.delete_branch(branch_id)

    # ── GroupType Management ────────────────────────
    async def list_group_types(self, branch_id: str) -> List[GroupType]:
        return await self.org_repo.list_group_types(branch_id)

    async def create_group_type(self, data: dict) -> GroupType:
        return await self.org_repo.create_group_type(data)

    async def delete_group_type(self, group_type_id: str) -> bool:
        return await self.org_repo.delete_group_type(group_type_id)

    # ── Group Management ────────────────────────────
    async def list_groups(self, group_type_id: Optional[str] = None) -> List[Group]:
        return await self.org_repo.list_groups(group_type_id)

    async def create_group(self, data: dict) -> Group:
        return await self.org_repo.create_group(data)

    async def delete_group(self, group_id: str) -> bool:
        return await self.org_repo.delete_group(group_id)

    # ── Checklist Templates ─────────────────────────
    async def create_checklist_template(self, data: dict):
        return await self.template_repo.create_template(data)

    async def list_checklist_templates(self, company_id: str, branch_id: Optional[str] = None):
        return await self.template_repo.list_templates(company_id, branch_id)

    # ── Feedbacks ───────────────────────────────────
    async def list_feedbacks(self, company_id: str, filters: dict) -> List[dict]:
        return await self.feedback_repo.list_feedbacks(company_id, filters)

    async def create_feedback(self, data: dict) -> dict:
        result = await self.feedback_repo.create_feedback(data)

        # Notify target user about feedback
        target_user_id = data.get("target_user_id")
        if target_user_id:
            try:
                await self.notification_service.notify(
                    company_id=data.get("company_id", ""),
                    user_id=target_user_id,
                    notification_type="feedback",
                    title="New feedback received",
                    message=data.get("content", "")[:100],
                    reference_id=result.get("id"),
                    reference_type="feedback",
                )
            except Exception:
                pass  # Never block feedback creation

        return result

    # ── Dashboard ───────────────────────────────────
    async def get_compliance_summary(self, branch_id: str, date: str):
        return {
            "date": date,
            "branch_id": branch_id,
            "overall_rate": 0.0,
            "by_group": [],
            "by_template": [],
        }
