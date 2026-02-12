from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from app.services.file_service import FileService
from app.core.dependencies import get_storage_provider
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()


def _get_service() -> FileService:
    return FileService(storage_provider=get_storage_provider())


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query(default="uploads"),
    current_user: User = Depends(get_current_user),
):
    service = _get_service()
    try:
        content = await file.read()
        result = await service.upload_file(content, file.filename, folder)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presigned-url")
async def get_presigned_url(
    file_path: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    service = _get_service()
    try:
        url = await service.get_presigned_url(file_path)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
