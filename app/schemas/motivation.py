from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingBase(BaseModel):
    timeliness: int = Field(..., ge=1, le=5)
    completeness: int = Field(..., ge=1, le=5)
    quality: int = Field(..., ge=1, le=5)


class RatingCreate(RatingBase):
    pass


class RatingRead(RatingBase):
    task_id: int
    avg: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingsSummary(BaseModel):
    items: list[RatingRead]
    user_avg: float
    department_avg: float

    model_config = ConfigDict(from_attributes=True)
