from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: str
    created_at: datetime
    class Config: from_attributes = True

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

class GroupBase(BaseModel):
    branch_id: str
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: str
    created_at: datetime
    class Config: from_attributes = True
