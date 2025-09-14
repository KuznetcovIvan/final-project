from sqlalchemy import select
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

    async def get_multi_by_company(self, company_id: int, session: AsyncSession):
        result = await session.execute(select(self.model).where(self.model.company_id == company_id))
        return result.scalars().all()

    async def get_by_company(self, task_id: int, company_id: int, session: AsyncSession):
        result = await session.execute(
            select(self.model).where(self.model.id == task_id, self.model.company_id == company_id)
        )
        return result.scalars().first()


class CRUDCommentTask(CRUDBase):
    async def create_for_task(self, obj_in, task_id: int, session: AsyncSession, author: User):
        data = obj_in.model_dump()
        data['task_id'] = task_id
        data['author_id'] = author.id
        db_obj = TaskComment(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_task(self, task_id: int, session: AsyncSession):
        result = await session.execute(select(self.model).where(self.model.task_id == task_id))
        return result.scalars().all()

    async def get_by_task(self, comment_id: int, task_id: int, session: AsyncSession):
        result = await session.execute(
            select(self.model).where(self.model.id == comment_id, self.model.task_id == task_id)
        )
        return result.scalars().first()


task_crud = CRUDTask(Task)
task_comment_crud = CRUDCommentTask(TaskComment)
