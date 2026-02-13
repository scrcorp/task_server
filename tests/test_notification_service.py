"""Unit tests for NotificationService.notify() method."""
import pytest

from tests.conftest import FakeNotificationChannel, FakeNotificationRepository, FakeAuthRepository
from app.notifications.dispatcher import NotificationDispatcher
from app.services.notification_service import NotificationService


@pytest.fixture
def setup_notification_service():
    """Create NotificationService with fakes, including a user with email."""
    channel = FakeNotificationChannel()
    dispatcher = NotificationDispatcher(channels=[channel])
    notif_repo = FakeNotificationRepository()
    auth_repo = FakeAuthRepository()
    service = NotificationService(
        notification_repo=notif_repo,
        auth_repo=auth_repo,
        dispatcher=dispatcher,
    )
    return service, notif_repo, auth_repo, channel


@pytest.mark.asyncio
async def test_notify_creates_db_record(setup_notification_service):
    """notify() creates a record via notification_repo."""
    service, notif_repo, auth_repo, _ = setup_notification_service
    auth_repo.users["user-1"] = {"id": "user-1", "email": "user@test.com", "login_id": "u1"}

    await service.notify(
        company_id="company-1",
        user_id="user-1",
        notification_type="comment",
        title="Test",
        message="Hello",
    )

    assert len(notif_repo.notifications) == 1
    assert notif_repo.notifications[0]["type"] == "comment"
    assert notif_repo.notifications[0]["user_id"] == "user-1"


@pytest.mark.asyncio
async def test_notify_dispatches_to_channels(setup_notification_service):
    """notify() dispatches via the dispatcher to channels."""
    service, _, auth_repo, channel = setup_notification_service
    auth_repo.users["user-1"] = {"id": "user-1", "email": "user@test.com", "login_id": "u1"}

    await service.notify(
        company_id="company-1",
        user_id="user-1",
        notification_type="comment",
        title="Test",
        message="Hello",
    )

    assert len(channel.sent) == 1
    assert channel.sent[0]["to"] == "user@test.com"
    assert channel.sent[0]["title"] == "Test"


@pytest.mark.asyncio
async def test_notify_skips_dispatch_when_no_email(setup_notification_service):
    """When user has no email, dispatch is skipped but DB record is still created."""
    service, notif_repo, auth_repo, channel = setup_notification_service
    auth_repo.users["user-1"] = {"id": "user-1", "login_id": "u1"}  # no email

    await service.notify(
        company_id="company-1",
        user_id="user-1",
        notification_type="comment",
        title="Test",
        message="Hello",
    )

    assert len(notif_repo.notifications) == 1  # DB record created
    assert len(channel.sent) == 0  # dispatch skipped


@pytest.mark.asyncio
async def test_notify_skips_dispatch_when_user_not_found(setup_notification_service):
    """When user doesn't exist, dispatch is skipped."""
    service, notif_repo, _, channel = setup_notification_service

    await service.notify(
        company_id="company-1",
        user_id="nonexistent-user",
        notification_type="comment",
        title="Test",
        message="Hello",
    )

    assert len(notif_repo.notifications) == 1
    assert len(channel.sent) == 0


@pytest.mark.asyncio
async def test_notify_dispatch_failure_doesnt_raise(setup_notification_service):
    """Dispatcher error is caught, no exception raised."""
    service, notif_repo, auth_repo, _ = setup_notification_service
    auth_repo.users["user-1"] = {"id": "user-1", "email": "user@test.com", "login_id": "u1"}

    # Replace dispatcher with one that has a failing channel
    failing_channel = FakeNotificationChannel(should_fail=True)
    service.dispatcher = NotificationDispatcher(channels=[failing_channel])

    # Should not raise
    await service.notify(
        company_id="company-1",
        user_id="user-1",
        notification_type="comment",
        title="Test",
        message="Hello",
    )

    assert len(notif_repo.notifications) == 1  # DB record still created
