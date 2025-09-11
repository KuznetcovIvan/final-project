from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import MEETING_DESC_MAX_LENGTH, MEETING_TITLE_MAX_LENGTH

INVALID_DATES = 'Дата окончания не может быть раньше даты начала!'
FIELD_CANT_BE_EMPTY = 'Поле не может быть пустым!'
BOTH_OR_NONE_DATES = 'Необходимо указать обе даты, либо не указывать ни одной!'


class MeetingBase(BaseModel):
    title: str = Field(..., max_length=MEETING_TITLE_MAX_LENGTH)
    description: str = Field(..., max_length=MEETING_DESC_MAX_LENGTH)
    start_at: datetime
    end_at: datetime


class MeetingCreate(MeetingBase):
    @model_validator(mode='after')
    def check_dates(cls, values):
        if values.end_at < values.start_at:
            raise ValueError(INVALID_DATES)
        return values


class MeetingUpdate(BaseModel):
    title: str | None = Field(None, max_length=MEETING_TITLE_MAX_LENGTH)
    description: str | None = Field(None, max_length=MEETING_DESC_MAX_LENGTH)
    start_at: datetime | None = None
    end_at: datetime | None = None

    @field_validator('title', 'description', 'start_at', 'end_at')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value

    @model_validator(mode='after')
    def check_dates(cls, values):
        if (values.start_at is None) != (values.end_at is None):
            raise ValueError(BOTH_OR_NONE_DATES)
        if values.start_at and values.end_at and values.end_at < values.start_at:
            raise ValueError(INVALID_DATES)
        return values


class MeetingRead(MeetingBase):
    id: int
    company_id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)
