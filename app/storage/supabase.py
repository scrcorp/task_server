import mimetypes

from app.storage.base import IStorageProvider
from app.core.supabase import supabase
from app.core.config import settings


class SupabaseStorageProvider(IStorageProvider):
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or settings.STORAGE_BUCKET_NAME

    async def upload(self, file_content: bytes, filename: str, folder: str) -> str:
        file_path = f"{folder}/{filename}"
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        supabase.storage.from_(self.bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": content_type},
        )
        return await self.get_url(file_path)

    async def delete(self, file_path: str) -> bool:
        supabase.storage.from_(self.bucket_name).remove([file_path])
        return True

    async def get_url(self, file_path: str) -> str:
        res = supabase.storage.from_(self.bucket_name).get_public_url(file_path)
        return res
