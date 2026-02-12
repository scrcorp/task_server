from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.models.enums import TaskType # Just for reference if needed, but we need role enum

from enum import Enum

class UserRole(str, Enum):
    STAFF = "staff"
    MANAGER = "manager"
    ADMIN = "admin"

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    email: EmailStr
    login_id: str
    full_name: str
    role: UserRole = UserRole.STAFF
    status: UserStatus = UserStatus.PENDING
    branch_id: Optional[str] = None
    group_id: Optional[str] = None
    language: str = "ko"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None
    group_id: Optional[str] = None
    branch_id: Optional[str] = None

class User(UserBase):
    id: str
    join_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config: from_attributes = True
