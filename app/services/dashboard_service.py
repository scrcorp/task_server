from typing import List, Optional
from app.repositories.assignment import IAssignmentRepository
from app.repositories.feedback_notice import INoticeRepository
from app.repositories.daily_checklist import IDailyChecklistRepository
from app.models.enums import AssignmentStatus, Priority
from datetime import date


class DashboardService:
    def __init__(
        self,
        assignment_repo: IAssignmentRepository,
        notice_repo: INoticeRepository,
        checklist_repo: IDailyChecklistRepository,
    ):
        self.assignment_repo = assignment_repo
        self.notice_repo = notice_repo
        self.checklist_repo = checklist_repo

    async def get_summary(self, user_id: str, company_id: str) -> dict:
        # 1. Assignment summary
        assignments = await self.assignment_repo.list_by_assignee(user_id, company_id)

        total = len(assignments)
        done = sum(1 for a in assignments if a.get("status") == AssignmentStatus.DONE.value)
        in_progress = sum(1 for a in assignments if a.get("status") == AssignmentStatus.IN_PROGRESS.value)
        todo = sum(1 for a in assignments if a.get("status") == AssignmentStatus.TODO.value)
        completion_rate = round(done / total * 100, 1) if total > 0 else 0

        assignment_summary = {
            "total_assignments": total,
            "completed": done,
            "in_progress": in_progress,
            "todo": todo,
            "completion_rate": completion_rate,
        }

        # 2. Urgent alerts
        urgent_alerts = [
            {"id": a["id"], "title": a["title"], "due_date": a.get("due_date")}
            for a in assignments
            if a.get("priority") == Priority.URGENT.value and a.get("status") != AssignmentStatus.DONE.value
        ]

        # 3. Recent notices
        notices = await self.notice_repo.list_notices(company_id, limit=5)
        recent_notices = [
            {"id": n["id"], "title": n["title"], "created_at": n["created_at"]}
            for n in notices
        ]

        return {
            "assignment_summary": assignment_summary,
            "urgent_alerts": urgent_alerts,
            "recent_notices": recent_notices,
        }
