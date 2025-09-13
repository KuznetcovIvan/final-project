from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.task import TaskStatus

FIELD_CANT_BE_EMPTY = 'Поле не может быть пустым!'
INVALID_DATES = 'Дата завершения не может быть раньше даты начала!'
BOTH_OR_NONE_DATES = 'Необходимо указать обе даты, либо не указывать ни одной!'


class TaskBase(BaseModel):
    title: str
    body: str
    start_at: datetime
    end_at: datetime


class TaskCreate(TaskBase):
    executor_id: int
    status: TaskStatus = TaskStatus.TODO

    @model_validator(mode='after')
    def check_dates(cls, values):
        if values.end_at < values.start_at:
            raise ValueError(INVALID_DATES)
        return values


class TaskRead(TaskBase):
    id: int
    company_id: int
    author_id: int
    executor_id: int
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    status: TaskStatus | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None

    @field_validator('title', 'body', 'status', 'start_at', 'end_at')
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


class TaskCommentCreate(BaseModel):
    body: str


class TaskCommentRead(BaseModel):
    id: int
    task_id: int
    author_id: int
    body: str

    model_config = ConfigDict(from_attributes=True)


class TaskCommentUpdate(TaskCommentCreate):
    body: str
