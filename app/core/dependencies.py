"""
Dependency Injection container.
All Repository/Service instances are managed here.
To switch from Supabase to another implementation, modify this file only.
"""
from app.core.supabase import supabase
from app.repositories.auth import CustomAuthRepository, IAuthRepository
from app.repositories.user import SupabaseUserRepository
from app.repositories.organization import OrganizationRepository, IOrganizationRepository
from app.repositories.assignment import AssignmentRepository, IAssignmentRepository
from app.repositories.daily_checklist import DailyChecklistRepository, IDailyChecklistRepository
from app.repositories.checklist_template import ChecklistTemplateRepository, IChecklistTemplateRepository
from app.repositories.comment import CommentRepository, ICommentRepository
from app.repositories.feedback_notice import (
    FeedbackRepository, IFeedbackRepository,
    NoticeRepository, INoticeRepository,
)
from app.repositories.attendance import AttendanceRepository, IAttendanceRepository
from app.repositories.opinion import OpinionRepository, IOpinionRepository
from app.repositories.notification import NotificationRepository, INotificationRepository
from app.storage.supabase import SupabaseStorageProvider
from app.storage.base import IStorageProvider
from app.notifications.channel import EmailNotificationChannel
from app.notifications.dispatcher import NotificationDispatcher

from app.services.auth_service import AuthService
from app.services.assignment_service import AssignmentService
from app.services.daily_checklist_service import DailyChecklistService
from app.services.comment_service import CommentService
from app.services.admin_service import AdminService
from app.services.notice_service import NoticeService
from app.services.dashboard_service import DashboardService
from app.services.attendance_service import AttendanceService
from app.services.opinion_service import OpinionService
from app.services.notification_service import NotificationService
from app.services.file_service import FileService
from app.services.user_service import UserService


# -- Repository Instances --

def get_auth_repo() -> IAuthRepository:
    return CustomAuthRepository(supabase)

def get_user_repo() -> SupabaseUserRepository:
    return SupabaseUserRepository()

def get_org_repo() -> IOrganizationRepository:
    return OrganizationRepository()

def get_assignment_repo() -> IAssignmentRepository:
    return AssignmentRepository()

def get_daily_checklist_repo() -> IDailyChecklistRepository:
    return DailyChecklistRepository()

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


# -- Service Factories --

def get_auth_service() -> AuthService:
    return AuthService(
        auth_repo=get_auth_repo(),
        org_repo=get_org_repo(),
    )

def get_assignment_service() -> AssignmentService:
    return AssignmentService(assignment_repo=get_assignment_repo())

def get_daily_checklist_service() -> DailyChecklistService:
    return DailyChecklistService(
        checklist_repo=get_daily_checklist_repo(),
        template_repo=get_template_repo(),
    )

def get_comment_service() -> CommentService:
    return CommentService(
        comment_repo=get_comment_repo(),
        assignment_repo=get_assignment_repo(),
        notification_service=get_notification_service(),
    )

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

def get_notice_service() -> NoticeService:
    return NoticeService(notice_repo=get_notice_repo())

def get_dashboard_service() -> DashboardService:
    return DashboardService(
        assignment_repo=get_assignment_repo(),
        notice_repo=get_notice_repo(),
        checklist_repo=get_daily_checklist_repo(),
    )

def get_attendance_service() -> AttendanceService:
    return AttendanceService(attendance_repo=get_attendance_repo())

def get_opinion_service() -> OpinionService:
    return OpinionService(opinion_repo=get_opinion_repo())

def get_notification_dispatcher() -> NotificationDispatcher:
    return NotificationDispatcher(channels=[EmailNotificationChannel()])

def get_notification_service() -> NotificationService:
    return NotificationService(
        notification_repo=get_notification_repo(),
        auth_repo=get_auth_repo(),
        dispatcher=get_notification_dispatcher(),
    )

def get_file_service() -> FileService:
    return FileService(storage_provider=get_storage_provider())

def get_user_service() -> UserService:
    return UserService(user_repo=get_user_repo(), auth_repo=get_auth_repo())
