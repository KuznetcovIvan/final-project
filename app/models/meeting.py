from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MEETING_DESC_MAX_LENGTH, MEETING_TITLE_MAX_LENGTH
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class Meeting(Base):
    title: Mapped[str] = mapped_column(String(MEETING_TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(String(MEETING_DESC_MAX_LENGTH))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)

    __table_args__ = (CheckConstraint('end_at > start_at', name='meeting_time_valid'),)

    company: Mapped['Company'] = relationship(back_populates='meetings')
    author: Mapped['User'] = relationship(back_populates='meetings_authored')
    attendees: Mapped[list['MeetingAttendee']] = relationship(back_populates='meeting')

    def __repr__(self) -> str:
        return f'Встреча "{self.title[:30]}..." начало: {self.start_at} окончание: {self.end_at}.'

    def __admin_repr__(self, request):
        return f'{self.title[:30]} ({self.start_at} - {self.end_at})'


class MeetingAttendee(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))

    __table_args__ = (UniqueConstraint('meeting_id', 'user_id', name='unique_meeting_user'),)

    meeting: Mapped['Meeting'] = relationship(back_populates='attendees')
    user: Mapped['User'] = relationship(back_populates='meetings_attendances')

    def __admin_repr__(self, request):
        return f'meeting_id={self.meeting_id}, user_id={self.user_id}'
