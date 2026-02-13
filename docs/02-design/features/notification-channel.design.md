# Design: Notification Channel (Extensible Delivery)

> **Feature**: notification-channel
> **Plan**: [notification-channel.plan.md](../../01-plan/features/notification-channel.plan.md)
> **Created**: 2026-02-13
> **Status**: Design

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Endpoint Layer                                             │
│  POST /assignments/{id}/comments  →  CommentService         │
│  POST /admin/feedbacks            →  AdminService           │
└──────────────────┬──────────────────────────────────────────┘
                   │ calls notify()
┌──────────────────▼──────────────────────────────────────────┐
│  NotificationService                                        │
│  ├── notify() → DB record + dispatch                        │
│  ├── get_notifications()  (existing)                        │
│  ├── mark_as_read()       (existing)                        │
│  └── mark_all_as_read()   (existing)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  NotificationDispatcher (Strategy Pattern)                   │
│  ├── channels: List[INotificationChannel]                   │
│  └── dispatch(recipient_email, title, message, context)     │
│       └── for channel in channels: channel.send(...)        │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  INotificationChannel (ABC)                                 │
│  ├── EmailNotificationChannel                               │
│  │   └── send_email() + notification_email.html template    │
│  ├── (Future) SMSNotificationChannel                        │
│  └── (Future) PushNotificationChannel                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Module-Level Design

### 2.1 `app/notifications/__init__.py` (Create)

Empty package init.

```python
```

### 2.2 `app/notifications/channel.py` (Create)

INotificationChannel interface + EmailNotificationChannel implementation.

```python
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
        """Send a notification. Returns True on success, False on failure."""
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
                action_url=ctx.get("action_url", ""),
                app_name=ctx.get("app_name", "Task Server"),
            )
            await send_email(to=recipient_email, subject=title, html_body=html)
            return True
        except Exception as e:
            logger.error(f"EmailNotificationChannel failed: {e}")
            return False
```

**Key decisions**:
- `send()` returns `bool` instead of raising — failure is non-fatal
- Uses existing `send_email()` and `_load_template()` from `app/core/email.py`
- Catches all exceptions to ensure graceful degradation
- `context` dict allows channel-specific metadata (action_url, etc.)

### 2.3 `app/notifications/dispatcher.py` (Create)

NotificationDispatcher orchestrates multi-channel delivery.

```python
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
```

**Key decisions**:
- `dispatch()` returns `None` — it's fire-and-forget, never raises
- Iterates all channels; one failure doesn't block others
- Double safety: channel.send() already catches internally, dispatcher also catches

### 2.4 `app/templates/notification_email.html` (Create)

HTML template for notification emails. Consistent style with existing `verify_email.html`.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; margin: 0;">
  <div style="max-width: 480px; margin: 0 auto; background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <h2 style="color: #333; text-align: center; margin-top: 0;">{{title}}</h2>
    <p style="color: #666; line-height: 1.6; white-space: pre-wrap;">{{message}}</p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
    <p style="color: #bbb; text-align: center; font-size: 12px;">
      &copy; {{app_name}}
    </p>
  </div>
</body>
</html>
```

### 2.5 `app/models/enums.py` (Modify)

Add `COMMENT` to `NotificationType`.

```python
class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    NOTICE = "notice"
    FEEDBACK = "feedback"
    COMMENT = "comment"       # ← NEW
    SYSTEM = "system"
```

### 2.6 `app/services/notification_service.py` (Modify)

Add `notify()` method that creates DB record + dispatches to channels.

```python
import logging
from typing import List, Optional
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

    # --- Existing methods (unchanged) ---

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
```

**Key decisions**:
- `notify()` always creates DB record first (in-app notification)
- Recipient email is looked up via `IAuthRepository.get_user_by_id()`
- If no email found, skips dispatch silently (logs warning)
- Dispatch errors are caught — never blocks the caller
- Constructor now requires `auth_repo` and `dispatcher` (DI change)

### 2.7 `app/services/comment_service.py` (Modify)

Inject NotificationService and trigger notification on comment create.

```python
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
```

**Key decisions**:
- Needs `IAssignmentRepository` to look up assignees
- Notifies all assignees except the commenter (no self-notification)
- `_notify_assignees()` wrapped in try/except — comment creation never fails due to notification
- Message includes commenter name + content preview (max 100 chars)

### 2.8 `app/services/admin_service.py` (Modify)

Add NotificationService injection and trigger notification on feedback create.

```python
# Add to __init__ parameters:
notification_service: NotificationService

