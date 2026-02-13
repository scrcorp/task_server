"""
Dependency Injection container.
모든 Repository/Service 인스턴스를 여기서 관리합니다.
Supabase에서 다른 구현체로 전환 시 이 파일만 수정하면 됩니다.
"""
from app.core.supabase import supabase
from app.repositories.auth import SupabaseAuthRepository, IAuthRepository
from app.repositories.user import SupabaseUserRepository
from app.repositories.task import TaskRepository
from app.repositories.organization import OrganizationRepository, IOrganizationRepository
from app.repositories.checklist_template import ChecklistTemplateRepository, IChecklistTemplateRepository
from app.repositories.feedback_notice import (
    FeedbackRepository, IFeedbackRepository,
    NoticeRepository, INoticeRepository,
)
from app.repositories.comment import CommentRepository, ICommentRepository
from app.repositories.attendance import AttendanceRepository, IAttendanceRepository
from app.repositories.opinion import OpinionRepository, IOpinionRepository
from app.repositories.notification import NotificationRepository, INotificationRepository
from app.storage.supabase import SupabaseStorageProvider
from app.storage.base import IStorageProvider

from app.services.auth_service import AuthService
from app.services.task_service import TaskService
from app.services.comment_service import CommentService
from app.services.admin_service import AdminService
from app.services.notice_service import NoticeService
from app.services.dashboard_service import DashboardService
from app.services.attendance_service import AttendanceService
from app.services.opinion_service import OpinionService
from app.services.notification_service import NotificationService
from app.services.file_service import FileService
from app.services.user_service import UserService


# ── Repository Instances ──────────────────────────────────
# Supabase를 교체하려면 여기의 구현체만 바꾸면 됩니다.

def get_auth_repo() -> IAuthRepository:
    return SupabaseAuthRepository(supabase)

def get_user_repo() -> SupabaseUserRepository:
    return SupabaseUserRepository()

def get_task_repo() -> TaskRepository:
    return TaskRepository()

def get_org_repo() -> IOrganizationRepository:
    return OrganizationRepository()

def get_template_repo() -> IChecklistTemplateRepository:
    return ChecklistTemplateRepository()

def get_feedback_repo() -> IFeedbackRepository:
    return FeedbackRepository()

def get_notice_repo() -> INoticeRepository:
    return NoticeRepository()

def get_comment_repo() -> ICommentRepository:
    return CommentRepository()

def get_attendance_repo() -> IAttendanceRepository:
    return AttendanceRepository()

def get_opinion_repo() -> IOpinionRepository:
    return OpinionRepository()

def get_notification_repo() -> INotificationRepository:
    return NotificationRepository()

def get_storage_provider() -> IStorageProvider:
    return SupabaseStorageProvider()


# ── Service Factories ─────────────────────────────────────

def get_auth_service() -> AuthService:
    return AuthService(auth_repo=get_auth_repo(), user_repo=get_user_repo())

def get_task_service() -> TaskService:
    return TaskService(task_repo=get_task_repo())

def get_comment_service() -> CommentService:
    return CommentService(comment_repo=get_comment_repo())

def get_admin_service() -> AdminService:
    return AdminService(
        user_repo=get_user_repo(),
        org_repo=get_org_repo(),
        template_repo=get_template_repo(),
        task_repo=get_task_repo(),
        feedback_repo=get_feedback_repo(),
        notice_repo=get_notice_repo(),
    )

def get_notice_service() -> NoticeService:
    return NoticeService(notice_repo=get_notice_repo())

def get_dashboard_service() -> DashboardService:
    return DashboardService(task_repo=get_task_repo(), notice_repo=get_notice_repo())

def get_attendance_service() -> AttendanceService:
    return AttendanceService(attendance_repo=get_attendance_repo())

def get_opinion_service() -> OpinionService:
    return OpinionService(opinion_repo=get_opinion_repo())

def get_notification_service() -> NotificationService:
    return NotificationService(notification_repo=get_notification_repo())

def get_file_service() -> FileService:
    return FileService(storage_provider=get_storage_provider())

def get_user_service() -> UserService:
    return UserService(user_repo=get_user_repo(), auth_repo=get_auth_repo())
