from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Computed, DateTime, Float, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.task import Task


class Rating(Base):
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id', ondelete='CASCADE'), unique=True)
    timeliness: Mapped[int] = mapped_column(SmallInteger)
    completeness: Mapped[int] = mapped_column(SmallInteger)
    quality: Mapped[int] = mapped_column(SmallInteger)
    avg: Mapped[float] = mapped_column(
        Float, Computed('ROUND((timeliness + completeness + quality) / 3.0, 2)', persisted=True)
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (
        CheckConstraint('timeliness BETWEEN 1 AND 5', name='timeliness_1-5'),
        CheckConstraint('completeness BETWEEN 1 AND 5', name='completeness_1-5'),
        CheckConstraint('quality BETWEEN 1 AND 5', name='quality_1-5'),
    )

    task: Mapped['Task'] = relationship(back_populates='rating')

    def __admin_repr__(self, request):
        return f'task_id={self.task_id} - avg={self.avg}'