# Modify create_feedback:
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
```

### 2.9 `app/core/dependencies.py` (Modify)

Wire dispatcher, updated NotificationService, CommentService, AdminService.

```python
# Add imports:
from app.notifications.channel import EmailNotificationChannel
from app.notifications.dispatcher import NotificationDispatcher

# Add dispatcher factory:
def get_notification_dispatcher() -> NotificationDispatcher:
    return NotificationDispatcher(channels=[EmailNotificationChannel()])

# Update get_notification_service:
def get_notification_service() -> NotificationService:
    return NotificationService(
        notification_repo=get_notification_repo(),
        auth_repo=get_auth_repo(),
        dispatcher=get_notification_dispatcher(),
    )

# Update get_comment_service:
def get_comment_service() -> CommentService:
    return CommentService(
        comment_repo=get_comment_repo(),
        assignment_repo=get_assignment_repo(),
        notification_service=get_notification_service(),
    )

# Update get_admin_service:
def get_admin_service() -> AdminService:
    return AdminService(
        user_repo=get_user_repo(),
        org_repo=get_org_repo(),
        template_repo=get_template_repo(),
        assignment_repo=get_assignment_repo(),
        feedback_repo=get_feedback_repo(),
        notice_repo=get_notice_repo(),
        notification_service=get_notification_service(),
    )
```

---

## 3. Data Flow

### 3.1 Comment → Notification Flow

```
1. POST /assignments/{id}/comments
2. CommentService.create_comment()
3.   → comment_repo.create()  (save comment to DB)
4.   → _notify_assignees()
5.     → assignment_repo.get_by_id()  (get assignees list)
6.     → for each assignee (except commenter):
7.       → notification_service.notify()
8.         → notification_repo.create()  (in-app notification)
9.         → auth_repo.get_user_by_id()  (get email)
10.        → dispatcher.dispatch()
11.          → EmailNotificationChannel.send()
12.            → send_email() via SMTP
```

### 3.2 Feedback → Notification Flow

```
1. POST /admin/feedbacks
2. AdminService.create_feedback()
3.   → feedback_repo.create_feedback()  (save feedback to DB)
4.   → notification_service.notify() for target_user_id
5.     → notification_repo.create()  (in-app notification)
6.     → auth_repo.get_user_by_id()  (get email)
7.     → dispatcher.dispatch()
8.       → EmailNotificationChannel.send()
9.         → send_email() via SMTP
```

---

## 4. Error Handling Strategy

| Layer | Error Handling | Reason |
|-------|---------------|--------|
| `EmailNotificationChannel.send()` | try/except → return False | Channel failure is non-fatal |
| `NotificationDispatcher.dispatch()` | try/except per channel → log | One channel failure doesn't block others |
| `NotificationService.notify()` | try/except on dispatch → log | DB record always created; dispatch optional |
| `CommentService._notify_assignees()` | try/except all → pass | Comment creation never blocked |
| `AdminService.create_feedback()` | try/except notify → pass | Feedback creation never blocked |

---

## 5. Test Design

### 5.1 Fakes for Testing (in `conftest.py`)

```python
from app.notifications.channel import INotificationChannel
from app.notifications.dispatcher import NotificationDispatcher
from app.repositories.notification import INotificationRepository


class FakeNotificationChannel(INotificationChannel):
    def __init__(self):
        self.sent = []

    async def send(self, recipient_email, title, message, context=None):
        self.sent.append({"to": recipient_email, "title": title, "message": message})
        return True


