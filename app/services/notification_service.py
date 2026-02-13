import logging
from typing import Optional

from app.repositories.notification import INotificationRepository
from app.repositories.auth import IAuthRepository
from app.notifications.dispatcher import NotificationDispatcher
from app.schemas.notification import Notification, NotificationListResponse

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        notification_repo: INotificationRepository,
        auth_repo: IAuthRepository,
        dispatcher: NotificationDispatcher,
    ):
        self.notification_repo = notification_repo
        self.auth_repo = auth_repo
        self.dispatcher = dispatcher

    async def notify(
        self,
        company_id: str,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        reference_id: Optional[str] = None,
        reference_type: Optional[str] = None,
    ) -> None:
        """Create in-app notification + dispatch to external channels."""
        # 1. Create DB record (in-app notification)
        await self.notification_repo.create({
            "company_id": company_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "reference_id": reference_id,
            "reference_type": reference_type,
        })

        # 2. Look up recipient email
        user = await self.auth_repo.get_user_by_id(user_id)
        if not user or not user.get("email"):
            logger.warning(f"No email found for user {user_id}, skipping dispatch")
            return

        # 3. Dispatch to external channels (email, etc.)
        try:
            await self.dispatcher.dispatch(
                recipient_email=user["email"],
                title=title,
                message=message,
                context={"reference_id": reference_id, "reference_type": reference_type},
            )
        except Exception as e:
            logger.error(f"Notification dispatch failed: {e}")

    async def get_notifications(self, user_id: str, company_id: str) -> NotificationListResponse:
        notifications_data = await self.notification_repo.list_by_user(user_id, company_id)
        unread_count = await self.notification_repo.count_unread(user_id, company_id)
        notifications = [Notification(**n) for n in notifications_data]
        return NotificationListResponse(
            unread_count=unread_count,
            notifications=notifications,
        )

    async def mark_as_read(self, notification_id: str, user_id: str) -> dict:
        return await self.notification_repo.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: str, company_id: str) -> int:
        return await self.notification_repo.mark_all_as_read(user_id, company_id)
