from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.meeting import MeetingCreate


class CRUDMeeting(CRUDBase):
    async def create(self, obj_in: MeetingCreate, user: User, company_id: int, session: AsyncSession):
        data = obj_in.model_dump()
        data['author_id'] = user.id
        data['company_id'] = company_id
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_company(self, company_id: int, session: AsyncSession):
        result = await session.execute(select(self.model).where(self.model.company_id == company_id))
        return result.scalars().all()


meeting_crud = CRUDMeeting(Meeting)
