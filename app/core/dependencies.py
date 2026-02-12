"""
Dependency Injection container.
모든 Repository/Service 인스턴스를 여기서 관리합니다.
Supabase에서 다른 구현체로 전환 시 이 파일만 수정하면 됩니다.
"""
from app.core.supabase import supabase
from app.repositories.auth import SupabaseAuthRepository, IAuthRepository
from app.repositories.user import SupabaseUserRepository
from app.repositories.task import TaskRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.checklist_template import ChecklistTemplateRepository
from app.repositories.feedback_notice import FeedbackRepository, NoticeRepository
from app.repositories.comment import CommentRepository
from app.repositories.attendance import AttendanceRepository
from app.repositories.opinion import OpinionRepository
from app.repositories.notification import NotificationRepository
from app.storage.supabase import SupabaseStorageProvider
from app.storage.base import IStorageProvider

from app.services.task_service import TaskService
from app.services.comment_service import CommentService


# ── Repository Instances ──────────────────────────────────
# Supabase를 교체하려면 여기의 구현체만 바꾸면 됩니다.

def get_auth_repo() -> IAuthRepository:
    return SupabaseAuthRepository(supabase)

def get_user_repo() -> SupabaseUserRepository:
    return SupabaseUserRepository()

def get_task_repo() -> TaskRepository:
    return TaskRepository()

def get_org_repo() -> OrganizationRepository:
    return OrganizationRepository()

def get_template_repo() -> ChecklistTemplateRepository:
    return ChecklistTemplateRepository()

def get_feedback_repo() -> FeedbackRepository:
    return FeedbackRepository()

def get_notice_repo() -> NoticeRepository:
    return NoticeRepository()

def get_comment_repo() -> CommentRepository:
    return CommentRepository()

def get_attendance_repo() -> AttendanceRepository:
    return AttendanceRepository()

def get_opinion_repo() -> OpinionRepository:
    return OpinionRepository()

def get_notification_repo() -> NotificationRepository:
    return NotificationRepository()

def get_storage_provider() -> IStorageProvider:
    return SupabaseStorageProvider()


# ── Service Factories ─────────────────────────────────────

def get_task_service() -> TaskService:
    return TaskService(task_repo=get_task_repo())

def get_comment_service() -> CommentService:
    return CommentService(comment_repo=get_comment_repo())
