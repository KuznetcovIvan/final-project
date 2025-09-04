from datetime import datetime
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import COMPANY_NAME_MAX_LENGTH, DEPARTMENT_NAME_MAX_LENGTH
from app.core.db import Base


class UserRole(StrEnum):
    USER = 'user'
    MANAGER = 'manager'
    ADMIN = 'admin'


class Company(Base):
    name: Mapped[str] = mapped_column(String(COMPANY_NAME_MAX_LENGTH), unique=True)


class Department(Base):
    __table_args__ = (UniqueConstraint('name', 'company_id', name='unique_department_company'),)

    name: Mapped[str] = mapped_column(String(DEPARTMENT_NAME_MAX_LENGTH))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('department.id', ondelete='SET NULL'))


class UserCompanyMembership(Base):
    __table_args__ = (UniqueConstraint('user_id', 'company_id', name='unique_user_company'),)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    department_id: Mapped[int | None] = mapped_column(ForeignKey('department.id', ondelete='SET NULL'))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey('user.id', ondelete='SET NULL'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)


class CompanyNews(Base):
    __table_args__ = (UniqueConstraint('title', 'published_at', name='unique_title_published'),)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(String(4000))
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    published_at: Mapped[datetime] = mapped_column(default=datetime.now)


class Invite(Base):
    code: Mapped[str] = mapped_column(String(6), unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    department_id: Mapped[int | None] = mapped_column(ForeignKey('department.id', ondelete='SET NULL'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    created_by: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
