from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ── Company ─────────────────────────────────────────

class CompanyBase(BaseModel):
    code: str
    name: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True


# ── Brand ───────────────────────────────────────────

class BrandBase(BaseModel):
    company_id: str
    name: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: str
    created_at: datetime
    class Config: from_attributes = True


# ── Branch ──────────────────────────────────────────

class BranchBase(BaseModel):
    brand_id: str
    name: str
    address: Optional[str] = None

class BranchCreate(BranchBase):
    pass

class Branch(BranchBase):
    id: str
    created_at: datetime
    class Config: from_attributes = True


# ── GroupType ───────────────────────────────────────

class GroupTypeBase(BaseModel):
    branch_id: str
    priority: int
    label: str

class GroupTypeCreate(GroupTypeBase):
    pass

class GroupType(GroupTypeBase):
    id: str
    created_at: datetime
    class Config: from_attributes = True


# ── Group ───────────────────────────────────────────

class GroupBase(BaseModel):
    group_type_id: str
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: str
    created_at: datetime
    class Config: from_attributes = True
