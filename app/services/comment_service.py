from typing import List
from app.repositories.comment import ICommentRepository
from app.schemas.task import Comment


class CommentService:
    def __init__(self, comment_repo: ICommentRepository):
        self.comment_repo = comment_repo

    async def list_comments(self, task_id: str) -> List[Comment]:
        data = await self.comment_repo.list_by_task(task_id)
        return [Comment(**item) for item in data]

    async def create_comment(self, task_id: str, user_id: str, content: str) -> Comment:
        data = {
            "task_id": task_id,
            "user_id": user_id,
            "content": content,
        }
        result = await self.comment_repo.create(data)
        return Comment(**result)

    async def delete_comment(self, comment_id: str) -> bool:
        return await self.comment_repo.delete(comment_id)
