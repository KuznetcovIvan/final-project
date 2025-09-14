from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.meeting import Meeting, MeetingAttendee
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

    async def get_user_meetings_at_the_same_time(
        self, user_id: int, start: datetime, end: datetime, session: AsyncSession, company_id: int | None = None
    ):
        query = (
            select(self.model)
            .join(MeetingAttendee, MeetingAttendee.meeting_id == self.model.id)
            .where(self.model.start_at < end, self.model.end_at > start, MeetingAttendee.user_id == user_id)
        )
        if company_id is not None:
            query = query.where(self.model.company_id == company_id)
        result = await session.execute(query)
        return result.scalars().all()


class CRUDMeetingAttendee(CRUDBase):
    async def create(self, meeting_id: int, user_id: int, session: AsyncSession):
        db_obj = self.model(meeting_id=meeting_id, user_id=user_id)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_users_from_meeting_attend(self, meeting_id: int, session: AsyncSession):
        result = await session.execute(
            select(User)
            .join_from(User, self.model, self.model.user_id == User.id)
            .where(self.model.meeting_id == meeting_id)
        )
        return result.scalars().all()


meeting_crud = CRUDMeeting(Meeting)
attendee_crud = CRUDMeetingAttendee(MeetingAttendee)
