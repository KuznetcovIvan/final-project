from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

rating_field = Field(..., ge=1, le=5)


class RatingBase(BaseModel):
    timeliness: int = rating_field
    completeness: int = rating_field
    quality: int = rating_field


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
