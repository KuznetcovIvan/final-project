from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserRole(StrEnum):
    USER = 'user'
    MANAGER = 'manager'
    ADMIN = 'admin'


class Company(Base):
    name: Mapped[str] = mapped_column(String(255), unique=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey('user.id'))


class Department(Base):
    name: Mapped[str] = mapped_column(String(255))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('department.id'))


class UserCompanyMembership(Base):
    __table_args__ = (UniqueConstraint('user_id', 'company_id', name='unique_user_company'),)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    department_id: Mapped[int | None] = mapped_column(ForeignKey('department.id'))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey('user.id'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name='user_role'), default=UserRole.USER)
