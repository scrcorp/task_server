import uuid
from app.storage.base import IStorageProvider


class FileService:
    def __init__(self, storage_provider: IStorageProvider):
        self.storage = storage_provider

    async def upload_file(self, file_content: bytes, original_filename: str, folder: str) -> dict:
        ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
        unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

        url = await self.storage.upload(file_content, unique_name, folder)
        return {
            "filename": unique_name,
            "original_filename": original_filename,
            "url": url,
            "folder": folder,
        }

    async def get_presigned_url(self, file_path: str) -> str:
        return self.storage.get_url(file_path)
