from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MEETING_DESC_MAX_LENGTH, MEETING_TITLE_MAX_LENGTH
from app.core.db import Base


class Meeting(Base):
    title: Mapped[str] = mapped_column(String(MEETING_TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(String(MEETING_DESC_MAX_LENGTH))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    organizer_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)

    __table_args__ = (CheckConstraint('end_at > start_at', name='meeting_time_valid'),)


class MeetingAttendee(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))

    __table_args__ = (UniqueConstraint('meeting_id', 'user_id', name='unique_meeting_user'),)