class FakeNotificationRepository(INotificationRepository):
    def __init__(self):
        self.notifications = []

    async def list_by_user(self, user_id, company_id, limit=50):
        return [n for n in self.notifications if n["user_id"] == user_id]

    async def count_unread(self, user_id, company_id):
        return sum(1 for n in self.notifications if n["user_id"] == user_id and not n.get("is_read"))

    async def mark_as_read(self, notification_id, user_id):
        return {}

    async def mark_all_as_read(self, user_id, company_id):
        return 0

    async def create(self, data):
        data["id"] = f"notif-{len(self.notifications)+1}"
        data["is_read"] = False
        self.notifications.append(data)
        return data
```

### 5.2 Unit Tests: `tests/test_notification_channel.py`

| # | Test | Description |
|---|------|-------------|
| 1 | `test_email_channel_send_success` | EmailNotificationChannel calls send_email (mocked) |
| 2 | `test_email_channel_send_failure_returns_false` | send_email raises → returns False, no exception |
| 3 | `test_dispatcher_calls_all_channels` | Dispatcher iterates all registered channels |
| 4 | `test_dispatcher_continues_on_channel_failure` | One channel fails, others still called |
| 5 | `test_dispatcher_empty_channels` | No channels → no error |

### 5.3 Unit Tests: `tests/test_notification_service.py`

| # | Test | Description |
|---|------|-------------|
| 1 | `test_notify_creates_db_record` | notify() creates record via notification_repo |
| 2 | `test_notify_dispatches_to_channels` | notify() dispatches via dispatcher |
| 3 | `test_notify_skips_dispatch_when_no_email` | User has no email → dispatch skipped |
| 4 | `test_notify_dispatch_failure_doesnt_raise` | Dispatcher error → caught, no exception |
| 5 | `test_get_notifications_unchanged` | Existing method still works |

### 5.4 Integration Tests: `tests/test_comment_notification.py`

| # | Test | Description |
|---|------|-------------|
| 1 | `test_comment_creates_notification_for_assignees` | Comment triggers notification for each assignee |
| 2 | `test_comment_excludes_commenter_from_notification` | Commenter doesn't get self-notification |
| 3 | `test_comment_notification_failure_doesnt_block` | Notification error doesn't affect comment creation |
| 4 | `test_feedback_creates_notification_for_target` | Feedback triggers notification for target user |

---

## 6. Implementation Order

| Step | Task | Files | Dependencies |
|------|------|-------|-------------|
| 1 | Create INotificationChannel + EmailNotificationChannel | `app/notifications/__init__.py`, `app/notifications/channel.py` | None |
| 2 | Create NotificationDispatcher | `app/notifications/dispatcher.py` | Step 1 |
| 3 | Create notification_email.html template | `app/templates/notification_email.html` | None |
| 4 | Add COMMENT to NotificationType enum | `app/models/enums.py` | None |
| 5 | Update NotificationService with notify() | `app/services/notification_service.py` | Step 2 |
| 6 | Update CommentService with notification trigger | `app/services/comment_service.py` | Step 5 |
| 7 | Update AdminService with feedback notification | `app/services/admin_service.py` | Step 5 |
| 8 | Update DI container | `app/core/dependencies.py` | Step 6, 7 |
| 9 | Add test fakes to conftest.py | `tests/conftest.py` | Step 1 |
| 10 | Write unit tests (channel, dispatcher, service) | `tests/test_notification_channel.py`, `tests/test_notification_service.py` | Step 9 |
| 11 | Write integration tests (comment → notification) | `tests/test_comment_notification.py` | Step 10 |

---

## 7. Extensibility Guide

Adding a new channel (e.g., SMS):

```python
# 1. Implement interface
class SMSNotificationChannel(INotificationChannel):
    async def send(self, recipient_email, title, message, context=None):
        phone = context.get("phone")
        # ... send SMS via Twilio
        return True

# 2. Register in DI (dependencies.py)
def get_notification_dispatcher():
    return NotificationDispatcher(channels=[
        EmailNotificationChannel(),
        SMSNotificationChannel(),  # ← add here
    ])
```

No other code changes required.
