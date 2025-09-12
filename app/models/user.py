from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.company import CompanyNews, Invite, UserCompanyMembership
    from app.models.meeting import Meeting, MeetingAttendee
    from app.models.task import Task, TaskComment


class User(SQLAlchemyBaseUserTable[int], Base):
    memberships: Mapped[list['UserCompanyMembership']] = relationship(
        back_populates='user', foreign_keys='UserCompanyMembership.user_id'
    )
    managed_memberships: Mapped[list['UserCompanyMembership']] = relationship(
        back_populates='manager', foreign_keys='UserCompanyMembership.manager_id'
    )
    news_posts: Mapped[list['CompanyNews']] = relationship(back_populates='author')
    meetings_authored: Mapped[list['Meeting']] = relationship(back_populates='author')
    meetings_attendances: Mapped[list['MeetingAttendee']] = relationship(back_populates='user')
    tasks_authored: Mapped[list['Task']] = relationship(back_populates='author', foreign_keys='Task.author_id')
    tasks_executed: Mapped[list['Task']] = relationship(back_populates='executor', foreign_keys='Task.executor_id')
    task_comments: Mapped[list['TaskComment']] = relationship(back_populates='author')
    sent_invites: Mapped[list['Invite']] = relationship(back_populates='manager')

    def __admin_repr__(self, request):
        if self.is_superuser:
            return f'{self.email} (super)'
        return self.email
