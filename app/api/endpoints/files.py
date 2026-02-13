from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from app.services.file_service import FileService
from app.core.dependencies import get_file_service
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


# ── Request Schemas ──────────────────────────────────

class PresignedUrlRequest(BaseModel):
    file_path: str


# ── Endpoints ────────────────────────────────────────

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query(default="uploads"),
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    content = await file.read()
    result = await service.upload_file(content, file.filename, folder)
    return result


@router.post("/presigned-url")
async def get_presigned_url(
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    url = await service.get_presigned_url(body.file_path)
    return {"url": url}
