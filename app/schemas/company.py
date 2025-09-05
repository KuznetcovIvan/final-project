from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import COMPANY_NAME_MAX_LENGTH, DEPARTMENT_NAME_MAX_LENGTH
from app.models.company import UserRole

FIELD_CANT_BE_EMPTY = 'Поле не может быть пустым!'


class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=COMPANY_NAME_MAX_LENGTH)


class CompanyRead(CompanyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, max_length=COMPANY_NAME_MAX_LENGTH)

    @field_validator('name')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value


class DepartmentCreate(BaseModel):
    name: str = Field(..., max_length=DEPARTMENT_NAME_MAX_LENGTH)
    company_name: str = Field(..., max_length=COMPANY_NAME_MAX_LENGTH)
    parent_department_name: str | None = Field(None, max_length=DEPARTMENT_NAME_MAX_LENGTH)


class DepartmentRead(DepartmentCreate):
    model_config = ConfigDict(from_attributes=True)


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=DEPARTMENT_NAME_MAX_LENGTH)

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
    model_config = ConfigDict(from_attributes=True)
