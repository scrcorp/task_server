from typing import List, Optional
from app.repositories.feedback_notice import INoticeRepository
from app.schemas.notice import Notice, NoticeCreate


class NoticeService:
    def __init__(self, notice_repo: INoticeRepository):
        self.notice_repo = notice_repo

    async def list_notices(self, limit: Optional[int] = None) -> List[dict]:
        return await self.notice_repo.list_notices(limit=limit)

    async def get_notice(self, notice_id: str) -> Optional[dict]:
        return await self.notice_repo.get_notice(notice_id)

    async def confirm_notice(self, notice_id: str, user_id: str) -> dict:
        return await self.notice_repo.confirm_notice(notice_id, user_id)

    async def create_notice(self, body: NoticeCreate, author_id: str) -> dict:
        data = {
            "title": body.title,
            "content": body.content,
            "author_id": author_id,
        }
        if hasattr(body, 'is_important') and body.is_important is not None:
            data["is_important"] = body.is_important
        return await self.notice_repo.create_notice(data)

    async def update_notice(self, notice_id: str, data: dict) -> dict:
        return await self.notice_repo.update_notice(notice_id, data)

    async def delete_notice(self, notice_id: str) -> bool:
        return await self.notice_repo.delete_notice(notice_id)
