from enum import StrEnum

from pydantic import BaseModel

from app.schemas.company import CompanyNewsRead
from app.schemas.meeting import MeetingRead
from app.schemas.task import TaskRead


class CalendarScope(StrEnum):
    DAY = 'day'
    MONTH = 'month'
    YEAR = 'year'


class CalendarRead(BaseModel):
    scope: CalendarScope
    news: list[CompanyNewsRead]
    tasks: list[TaskRead]
    meetings: list[MeetingRead]
