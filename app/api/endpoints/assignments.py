from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, Comment
from app.services.assignment_service import AssignmentService
from app.services.comment_service import CommentService
from app.models.enums import AssignmentStatus
from app.core.security import get_current_user
from app.core.dependencies import get_assignment_service, get_comment_service
from app.schemas.user import User

router = APIRouter()


# ── Request Schemas ──────────────────────────────────

class CommentCreateRequest(BaseModel):
    content: Optional[str] = None
    content_type: str = "text"
    attachments: Optional[List[dict]] = None

class AssigneeUpdateRequest(BaseModel):
    user_ids: List[str]

class StatusUpdateRequest(BaseModel):
    status: AssignmentStatus


# ── Assignment CRUD ──────────────────────────────────

@router.get("/")
async def list_assignments(
    status: Optional[str] = None,
    branch_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    filters = {}
    if status:
        filters["status"] = status
    if branch_id:
        filters["branch_id"] = branch_id
    return await service.list_assignments(current_user.company_id, filters)


@router.get("/my")
async def get_my_assignments(
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    return await service.get_my_assignments(current_user.id, current_user.company_id)


@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    assignment = await service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return assignment


@router.post("/", status_code=201)
async def create_assignment(
    body: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    data = body.model_dump(exclude={"assignee_ids"})
    data["company_id"] = current_user.company_id
    data["created_by"] = current_user.id
    # Convert enums to values
    data["priority"] = data["priority"].value if hasattr(data["priority"], "value") else data["priority"]
    data["status"] = data["status"].value if hasattr(data["status"], "value") else data["status"]
    return await service.create_assignment(data, body.assignee_ids)


@router.patch("/{assignment_id}")
async def update_assignment(
    assignment_id: str,
    body: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    data = body.model_dump(exclude_unset=True)
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value
    if "priority" in data and hasattr(data["priority"], "value"):
        data["priority"] = data["priority"].value
    return await service.update_assignment(assignment_id, data)


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    await service.delete_assignment(assignment_id)
    return {"message": "Assignment deleted."}


@router.patch("/{assignment_id}/status")
async def update_status(
    assignment_id: str,
    body: StatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    return await service.update_status(assignment_id, body.status.value)


# ── Assignees ────────────────────────────────────────

@router.post("/{assignment_id}/assignees", status_code=201)
async def add_assignees(
    assignment_id: str,
    body: AssigneeUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    result = await service.add_assignees(assignment_id, body.user_ids)
    return {"message": "Assignees added.", "data": result}


@router.delete("/{assignment_id}/assignees/{user_id}")
async def remove_assignee(
    assignment_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
):
    await service.remove_assignee(assignment_id, user_id)
    return {"message": "Assignee removed."}


# ── Comments ─────────────────────────────────────────

@router.get("/{assignment_id}/comments", response_model=List[Comment])
async def list_comments(
    assignment_id: str,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.list_comments(assignment_id)


@router.post("/{assignment_id}/comments", status_code=201)
async def create_comment(
    assignment_id: str,
    body: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.create_comment(
        assignment_id=assignment_id,
        user_id=current_user.id,
        content=body.content,
        content_type=body.content_type,
        attachments=body.attachments,
        user_name=current_user.full_name,
        is_manager=current_user.role.value in ("manager", "admin"),
    )


@router.delete("/{assignment_id}/comments/{comment_id}")
async def delete_comment(
    assignment_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    await service.delete_comment(comment_id)
    return {"message": "Comment deleted."}
