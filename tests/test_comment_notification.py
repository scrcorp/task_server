"""Integration tests for comment/feedback → notification flow."""
import pytest

from tests.conftest import (
    FakeNotificationChannel, FakeNotificationRepository,
    FakeAuthRepository, FakeCommentRepository, FakeAssignmentRepository,
)
from app.notifications.dispatcher import NotificationDispatcher
from app.repositories.feedback_notice import IFeedbackRepository
from app.services.notification_service import NotificationService
from app.services.comment_service import CommentService
from app.services.admin_service import AdminService


@pytest.fixture
def integration_setup():
    """Full integration setup: comment → notification → channel."""
    channel = FakeNotificationChannel()
    dispatcher = NotificationDispatcher(channels=[channel])
    notif_repo = FakeNotificationRepository()
    auth_repo = FakeAuthRepository()
    comment_repo = FakeCommentRepository()
    assignment_repo = FakeAssignmentRepository()

    notification_service = NotificationService(
        notification_repo=notif_repo,
        auth_repo=auth_repo,
        dispatcher=dispatcher,
    )
    comment_service = CommentService(
        comment_repo=comment_repo,
        assignment_repo=assignment_repo,
        notification_service=notification_service,
    )

    # Seed: two users assigned to an assignment
    auth_repo.users["user-commenter"] = {
        "id": "user-commenter", "email": "commenter@test.com", "login_id": "commenter",
    }
    auth_repo.users["user-assignee"] = {
        "id": "user-assignee", "email": "assignee@test.com", "login_id": "assignee",
    }
    assignment_repo.assignments["assign-1"] = {
        "id": "assign-1",
        "title": "Fix login bug",
        "company_id": "company-1",
        "assignees": [
            {"user_id": "user-commenter", "assignment_id": "assign-1"},
            {"user_id": "user-assignee", "assignment_id": "assign-1"},
        ],
    }

    return comment_service, notif_repo, channel


@pytest.mark.asyncio
async def test_comment_creates_notification_for_assignees(integration_setup):
    """Comment triggers notification for each assignee except the commenter."""
    comment_service, notif_repo, channel = integration_setup

    comment = await comment_service.create_comment(
        assignment_id="assign-1",
        user_id="user-commenter",
        content="Please check this",
        user_name="Commenter",
    )

    assert comment.id is not None
    # Only user-assignee should get a notification (not user-commenter)
    assert len(notif_repo.notifications) == 1
    assert notif_repo.notifications[0]["user_id"] == "user-assignee"
    assert notif_repo.notifications[0]["type"] == "comment"


@pytest.mark.asyncio
async def test_comment_excludes_commenter_from_notification(integration_setup):
    """Commenter doesn't get self-notification."""
    comment_service, notif_repo, channel = integration_setup

    await comment_service.create_comment(
        assignment_id="assign-1",
        user_id="user-commenter",
        content="My own comment",
        user_name="Commenter",
    )

    for notif in notif_repo.notifications:
        assert notif["user_id"] != "user-commenter"


@pytest.mark.asyncio
async def test_comment_dispatches_email_to_assignee(integration_setup):
    """Comment triggers email dispatch to assignee."""
    comment_service, _, channel = integration_setup

    await comment_service.create_comment(
        assignment_id="assign-1",
        user_id="user-commenter",
        content="Check this out",
        user_name="Commenter",
    )

    assert len(channel.sent) == 1
    assert channel.sent[0]["to"] == "assignee@test.com"
    assert "Fix login bug" in channel.sent[0]["title"]


@pytest.mark.asyncio
async def test_comment_notification_failure_doesnt_block(integration_setup):
    """Notification failure doesn't prevent comment creation."""
    comment_service, _, _ = integration_setup

    # Replace notification_service dispatcher with a failing one
    failing_channel = FakeNotificationChannel(should_fail=True)
    comment_service.notification_service.dispatcher = NotificationDispatcher(
        channels=[failing_channel]
    )

    comment = await comment_service.create_comment(
        assignment_id="assign-1",
        user_id="user-commenter",
        content="This should still work",
        user_name="Commenter",
    )

    assert comment.id is not None
    assert comment.content == "This should still work"


# -- Feedback → Notification tests --

class FakeFeedbackRepository(IFeedbackRepository):
    """In-memory fake feedback repository for testing."""

    def __init__(self):
        self.feedbacks = []
        self._counter = 0

    async def create_feedback(self, data):
        self._counter += 1
        data["id"] = f"feedback-{self._counter}"
        self.feedbacks.append(data)
        return data

    async def list_feedbacks(self, company_id, filters):
        return self.feedbacks

    async def update_feedback(self, id, data):
        return data


@pytest.fixture
def feedback_integration_setup():
    """Full integration setup: feedback → notification → channel."""
    from unittest.mock import MagicMock
    from tests.conftest import FakeOrgRepository

    channel = FakeNotificationChannel()
    dispatcher = NotificationDispatcher(channels=[channel])
    notif_repo = FakeNotificationRepository()
    auth_repo = FakeAuthRepository()
    feedback_repo = FakeFeedbackRepository()

    notification_service = NotificationService(
        notification_repo=notif_repo,
        auth_repo=auth_repo,
        dispatcher=dispatcher,
    )

    admin_service = AdminService(
        user_repo=MagicMock(),
        org_repo=FakeOrgRepository(),
        template_repo=MagicMock(),
        assignment_repo=MagicMock(),
        feedback_repo=feedback_repo,
        notice_repo=MagicMock(),
        notification_service=notification_service,
    )

    # Seed: target user
    auth_repo.users["target-user"] = {
        "id": "target-user", "email": "target@test.com", "login_id": "target",
    }

    return admin_service, notif_repo, channel


@pytest.mark.asyncio
async def test_feedback_creates_notification_for_target(feedback_integration_setup):
    """Feedback creation triggers notification for target user."""
    admin_service, notif_repo, channel = feedback_integration_setup

    await admin_service.create_feedback({
        "content": "Great job on the task!",
        "company_id": "company-1",
        "author_id": "manager-1",
        "target_user_id": "target-user",
    })

    assert len(notif_repo.notifications) == 1
    assert notif_repo.notifications[0]["user_id"] == "target-user"
    assert notif_repo.notifications[0]["type"] == "feedback"
    assert len(channel.sent) == 1
    assert channel.sent[0]["to"] == "target@test.com"
