from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import (
    COMPANY_NAME_MAX_LENGTH,
    DEPARTMENT_NAME_MAX_LENGTH,
    NEWS_BODY_MAX_LENGTH,
    NEWS_TITLE_MAX_LENGTH,
)
from app.models.company import UserRole

FIELD_CANT_BE_EMPTY = 'Поле не может быть пустым!'
DATE_CANT_BE_IN_PAST = 'Нельзя опубликовать новость в прошлом'


class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=COMPANY_NAME_MAX_LENGTH)


class CompanyRead(CompanyCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, max_length=COMPANY_NAME_MAX_LENGTH)

    @field_validator('name')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value


class DepartmentCreate(BaseModel):
    name: str = Field(..., max_length=DEPARTMENT_NAME_MAX_LENGTH)
    parent_id: int | None = None


class DepartmentRead(DepartmentCreate):
    id: int
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=DEPARTMENT_NAME_MAX_LENGTH)
    parent_id: int | None = None

    @field_validator('name')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value


class CompanyMembershipBase(BaseModel):
    company_id: int
    department_id: int | None = None
    manager_id: int | None = None
    role: UserRole


class CompanyMembershipCreate(CompanyMembershipBase):
    user_id: int


class CompanyMembershipRead(CompanyMembershipBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CompanyMembershipUpdate(BaseModel):
    role: UserRole | None = None
    department_id: int | None = None
    manager_id: int | None = None

    @field_validator('role')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value


class CompanyNewsBase(BaseModel):
    title: str = Field(..., max_length=NEWS_TITLE_MAX_LENGTH)
    body: str = Field(..., max_length=NEWS_BODY_MAX_LENGTH)
    published_at: datetime = Field(default_factory=datetime.now)

    @field_validator('title', 'body', 'published_at')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value

    @field_validator('published_at')
    def check_publish_datetime(cls, value):
        if value.date() < datetime.now().date():
            raise ValueError(DATE_CANT_BE_IN_PAST)
        return value


class CompanyNewsCreate(CompanyNewsBase):
    pass


class CompanyNewsRead(CompanyNewsBase):
    id: int
    company_id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class CompanyNewsUpdate(CompanyNewsBase):
    title: str | None = Field(None, max_length=NEWS_TITLE_MAX_LENGTH)
    body: str | None = Field(None, max_length=NEWS_BODY_MAX_LENGTH)
    published_at: datetime | None = None
