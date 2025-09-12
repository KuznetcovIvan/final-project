from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Computed, DateTime, Float, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.task import Task


class Rating(Base):
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id', ondelete='CASCADE'), unique=True)
    timeliness: Mapped[int] = mapped_column(SmallInteger)
    completeness: Mapped[int] = mapped_column(SmallInteger)
    quality: Mapped[int] = mapped_column(SmallInteger)
    avg: Mapped[float] = mapped_column(Float, Computed('(timeliness + completeness + quality) / 3.0', persisted=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    task: Mapped['Task'] = relationship(back_populates='rating')
