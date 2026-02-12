from abc import ABC, abstractmethod
from typing import Optional

class IStorageProvider(ABC):
    @abstractmethod
    async def upload(self, file_content: bytes, filename: str, folder: str) -> str:
        """Upload a file and return its public URL or path."""
        pass
    
    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Delete a file from storage."""
        pass
    
    @abstractmethod
    async def get_url(self, file_path: str) -> str:
        """Get the public URL of a file."""
        pass
