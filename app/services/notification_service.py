from typing import List
from app.repositories.notification import INotificationRepository
from app.schemas.notification import Notification, NotificationListResponse


class NotificationService:
    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    async def get_notifications(self, user_id: str) -> NotificationListResponse:
        notifications_data = await self.notification_repo.list_by_user(user_id)
        unread_count = await self.notification_repo.count_unread(user_id)

        notifications = [Notification(**n) for n in notifications_data]
        return NotificationListResponse(
            unread_count=unread_count,
            notifications=notifications,
        )

    async def mark_as_read(self, notification_id: str, user_id: str) -> dict:
        return await self.notification_repo.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: str) -> int:
        return await self.notification_repo.mark_all_as_read(user_id)
