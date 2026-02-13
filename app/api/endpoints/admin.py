from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.services.admin_service import AdminService
from app.schemas.user import User, UserRole
from app.core.security import require_role
from app.core.dependencies import get_admin_service

router = APIRouter(dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))])


# ── Request Schemas ──────────────────────────────────

class ApproveStaffRequest(BaseModel):
    group_id: str

class BrandCreateRequest(BaseModel):
    name: str

class BranchCreateRequest(BaseModel):
    brand_id: str
    name: str
    address: Optional[str] = None

class GroupCreateRequest(BaseModel):
    branch_id: str
    name: str


# ── Staff Management ─────────────────────────────────

@router.get("/staff/pending", response_model=List[User])
async def get_pending_staff(service: AdminService = Depends(get_admin_service)):
    return await service.get_pending_staff()

@router.patch("/staff/{user_id}/approve", response_model=User)
async def approve_staff(user_id: str, body: ApproveStaffRequest, service: AdminService = Depends(get_admin_service)):
    return await service.approve_staff(user_id, body.group_id)

@router.patch("/staff/{user_id}/reject", response_model=User)
async def reject_staff(user_id: str, service: AdminService = Depends(get_admin_service)):
    return await service.reject_staff(user_id)


# ── Organization: Brands ─────────────────────────────

@router.get("/brands")
async def list_brands(service: AdminService = Depends(get_admin_service)):
    return await service.list_brands()

@router.post("/brands", status_code=201)
async def create_brand(body: BrandCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.create_brand({"name": body.name})

@router.patch("/brands/{brand_id}")
async def update_brand(brand_id: str, body: BrandCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.update_brand(brand_id, {"name": body.name})

@router.delete("/brands/{brand_id}")
async def delete_brand(brand_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_brand(brand_id)
    return {"message": "브랜드가 삭제되었습니다."}


# ── Organization: Branches ───────────────────────────

@router.get("/branches")
async def list_branches(brand_id: Optional[str] = None, service: AdminService = Depends(get_admin_service)):
    return await service.list_branches(brand_id)

@router.post("/branches", status_code=201)
async def create_branch(body: BranchCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.create_branch(body.model_dump())

@router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_branch(branch_id)
    return {"message": "지점이 삭제되었습니다."}


# ── Organization: Groups ─────────────────────────────

@router.get("/groups")
async def list_groups(branch_id: Optional[str] = None, service: AdminService = Depends(get_admin_service)):
    return await service.list_groups(branch_id)

@router.post("/groups", status_code=201)
async def create_group(body: GroupCreateRequest, service: AdminService = Depends(get_admin_service)):
    return await service.create_group(body.model_dump())

@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, service: AdminService = Depends(get_admin_service)):
    await service.delete_group(group_id)
    return {"message": "그룹이 삭제되었습니다."}


# ── Checklist Templates ──────────────────────────────

@router.post("/checklist-templates", status_code=201)
async def create_template(data: dict, service: AdminService = Depends(get_admin_service)):
    return await service.create_checklist_template(data)

@router.get("/checklist-templates")
async def list_templates(
    brand_id: Optional[str] = None,
    group_id: Optional[str] = None,
    service: AdminService = Depends(get_admin_service),
):
    return await service.list_checklist_templates(brand_id, group_id)


# ── Dashboard ────────────────────────────────────────

@router.get("/dashboard/checklist-compliance")
async def get_compliance(branch_id: str, date: str, service: AdminService = Depends(get_admin_service)):
    return await service.get_compliance_summary(branch_id, date)


# ── Feedbacks ────────────────────────────────────────

@router.get("/feedbacks")
async def list_feedbacks(
    target_user_id: Optional[str] = None,
    task_id: Optional[str] = None,
    service: AdminService = Depends(get_admin_service),
):
    return await service.list_feedbacks({
        "target_user_id": target_user_id,
        "task_id": task_id,
    })

@router.post("/feedbacks", status_code=201)
async def create_feedback(data: dict, service: AdminService = Depends(get_admin_service)):
    return await service.create_feedback(data)
