from enum import Enum

class TaskType(str, Enum):
    """업무 유형: 데일리 루틴 또는 할당된 업무"""
    DAILY = "daily"
    ASSIGNED = "assigned"

class Priority(str, Enum):
    """업무 우선순위 (할당된 업무 전용)"""
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"

class TaskStatus(str, Enum):
    """업무 진행 상태"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class AttendanceStatus(str, Enum):
    """출퇴근 상태"""
    NOT_STARTED = "not_started"
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    COMPLETED = "completed"

class NotificationType(str, Enum):
    """알림 유형"""
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    NOTICE = "notice"
    FEEDBACK = "feedback"
    SYSTEM = "system"

class OpinionStatus(str, Enum):
    """건의사항 상태"""
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
