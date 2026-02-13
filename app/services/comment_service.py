from typing import List, Optional

from app.repositories.comment import ICommentRepository
from app.repositories.assignment import IAssignmentRepository
from app.services.notification_service import NotificationService
from app.schemas.assignment import Comment


class CommentService:
    def __init__(
        self,
        comment_repo: ICommentRepository,
        assignment_repo: IAssignmentRepository,
        notification_service: NotificationService,
    ):
        self.comment_repo = comment_repo
        self.assignment_repo = assignment_repo
        self.notification_service = notification_service

    async def list_comments(self, assignment_id: str) -> List[Comment]:
        data = await self.comment_repo.list_by_assignment(assignment_id)
        return [Comment(**item) for item in data]

    async def create_comment(
        self,
        assignment_id: str,
        user_id: str,
        content: Optional[str],
        content_type: str = "text",
        attachments: Optional[list] = None,
        user_name: Optional[str] = None,
        is_manager: bool = False,
    ) -> Comment:
        data = {
            "assignment_id": assignment_id,
            "user_id": user_id,
            "content": content,
            "content_type": content_type,
            "user_name": user_name,
            "is_manager": is_manager,
        }
        if attachments:
            data["attachments"] = attachments
        result = await self.comment_repo.create(data)
        comment = Comment(**result)

        # Notify assignees (except the commenter)
        await self._notify_assignees(assignment_id, user_id, user_name, content)

        return comment

    async def _notify_assignees(
        self,
        assignment_id: str,
        commenter_id: str,
        commenter_name: Optional[str],
        content: Optional[str],
    ) -> None:
        """Send notification to all assignees except the commenter."""
        try:
            assignment = await self.assignment_repo.get_by_id(assignment_id)
            if not assignment:
                return

            assignees = assignment.get("assignees", [])
            company_id = assignment.get("company_id", "")
            title_text = assignment.get("title", "task")
            sender = commenter_name or "Someone"
            preview = (content or "")[:100]

            for assignee in assignees:
                assignee_user_id = assignee.get("user_id")
                if assignee_user_id and assignee_user_id != commenter_id:
                    await self.notification_service.notify(
                        company_id=company_id,
                        user_id=assignee_user_id,
                        notification_type="comment",
                        title=f"New comment on '{title_text}'",
                        message=f"{sender}: {preview}",
                        reference_id=assignment_id,
                        reference_type="assignment",
                    )
        except Exception:
            pass  # Never block comment creation

    async def delete_comment(self, comment_id: str) -> bool:
        return await self.comment_repo.delete(comment_id)
