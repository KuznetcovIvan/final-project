from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import COMPANY_NAME_MAX_LENGTH, DEPARTMENT_NAME_MAX_LENGTH

FIELD_CANT_BE_EMPTY = 'Поле не может быть пустым!'


class CompanyBase(BaseModel):
    name: str = Field(..., max_length=COMPANY_NAME_MAX_LENGTH)


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, max_length=COMPANY_NAME_MAX_LENGTH)

    @field_validator('name')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value


class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=DEPARTMENT_NAME_MAX_LENGTH)


class DepartmentCreate(DepartmentBase):
    company_name: str = Field(..., max_length=COMPANY_NAME_MAX_LENGTH)
    parent_department_name: str | None = Field(None, max_length=DEPARTMENT_NAME_MAX_LENGTH)


class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    company_name: str
    parent_department: str | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=DEPARTMENT_NAME_MAX_LENGTH)

    @field_validator('name')
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(FIELD_CANT_BE_EMPTY)
        return value
