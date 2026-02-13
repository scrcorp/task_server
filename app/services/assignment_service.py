from typing import List, Optional
from app.repositories.assignment import IAssignmentRepository


class AssignmentService:
    def __init__(self, assignment_repo: IAssignmentRepository):
        self.assignment_repo = assignment_repo

    async def list_assignments(self, company_id: str, filters: Optional[dict] = None) -> List[dict]:
        all_filters = {"company_id": company_id}
        if filters:
            all_filters.update(filters)
        return await self.assignment_repo.list(all_filters)

    async def get_my_assignments(self, user_id: str, company_id: str) -> List[dict]:
        return await self.assignment_repo.list_by_assignee(user_id, company_id)

    async def get_assignment(self, assignment_id: str) -> Optional[dict]:
        return await self.assignment_repo.get_by_id(assignment_id)

    async def create_assignment(self, data: dict, assignee_ids: List[str]) -> dict:
        assignment = await self.assignment_repo.create(data)
        if assignee_ids:
            await self.assignment_repo.add_assignees(assignment["id"], assignee_ids)
        return await self.assignment_repo.get_by_id(assignment["id"])

    async def update_assignment(self, assignment_id: str, data: dict) -> dict:
        await self.assignment_repo.update(assignment_id, data)
        return await self.assignment_repo.get_by_id(assignment_id)

    async def delete_assignment(self, assignment_id: str) -> bool:
        return await self.assignment_repo.delete(assignment_id)

    async def update_status(self, assignment_id: str, status: str) -> dict:
        await self.assignment_repo.update(assignment_id, {"status": status})
        return await self.assignment_repo.get_by_id(assignment_id)

    async def add_assignees(self, assignment_id: str, user_ids: List[str]) -> List[dict]:
        return await self.assignment_repo.add_assignees(assignment_id, user_ids)

    async def remove_assignee(self, assignment_id: str, user_id: str) -> bool:
        return await self.assignment_repo.remove_assignee(assignment_id, user_id)
