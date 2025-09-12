from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    COMPANY_NAME_MAX_LENGTH,
    DEPARTMENT_NAME_MAX_LENGTH,
    INVITE_CODE_LENGTH,
    NEWS_BODY_MAX_LENGTH,
    NEWS_TITLE_MAX_LENGTH,
)
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.task import Task
    from app.models.user import User


class UserRole(StrEnum):
    USER = 'user'
    MANAGER = 'manager'
    ADMIN = 'admin'


class Company(Base):
    name: Mapped[str] = mapped_column(String(COMPANY_NAME_MAX_LENGTH), unique=True)

    memberships: Mapped[list['UserCompanyMembership']] = relationship(back_populates='company')
    departments: Mapped[list['Department']] = relationship(back_populates='company')
    news: Mapped[list['CompanyNews']] = relationship(back_populates='company')
    invites: Mapped[list['Invite']] = relationship(back_populates='company')
    meetings: Mapped[list['Meeting']] = relationship(back_populates='company')
    tasks: Mapped[list['Task']] = relationship(back_populates='company')


class Department(Base):
    name: Mapped[str] = mapped_column(String(DEPARTMENT_NAME_MAX_LENGTH))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('department.id', ondelete='SET NULL'))

    __table_args__ = (UniqueConstraint('name', 'company_id', name='unique_department_company'),)

    company: Mapped['Company'] = relationship(back_populates='departments')
    memberships: Mapped[list['UserCompanyMembership']] = relationship(back_populates='department')
    invites: Mapped[list['Invite']] = relationship(back_populates='department')
    parent: Mapped['Department | None'] = relationship(back_populates='children', remote_side='Department.id')
    children: Mapped[list['Department']] = relationship(back_populates='parent')


class UserCompanyMembership(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    department_id: Mapped[int | None] = mapped_column(ForeignKey('department.id', ondelete='SET NULL'))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey('user.id', ondelete='SET NULL'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    __table_args__ = (UniqueConstraint('user_id', 'company_id', name='unique_user_company'),)

    user: Mapped['User'] = relationship(back_populates='memberships', foreign_keys=[user_id])
    company: Mapped['Company'] = relationship(back_populates='memberships', foreign_keys=[company_id])
    department: Mapped['Department | None'] = relationship(back_populates='memberships', foreign_keys=[department_id])
    manager: Mapped['User | None'] = relationship(back_populates='managed_memberships', foreign_keys=[manager_id])


class CompanyNews(Base):
    title: Mapped[str] = mapped_column(String(NEWS_TITLE_MAX_LENGTH))
    body: Mapped[str] = mapped_column(String(NEWS_BODY_MAX_LENGTH))
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    published_at: Mapped[datetime] = mapped_column(DateTime)

    author: Mapped['User'] = relationship(back_populates='news_posts')
    company: Mapped['Company'] = relationship(back_populates='news')


class Invite(Base):
    code: Mapped[str] = mapped_column(String(INVITE_CODE_LENGTH), unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    department_id: Mapped[int | None] = mapped_column(ForeignKey('department.id', ondelete='SET NULL'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    email: Mapped[str] = mapped_column(String(length=320))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey('user.id', ondelete='SET NULL'))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    company: Mapped['Company'] = relationship(back_populates='invites')
    department: Mapped['Department | None'] = relationship(back_populates='invites')
    manager: Mapped['User | None'] = relationship(back_populates='sent_invites')
