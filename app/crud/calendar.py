from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models.company import CompanyNews
from app.models.meeting import Meeting, MeetingAttendee
from app.models.task import Task
from app.schemas.calendar import CalendarScope


class CalendarService:
    interval = {'day': text("INTERVAL '1 day'"), 'month': text("INTERVAL '1 month'"), 'year': text("INTERVAL '1 year'")}

    def __init__(self, company_id: int, user_id: int, scope: CalendarScope, session: AsyncSession):
        self.company_id = company_id
        self.user_id = user_id
        self.scope = scope.value
        self.window_start = func.date_trunc(self.scope, func.now())
        self.window_end = self.window_start + self.interval[self.scope]
        self.session = session

    async def fetch_news(self) -> list[CompanyNews]:
        news_query = (
            select(CompanyNews)
            .where(
                CompanyNews.company_id == self.company_id,
                CompanyNews.published_at >= self.window_start,
                CompanyNews.published_at < self.window_end,
            )
            .order_by(CompanyNews.published_at)
        )
        news_result = await self.session.execute(news_query)
        return news_result.scalars().all()

    async def fetch_tasks(self) -> list[Task]:
        task_query = (
            select(Task)
            .where(
                Task.company_id == self.company_id,
                Task.start_at < self.window_end,
                Task.due_at > self.window_start,
                Task.executor_id == self.user_id,
            )
            .order_by(Task.start_at)
        )
        task_result = await self.session.execute(task_query)
        return task_result.scalars().all()

    async def fetch_meetings(self) -> list[Meeting]:
        meeting_query = (
            select(Meeting)
            .where(
                Meeting.company_id == self.company_id,
                Meeting.start_at < self.window_end,
                Meeting.end_at > self.window_start,
            )
            .outerjoin(MeetingAttendee, MeetingAttendee.meeting_id == Meeting.id)
            .where(MeetingAttendee.user_id == self.user_id)
            .order_by(Meeting.start_at)
        )
        meeting_result = await self.session.execute(meeting_query)
        return meeting_result.scalars().all()
