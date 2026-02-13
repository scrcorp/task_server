from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.services.admin_service import AdminService
from app.schemas.user import User, UserRole
from app.core.security import require_role, get_current_user
from app.core.dependencies import get_admin_service

router = APIRouter(dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))])


# ── Request Schemas ──────────────────────────────────

class BrandCreateRequest(BaseModel):
    name: str

class BranchCreateRequest(BaseModel):
    brand_id: str
    name: str
    address: Optional[str] = None

class GroupTypeCreateRequest(BaseModel):
    branch_id: str
    priority: int
    label: str

class GroupCreateRequest(BaseModel):
    group_type_id: str
    name: str

class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None

class FeedbackCreateRequest(BaseModel):
    content: str
    assignment_id: Optional[str] = None
    branch_id: Optional[str] = None
    target_user_id: Optional[str] = None


# ── Staff Management ─────────────────────────────────

@router.get("/staff/pending", response_model=List[User])
async def get_pending_staff(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    return await service.get_pending_staff(current_user.company_id)

@router.patch("/staff/{user_id}/approve", response_model=User)
async def approve_staff(user_id: str, service: AdminService = Depends(get_admin_service)):
    return await service.approve_staff(user_id)

@router.patch("/staff/{user_id}/reject", response_model=User)
async def reject_staff(user_id: str, service: AdminService = Depends(get_admin_service)):
    return await service.reject_staff(user_id)


# ── Company ──────────────────────────────────────────

@router.get("/company")
async def get_company(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    return await service.get_company(current_user.company_id)

@router.patch("/company")
async def update_company(
    body: CompanyUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    data = body.model_dump(exclude_unset=True)
    return await service.update_company(current_user.company_id, data)


# ── Brands ───────────────────────────────────────────

@router.get("/brands")
async def list_brands(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    return await service.list_brands(current_user.company_id)

@router.post("/brands", status_code=201)
async def create_brand(
    body: BrandCreateRequest,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    return await service.create_brand({"company_id": current_user.company_id, "name": body.name})

@router.patch("/brands/{brand_id}")
async def update_brand(brand_id: str, body: BrandCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.update_brand(brand_id, {"name": body.name})

@router.delete("/brands/{brand_id}")
async def delete_brand(brand_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_brand(brand_id)
    return {"message": "Brand deleted."}


# ── Branches ─────────────────────────────────────────

@router.get("/branches")
async def list_branches(brand_id: Optional[str] = None, service: AdminService = Depends(get_admin_service)):
    return await service.list_branches(brand_id)

@router.post("/branches", status_code=201)
async def create_branch(body: BranchCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.create_branch(body.model_dump())

@router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_branch(branch_id)
    return {"message": "Branch deleted."}


# ── Group Types ──────────────────────────────────────

@router.get("/branches/{branch_id}/group-types")
async def list_group_types(branch_id: str, service: AdminService = Depends(get_admin_service)):
    return await service.list_group_types(branch_id)

@router.post("/group-types", status_code=201)
async def create_group_type(body: GroupTypeCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.create_group_type(body.model_dump())

@router.delete("/group-types/{group_type_id}")
async def delete_group_type(group_type_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_group_type(group_type_id)
    return {"message": "Group type deleted."}


# ── Groups ───────────────────────────────────────────

@router.get("/group-types/{group_type_id}/groups")
async def list_groups(group_type_id: str, service: AdminService = Depends(get_admin_service)):
    return await service.list_groups(group_type_id)

@router.post("/groups", status_code=201)
async def create_group(body: GroupCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.create_group(body.model_dump())

@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_group(group_id)
    return {"message": "Group deleted."}


# ── Checklist Templates ─────────────────────────────

@router.post("/checklist-templates", status_code=201)
async def create_template(
    data: dict,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    data["company_id"] = current_user.company_id
    return await service.create_checklist_template(data)

@router.get("/checklist-templates")
async def list_templates(
    branch_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    return await service.list_checklist_templates(current_user.company_id, branch_id)


# ── Dashboard ────────────────────────────────────────

@router.get("/dashboard/checklist-compliance")
async def get_compliance(branch_id: str, date: str, service: AdminService = Depends(get_admin_service)):
    return await service.get_compliance_summary(branch_id, date)


# ── Feedbacks ────────────────────────────────────────

@router.get("/feedbacks")
async def list_feedbacks(
    target_user_id: Optional[str] = None,
    assignment_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    return await service.list_feedbacks(current_user.company_id, {
        "target_user_id": target_user_id,
        "assignment_id": assignment_id,
    })

@router.post("/feedbacks", status_code=201)
async def create_feedback(
    body: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    data = body.model_dump()
    data["company_id"] = current_user.company_id
    data["author_id"] = current_user.id
    return await service.create_feedback(data)
