import uuid
import mimetypes

from app.storage.base import IStorageProvider
from app.core.config import settings


def _get_content_type(filename: str) -> str:
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


def _get_allowed_extensions() -> set:
    return {ext.strip().lower() for ext in settings.ALLOWED_FILE_EXTENSIONS.split(",")}


class FileService:
    def __init__(self, storage_provider: IStorageProvider):
        self.storage = storage_provider

    async def upload_file(self, file_content: bytes, original_filename: str, folder: str) -> dict:
        # Validate file size
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_content) > max_bytes:
            raise ValueError(f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit.")

        # Validate file extension
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        if not ext or ext not in _get_allowed_extensions():
            raise ValueError(f"File type '.{ext}' is not allowed.")

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex}.{ext}"

        # Upload
        url = await self.storage.upload(file_content, unique_name, folder)

        return {
            "file_url": url,
            "file_name": unique_name,
            "file_size": len(file_content),
            "content_type": _get_content_type(original_filename),
        }

    async def delete_file(self, file_path: str) -> bool:
        return await self.storage.delete(file_path)

    async def get_presigned_url(self, file_path: str) -> str:
        return await self.storage.get_url(file_path)
