from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.services.admin_service import AdminService
from app.schemas.user import User, UserRole
from app.core.security import require_role

router = APIRouter(dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))])
admin_service = AdminService()

@router.get("/staff/pending", response_model=List[User])
async def get_pending_staff():
    return await admin_service.get_pending_staff()

@router.patch("/staff/{user_id}/approve", response_model=User)
async def approve_staff(user_id: str, group_id: str):
    return await admin_service.approve_staff(user_id, group_id)

# Organization Endpoints
@router.get("/brands")
async def list_brands():
    return await admin_service.org_repo.list_brands()

@router.post("/brands")
async def create_brand(name: str):
    return await admin_service.org_repo.create_brand({"name": name})

# Checklist Template Endpoints
@router.post("/checklist-templates")
async def create_template(data: dict):
    return await admin_service.create_checklist_template(data)

@router.get("/checklist-templates")
async def list_templates(brand_id: str = None, group_id: str = None):
    return await admin_service.template_repo.list_templates(brand_id, group_id)

# Dashboard Endpoints
@router.get("/dashboard/checklist-compliance")
async def get_compliance(branch_id: str, date: str):
    return await admin_service.get_compliance_summary(branch_id, date)

# Feedback Endpoints
@router.get("/feedbacks")
async def list_feedbacks(target_user_id: Optional[str] = None, task_id: Optional[str] = None):
    return await admin_service.feedback_repo.list_feedbacks({
        "target_user_id": target_user_id,
        "task_id": task_id
    })

@router.post("/feedbacks")
async def create_feedback(data: dict):
    return await admin_service.feedback_repo.create_feedback(data)
