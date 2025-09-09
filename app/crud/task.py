from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.task import Task, TaskComment
from app.models.user import User


class CRUDTask(CRUDBase):
    async def create_for_company(self, obj_in, company_id: int, session: AsyncSession, author: User):
        data = obj_in.model_dump()
        data['company_id'] = company_id
        data['author_id'] = author.id
        db_obj = Task(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


class CRUDCommentTask(CRUDBase):
    pass


task_crud = CRUDTask(Task)
task_comment_crud = CRUDCommentTask(TaskComment)
