from enum import Enum


class Priority(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"


class AssignmentStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class AttendanceStatus(str, Enum):
    NOT_STARTED = "not_started"
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    COMPLETED = "completed"


class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    NOTICE = "notice"
    FEEDBACK = "feedback"
    COMMENT = "comment"
    SYSTEM = "system"


class OpinionStatus(str, Enum):
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"


class VerificationType(str, Enum):
    NONE = "none"
    PHOTO = "photo"
    SIGNATURE = "signature"
