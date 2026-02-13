from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
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
    company_id: str
    role: UserRole = UserRole.STAFF
    status: UserStatus = UserStatus.PENDING
    language: str = "en"
    profile_image: Optional[str] = None
    email_verified: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None
    profile_image: Optional[str] = None
    language: Optional[str] = None


class User(UserBase):
    id: str
    join_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config: from_attributes = True
