from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from app.services.file_service import FileService
from app.core.dependencies import get_file_service
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


# -- Request Schemas --

class PresignedUrlRequest(BaseModel):
    file_path: str


class DeleteFileRequest(BaseModel):
    file_path: str


# -- Endpoints --

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query(default="uploads"),
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    content = await file.read()
    try:
        result = await service.upload_file(content, file.filename, folder)
    except ValueError as e:
        status = 413 if "size" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e))
    return result


@router.post("/presigned-url")
async def get_presigned_url(
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    url = await service.get_presigned_url(body.file_path)
    return {"url": url}


@router.delete("/delete")
async def delete_file(
    body: DeleteFileRequest,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    await service.delete_file(body.file_path)
    return {"message": "File deleted successfully."}
