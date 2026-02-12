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
