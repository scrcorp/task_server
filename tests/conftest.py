import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from app.repositories.auth import IAuthRepository
from app.repositories.organization import IOrganizationRepository
from app.repositories.notification import INotificationRepository
from app.repositories.comment import ICommentRepository
from app.repositories.assignment import IAssignmentRepository
from app.notifications.channel import INotificationChannel
from app.notifications.dispatcher import NotificationDispatcher
from app.storage.base import IStorageProvider
from app.services.auth_service import AuthService
from app.services.notification_service import NotificationService
from app.services.comment_service import CommentService
from app.services.file_service import FileService


class FakeAuthRepository(IAuthRepository):
    """In-memory fake auth repository for testing."""

    def __init__(self):
        self.users = {}
        self.codes = {}
        self._code_counter = 0

    async def sign_up(self, data: dict) -> dict:
        self.users[data["id"]] = data
        return data

    async def sign_in(self, login_id: str, password: str) -> dict:
        from app.core.password import verify_password

        for user in self.users.values():
            if user["login_id"] == login_id:
                if verify_password(password, user["password_hash"]):
                    return user
                raise Exception("Invalid login ID or password.")
        raise Exception("Invalid login ID or password.")

    async def get_user_by_id(self, user_id: str) -> dict | None:
        return self.users.get(user_id)

    async def get_user_by_login_id(self, login_id: str) -> dict | None:
        for user in self.users.values():
            if user["login_id"] == login_id:
                return user
        return None

    async def get_user_by_email(self, email: str) -> dict | None:
        for user in self.users.values():
            if user["email"] == email:
                return user
        return None

    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        if user_id in self.users:
            self.users[user_id]["password_hash"] = new_password_hash
            return True
        return False

    async def verify_email(self, user_id: str) -> bool:
        if user_id in self.users:
            self.users[user_id]["email_verified"] = True
            return True
        return False

    async def check_duplicate(self, login_id: str, email: str) -> str | None:
        for user in self.users.values():
            if user["login_id"] == login_id:
                return "Login ID is already taken."
            if user["email"] == email:
                return "Email is already registered."
        return None

    async def save_verification_code(
        self, user_id: str, email: str, code: str, expires_at: datetime
    ) -> dict:
        self._code_counter += 1
        code_id = f"code-{self._code_counter}"
        record = {
            "id": code_id,
            "user_id": user_id,
            "email": email,
            "code": code,
            "expires_at": expires_at.isoformat(),
            "used": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.codes[code_id] = record
        return record

    async def get_valid_verification_code(
        self, email: str, code: str
    ) -> dict | None:
        now = datetime.now(timezone.utc).isoformat()
        for record in self.codes.values():
            if (
                record["email"] == email
                and record["code"] == code
                and not record["used"]
                and record["expires_at"] > now
            ):
                return record
        return None

    async def mark_verification_code_used(self, code_id: str) -> bool:
        if code_id in self.codes:
            self.codes[code_id]["used"] = True
            return True
        return False

    async def invalidate_previous_codes(self, email: str) -> bool:
        for record in self.codes.values():
            if record["email"] == email and not record["used"]:
                record["used"] = True
        return True

    async def count_recent_codes(self, email: str, since: datetime) -> int:
        since_str = since.isoformat()
        count = 0
        for record in self.codes.values():
            if record["email"] == email and record["created_at"] >= since_str:
                count += 1
        return count


class FakeOrgRepository(IOrganizationRepository):
    """Minimal fake org repository for testing."""

    async def get_company_by_code(self, code: str):
        if code == "VALID":
            return MagicMock(id="company-1")
        return None

    async def get_company_by_id(self, id: str):
        return None

    async def create_company(self, data: dict):
        return MagicMock(**data)

    async def update_company(self, id: str, data: dict):
        return MagicMock(**data)

    async def list_brands(self, company_id: str):
        return []

    async def create_brand(self, data: dict):
        return data

    async def update_brand(self, id: str, data: dict):
        return data

    async def delete_brand(self, id: str):
        return True

    async def list_branches(self, brand_id=None):
        return []

    async def create_branch(self, data: dict):
        return data

    async def delete_branch(self, id: str):
        return True

    async def list_group_types(self, branch_id: str):
        return []

    async def create_group_type(self, data: dict):
        return data

    async def delete_group_type(self, id: str):
        return True

    async def list_groups(self, group_type_id=None):
        return []

    async def create_group(self, data: dict):
        return data

    async def delete_group(self, id: str):
        return True


class FakeStorageProvider(IStorageProvider):
    """In-memory fake storage provider for testing."""

    def __init__(self):
        self.files = {}

    async def upload(self, file_content: bytes, filename: str, folder: str) -> str:
        path = f"{folder}/{filename}"
        self.files[path] = file_content
        return f"https://storage.example.com/{path}"

    async def delete(self, file_path: str) -> bool:
        self.files.pop(file_path, None)
        return True

    async def get_url(self, file_path: str) -> str:
        return f"https://storage.example.com/{file_path}"


@pytest.fixture
def fake_auth_repo():
    return FakeAuthRepository()


@pytest.fixture
def fake_org_repo():
    return FakeOrgRepository()


@pytest.fixture
def fake_storage():
    return FakeStorageProvider()


@pytest.fixture
def auth_service(fake_auth_repo, fake_org_repo):
    return AuthService(auth_repo=fake_auth_repo, org_repo=fake_org_repo)


@pytest.fixture
def file_service(fake_storage):
    return FileService(storage_provider=fake_storage)


# -- Notification Channel Fakes --

class FakeNotificationChannel(INotificationChannel):
    """In-memory fake notification channel for testing."""

    def __init__(self, should_fail: bool = False):
        self.sent = []
        self.should_fail = should_fail

    async def send(self, recipient_email, title, message, context=None):
        if self.should_fail:
            raise Exception("Channel send failed")
        self.sent.append({"to": recipient_email, "title": title, "message": message})
        return True


class FakeNotificationRepository(INotificationRepository):
    """In-memory fake notification repository for testing."""

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
        data["id"] = f"notif-{len(self.notifications) + 1}"
        data["is_read"] = False
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.notifications.append(data)
        return data


class FakeCommentRepository(ICommentRepository):
    """In-memory fake comment repository for testing."""

    def __init__(self):
        self.comments = []
        self._counter = 0

    async def list_by_assignment(self, assignment_id):
        return [c for c in self.comments if c["assignment_id"] == assignment_id]

    async def create(self, data):
        self._counter += 1
        data["id"] = f"comment-{self._counter}"
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.comments.append(data)
        return data

    async def delete(self, comment_id):
        self.comments = [c for c in self.comments if c["id"] != comment_id]
        return True


class FakeAssignmentRepository(IAssignmentRepository):
    """In-memory fake assignment repository for testing."""

    def __init__(self):
        self.assignments = {}

    async def get_by_id(self, id):
        return self.assignments.get(id)

    async def list(self, filters):
        return list(self.assignments.values())

    async def create(self, data):
        self.assignments[data["id"]] = data
        return data

    async def update(self, id, data):
        if id in self.assignments:
            self.assignments[id].update(data)
        return self.assignments.get(id, {})

    async def delete(self, id):
        self.assignments.pop(id, None)
        return True

    async def add_assignees(self, assignment_id, user_ids):
        return [{"assignment_id": assignment_id, "user_id": uid} for uid in user_ids]

    async def remove_assignee(self, assignment_id, user_id):
        return True

    async def get_assignees(self, assignment_id):
        assignment = self.assignments.get(assignment_id, {})
        return assignment.get("assignees", [])


@pytest.fixture
def fake_notification_channel():
    return FakeNotificationChannel()


@pytest.fixture
def fake_notification_repo():
    return FakeNotificationRepository()


@pytest.fixture
def fake_comment_repo():
    return FakeCommentRepository()


@pytest.fixture
def fake_assignment_repo():
    return FakeAssignmentRepository()


@pytest.fixture
def notification_dispatcher(fake_notification_channel):
    return NotificationDispatcher(channels=[fake_notification_channel])


@pytest.fixture
def notification_service(fake_notification_repo, fake_auth_repo, notification_dispatcher):
    return NotificationService(
        notification_repo=fake_notification_repo,
        auth_repo=fake_auth_repo,
        dispatcher=notification_dispatcher,
    )


@pytest.fixture
def comment_service(fake_comment_repo, fake_assignment_repo, notification_service):
    return CommentService(
        comment_repo=fake_comment_repo,
        assignment_repo=fake_assignment_repo,
        notification_service=notification_service,
    )
