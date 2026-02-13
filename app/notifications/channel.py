import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.core.email import send_email, _load_template

logger = logging.getLogger(__name__)


class INotificationChannel(ABC):
    """Abstract interface for notification delivery channels."""

    @abstractmethod
    async def send(
        self,
        recipient_email: str,
        title: str,
        message: str,
        context: Optional[dict] = None,
    ) -> bool:
        pass


class EmailNotificationChannel(INotificationChannel):
    """Sends notification emails via existing SMTP infrastructure."""

    async def send(
        self,
        recipient_email: str,
        title: str,
        message: str,
        context: Optional[dict] = None,
    ) -> bool:
        try:
            ctx = context or {}
            html = _load_template(
                "notification_email.html",
                title=title,
                message=message,
                app_name=ctx.get("app_name", "Task Server"),
            )
            await send_email(to=recipient_email, subject=title, html_body=html)
            return True
        except Exception as e:
            logger.error(f"EmailNotificationChannel failed: {e}")
            return False
