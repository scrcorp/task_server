from typing import List
from app.repositories.opinion import IOpinionRepository
from app.schemas.opinion import Opinion, OpinionCreate


class OpinionService:
    def __init__(self, opinion_repo: IOpinionRepository):
        self.opinion_repo = opinion_repo

    async def create_opinion(self, user_id: str, company_id: str, body: OpinionCreate) -> Opinion:
        data = {
            "user_id": user_id,
            "company_id": company_id,
            "content": body.content,
            "status": "submitted",
        }
        record = await self.opinion_repo.create(data)
        return Opinion(**record)

    async def get_my_opinions(self, user_id: str, company_id: str) -> List[Opinion]:
        records = await self.opinion_repo.list_by_user(user_id, company_id)
        return [Opinion(**r) for r in records]
