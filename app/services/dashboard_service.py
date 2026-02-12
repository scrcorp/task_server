from typing import List, Optional
from app.repositories.task import TaskRepository
from app.repositories.feedback_notice import INoticeRepository
from app.models.enums import TaskStatus, Priority
from datetime import datetime, date


class DashboardService:
    def __init__(self, task_repo: TaskRepository, notice_repo: INoticeRepository):
        self.task_repo = task_repo
        self.notice_repo = notice_repo

    async def get_summary(self, user_id: str) -> dict:
        # 1. Task summary
        tasks = await self.task_repo.list(filters={"assigned_to": user_id})

        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)
        completion_rate = round(done / total * 100, 1) if total > 0 else 0

        task_summary = {
            "total_tasks": total,
            "completed_tasks": done,
            "in_progress_tasks": in_progress,
            "pending_tasks": todo,
            "completion_rate": completion_rate,
        }

        # 2. Urgent alerts - tasks that are urgent priority and not done
        urgent_alerts = [
            {"id": t.id, "title": t.title, "due_date": t.due_date.isoformat() if t.due_date else None}
            for t in tasks
            if t.priority == Priority.URGENT and t.status != TaskStatus.DONE
        ]

        # 3. Daily progress - checklist completion rate for today's daily tasks
        daily_tasks = [t for t in tasks if t.type.value == "daily"]
        total_checklist = 0
        completed_checklist = 0
        for t in daily_tasks:
            if t.checklist:
                total_checklist += len(t.checklist)
                completed_checklist += sum(1 for c in t.checklist if c.is_completed)

        daily_progress = {
            "total_items": total_checklist,
            "completed_items": completed_checklist,
            "rate": round(completed_checklist / total_checklist * 100, 1) if total_checklist > 0 else 0,
        }

        # 4. Recent notices
        notices = await self.notice_repo.list_notices(limit=5)
        recent_notices = [
            {"id": n["id"], "title": n["title"], "created_at": n["created_at"]}
            for n in notices
        ]

        return {
            "task_summary": task_summary,
            "urgent_alerts": urgent_alerts,
            "daily_progress": daily_progress,
            "recent_notices": recent_notices,
        }
