from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.motivation import Rating
    from app.models.user import User


class TaskStatus(StrEnum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Task(Base):
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id', ondelete='CASCADE'))
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    executor_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    start_at: Mapped[datetime] = mapped_column(DateTime)
    due_at: Mapped[datetime] = mapped_column(DateTime)

    company: Mapped['Company'] = relationship(back_populates='tasks')
    author: Mapped['User'] = relationship(back_populates='tasks_authored', foreign_keys=[author_id])
    executor: Mapped['User'] = relationship(back_populates='tasks_executed', foreign_keys=[executor_id])
    comments: Mapped[list['TaskComment']] = relationship(back_populates='task')
    rating: Mapped['Rating | None'] = relationship(back_populates='task')


class TaskComment(Base):
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id', ondelete='CASCADE'))

    author: Mapped['User'] = relationship(back_populates='task_comments')
    task: Mapped['Task'] = relationship(back_populates='comments')
