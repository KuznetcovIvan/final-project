from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.company import UserCompanyMembership
from app.models.motivation import Rating
from app.models.task import Task
from app.schemas.motivation import RatingCreate


class CRUDRating(CRUDBase):
    async def create_for_task(self, task: Task, obj_in: RatingCreate, session: AsyncSession) -> Rating:
        data = obj_in.model_dump()
        data['task_id'] = task.id
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_user(
        self,
        user_id: int,
        session: AsyncSession,
        year: int | None = None,
        quarter: int | None = None,
        company_id: int | None = None,
    ) -> list[Rating]:
        query = select(self.model).join(Task, Task.id == self.model.task_id).where(Task.executor_id == user_id)
        if company_id is not None:
            query = query.where(Task.company_id == company_id)
        if year is not None:
            query = query.where(func.extract('year', self.model.created_at) == year)
        if quarter is not None:
            query = query.where(func.extract('quarter', self.model.created_at) == quarter)
        query = query.order_by(self.model.created_at.desc())
        query = await session.execute(query)
        return query.scalars().all()

    async def user_avg_in_company(
        self,
        membership: UserCompanyMembership,
        session: AsyncSession,
        year: int | None = None,
        quarter: int | None = None,
    ) -> float:
        query = (
            select(func.avg(self.model.avg))
            .join(Task, Task.id == self.model.task_id)
            .where(Task.executor_id == membership.user_id, Task.company_id == membership.company_id)
        )
        if year is not None:
            query = query.where(func.extract('year', self.model.created_at) == year)
        if quarter is not None:
            query = query.where(func.extract('quarter', self.model.created_at) == quarter)
        result = await session.execute(query)
        return result.scalar() or 0.0

    async def user_department_avg_in_company(
        self,
        membership: UserCompanyMembership,
        session: AsyncSession,
        year: int | None = None,
        quarter: int | None = None,
    ) -> float:
        query = (
            select(func.avg(self.model.avg))
            .join(Task, Task.id == self.model.task_id)
            .join(
                UserCompanyMembership,
                and_(
                    UserCompanyMembership.user_id == Task.executor_id,
                    UserCompanyMembership.company_id == membership.company_id,
                    UserCompanyMembership.department_id == membership.department_id,
                ),
            )
            .where(Task.company_id == membership.company_id)
        )
        if year is not None:
            query = query.where(func.extract('year', self.model.created_at) == year)
        if quarter is not None:
            query = query.where(func.extract('quarter', self.model.created_at) == quarter)
        result = await session.execute(query)
        return result.scalar() or 0.0

    async def summary(
        self,
        membership: UserCompanyMembership,
        session: AsyncSession,
        year: int | None = None,
        quarter: int | None = None,
    ) -> tuple[list[Rating], float, float]:
        return (
            await self.get_multi_by_user(membership.user_id, session, year, quarter, membership.company_id),
            await self.user_avg_in_company(membership, session, year, quarter),
            await self.user_department_avg_in_company(membership, session, year, quarter),
        )


rating_crud = CRUDRating(Rating)
