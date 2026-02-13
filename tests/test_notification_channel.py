"""Unit tests for INotificationChannel, EmailNotificationChannel, and NotificationDispatcher."""
import pytest
from unittest.mock import AsyncMock, patch

from app.notifications.channel import EmailNotificationChannel
from app.notifications.dispatcher import NotificationDispatcher
from tests.conftest import FakeNotificationChannel


@pytest.mark.asyncio
async def test_email_channel_send_success():
    """EmailNotificationChannel calls send_email and returns True."""
    channel = EmailNotificationChannel()
    with patch("app.notifications.channel.send_email", new_callable=AsyncMock) as mock_send:
        with patch("app.notifications.channel._load_template", return_value="<html>test</html>"):
            result = await channel.send("user@test.com", "Title", "Message")

    assert result is True
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_email_channel_send_failure_returns_false():
    """EmailNotificationChannel returns False when send_email raises."""
    channel = EmailNotificationChannel()
    with patch("app.notifications.channel.send_email", new_callable=AsyncMock, side_effect=Exception("SMTP error")):
        with patch("app.notifications.channel._load_template", return_value="<html>test</html>"):
            result = await channel.send("user@test.com", "Title", "Message")

    assert result is False


@pytest.mark.asyncio
async def test_dispatcher_calls_all_channels():
    """NotificationDispatcher iterates all registered channels."""
    ch1 = FakeNotificationChannel()
    ch2 = FakeNotificationChannel()
    dispatcher = NotificationDispatcher(channels=[ch1, ch2])

    await dispatcher.dispatch("user@test.com", "Title", "Message")

    assert len(ch1.sent) == 1
    assert len(ch2.sent) == 1
    assert ch1.sent[0]["to"] == "user@test.com"


@pytest.mark.asyncio
async def test_dispatcher_continues_on_channel_failure():
    """One channel failure doesn't block others."""
    ch_fail = FakeNotificationChannel(should_fail=True)
    ch_ok = FakeNotificationChannel()
    dispatcher = NotificationDispatcher(channels=[ch_fail, ch_ok])

    await dispatcher.dispatch("user@test.com", "Title", "Message")

    assert len(ch_fail.sent) == 0
    assert len(ch_ok.sent) == 1


@pytest.mark.asyncio
async def test_dispatcher_empty_channels():
    """Dispatcher with no channels doesn't raise."""
    dispatcher = NotificationDispatcher(channels=[])
    await dispatcher.dispatch("user@test.com", "Title", "Message")
