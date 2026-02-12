from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Fetch a single record by ID."""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[dict] = None) -> List[T]:
        """Fetch a list of records with optional filtering."""
        pass
    
    @abstractmethod
    async def create(self, data: Any) -> T:
        """Create a new record."""
        pass
    
    @abstractmethod
    async def update(self, id: str, data: dict) -> T:
        """Update an existing record."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a record."""
        pass
