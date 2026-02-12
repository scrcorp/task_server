from app.storage.base import IStorageProvider
from app.core.supabase import supabase
from app.core.config import settings

class SupabaseStorageProvider(IStorageProvider):
    def __init__(self, bucket_name: str = "task-assets"):
        self.bucket_name = bucket_name

    async def upload(self, file_content: bytes, filename: str, folder: str) -> str:
        file_path = f"{folder}/{filename}"
        # supabase-py upload is synchronous in current versions, or we can use it directly
        res = supabase.storage.from_(self.bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": "image/jpeg"} # Assuming images for now
        )
        # Note: res is usually the file path or an error.
        # To get the public URL:
        return self.get_url(file_path)

    async def delete(self, file_path: str) -> bool:
        res = supabase.storage.from_(self.bucket_name).remove([file_path])
        return True # Simplified

    def get_url(self, file_path: str) -> str:
        res = supabase.storage.from_(self.bucket_name).get_public_url(file_path)
        return res
