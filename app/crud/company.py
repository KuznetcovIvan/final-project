from app.crud.base import CRUDBase
from app.models.company import Company, Department, UserCompanyMembership


class CRUDCompany(CRUDBase):
    pass


class CRUDDepartment(CRUDBase):
    pass


class CRUDMembership(CRUDBase):
    pass


company_crud = CRUDCompany(Company)
department_crud = CRUDDepartment(Department)
membership_crud = CRUDMembership(UserCompanyMembership)
