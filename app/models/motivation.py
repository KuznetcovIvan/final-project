from datetime import datetime

from sqlalchemy import Computed, DateTime, Float, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Rating(Base):
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id', ondelete='CASCADE'), unique=True)

    timeliness: Mapped[int] = mapped_column(SmallInteger)
    completeness: Mapped[int] = mapped_column(SmallInteger)
    quality: Mapped[int] = mapped_column(SmallInteger)

    avg: Mapped[float] = mapped_column(Float, Computed('(timeliness + completeness + quality) / 3.0', persisted=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
