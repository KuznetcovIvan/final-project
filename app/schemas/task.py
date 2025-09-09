from pydantic import BaseModel, ConfigDict, field_validator

from app.models.task import TaskStatus

FIELD_CANT_BE_EMPTY = 'Поле не может быть пустым!'


class TaskBase(BaseModel):
    title: str
    body: str


class TaskCreate(TaskBase):
    executor_id: int
    status: TaskStatus = TaskStatus.TODO


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

    @field_validator('title', 'body', 'status')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value


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
