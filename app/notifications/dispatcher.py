import logging
from typing import List, Optional

from app.notifications.channel import INotificationChannel

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """Dispatches notifications to all registered channels."""

    def __init__(self, channels: List[INotificationChannel] = None):
        self.channels = channels or []

    async def dispatch(
        self,
        recipient_email: str,
        title: str,
        message: str,
        context: Optional[dict] = None,
    ) -> None:
        for channel in self.channels:
            try:
                await channel.send(recipient_email, title, message, context)
            except Exception as e:
                logger.error(f"Dispatch failed for {channel.__class__.__name__}: {e}")
