from sqlalchemy import func, select
from starlette_admin.exceptions import FormValidationError

from app.admin.views.base import BaseModelView
from app.models.company import Company, CompanyNews, Department, Invite, UserCompanyMembership
from app.schemas.company import (
    CompanyCreate,
    CompanyMembershipAdminCreate,
    CompanyNewsAdminCreate,
    DepartmentCreate,
    InviteCreate,
)


class CompanyView(BaseModelView):
    def __init__(self):
        super().__init__(
            Company,
            CompanyCreate,
            icon='fa fa-building',
            name='компанию',
            label='Компании',
        )

    fields = ['id', 'name']
    sortable_fields = fields
    searchable_fields = fields
    fields_default_sort = fields

    async def validate(self, request, data):
        errors = {}
        name = data.get('name')
        if not name:
            errors['name'] = 'Укажите название компании'
        else:
            session = request.state.session
            company_id = request.path_params.get('pk')
            query = select(Company.id).where(func.lower(Company.name) == func.lower(name))
            if company_id:
                query = query.where(Company.id != int(company_id))
            if await session.scalar(query):
                errors['name'] = 'Компания с таким названием уже существует'
        if errors:
            raise FormValidationError(errors)
        return data


class DepartmentView(BaseModelView):
    def __init__(self):
        super().__init__(
            Department,
            DepartmentCreate,
            icon='fa fa-sitemap',
            name='отдел',
            label='Отделы',
        )

    fields = ['id', 'name', 'company', 'parent']
    sortable_fields = [
        'id',
        'name',
        'company',
    ]
    searchable_fields = sortable_fields
    fields_default_sort = sortable_fields

    async def validate(self, request, data):
        errors = {}
        name = data.get('name')
        company = data.get('company')
        if not name:
            errors['name'] = 'Укажите название отдела'
        if not company:
            errors['company'] = 'Выберите компанию'
        if not errors:
            session = request.state.session
            departament_id = request.path_params.get('pk')
            query = select(Department.id).where(
                Department.company_id == company.id,
                func.lower(Department.name) == func.lower(name),
            )
            if departament_id:
                query = query.where(Department.id != int(departament_id))
            if await session.scalar(query):
                errors['name'] = 'В этой компании такой отдел уже есть'
        if errors:
            raise FormValidationError(errors)
        return data


class MembershipView(BaseModelView):
    def __init__(self):
        super().__init__(
            UserCompanyMembership,
            CompanyMembershipAdminCreate,
            icon='fa fa-id-badge',
            name='членство',
            label='Членства',
        )

    fields = ['id', 'user', 'company', 'department', 'manager', 'role']
    sortable_fields = ['role']
    searchable_fields = ['user', 'company', 'department', 'manager']
    fields_default_sort = sortable_fields

    async def validate(self, request, data):
        errors = {}
        user = data.get('user')
        company = data.get('company')
        if not user:
            errors['user'] = 'Выберите пользователя'
        if not company:
            errors['company'] = 'Выберите компанию'
        if not errors:
            session = request.state.session
            membership_id = request.path_params.get('pk')
            query = select(UserCompanyMembership.id).where(
                UserCompanyMembership.user_id == user.id,
                UserCompanyMembership.company_id == company.id,
            )
            if membership_id:
                query = query.where(UserCompanyMembership.id != int(membership_id))
            if await session.scalar(query):
                errors['user'] = 'Пользователь уже состоит в этой компании'
        if errors:
            raise FormValidationError(errors)
        return data


class InviteView(BaseModelView):
    def __init__(self):
        super().__init__(
            Invite,
            InviteCreate,
            icon='fa fa-envelope-open',
            name='приглашение',
            label='Инвайты',
        )

    fields = ['id', 'email', 'company', 'department', 'manager', 'role', 'expires_at', 'code']
    sortable_fields = [
        'id',
        'email',
        'expires_at',
        'role',
        'expires_at',
    ]
    searchable_fields = ['email', 'company', 'department', 'manager']
    fields_default_sort = ['expires_at']

    async def validate(self, request, data):
        code = data.get('code')
        session = request.state.session
        if await session.scalar(select(Invite.id).where(Invite.code == code)):
            raise FormValidationError({'code': 'Такой код уже используется'})
        return data


class NewsView(BaseModelView):
    def __init__(self):
        super().__init__(
            CompanyNews,
            CompanyNewsAdminCreate,
            icon='fa fa-newspaper',
            name='новость',
            label='Новости',
        )

    fields = ['id', 'title', 'body', 'author', 'company', 'published_at']
    sortable_fields = ['id', 'published_at', 'title']
    searchable_fields = ['title', 'body']
    fields_default_sort = ['published_at']

    async def validate(self, request, data):
        errors = {}
        for field in ('author', 'company'):
            if not data.get(field):
                errors[field] = f'Поле {field} обязательно!'
        if errors:
            raise FormValidationError(errors)
        return data
