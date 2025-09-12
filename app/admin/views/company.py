from app.admin.views.base import BaseModelView
from app.models.company import Company, CompanyNews, Department, Invite, UserCompanyMembership


class CompanyView(BaseModelView):
    def __init__(self):
        super().__init__(
            Company,
            icon='fa fa-building',
            name='компанию',
            label='Компании',
        )

    fields = ['id', 'name', 'departments']
    exclude_fields_from_create = ['departments']
    exclude_fields_from_edit = exclude_fields_from_create
    sortable_fields = fields
    searchable_fields = fields
    fields_default_sort = fields


class DepartmentView(BaseModelView):
    def __init__(self):
        super().__init__(
            Department,
            icon='fa fa-sitemap',
            name='отдел',
            label='Отделы',
        )

    fields = ['id', 'name', 'company', 'parent']
    sortable_fields = fields
    searchable_fields = fields
    fields_default_sort = fields


class MembershipView(BaseModelView):
    def __init__(self):
        super().__init__(
            UserCompanyMembership,
            icon='fa fa-id-badge',
            name='членство',
            label='Членства',
        )

    fields = ['id', 'user', 'company', 'department', 'manager', 'role']
    sortable_fields = fields
    searchable_fields = fields
    fields_default_sort = fields


class InviteView(BaseModelView):
    def __init__(self):
        super().__init__(
            Invite,
            icon='fa fa-envelope-open',
            name='приглашение',
            label='Инвайты',
        )

    fields = ['id', 'email', 'company', 'department', 'manager', 'role', 'expires_at', 'code']
    sortable_fields = ['id', 'email', 'expires_at']
    searchable_fields = ['email']
    fields_default_sort = ['expires_at']


class NewsView(BaseModelView):
    def __init__(self):
        super().__init__(
            CompanyNews,
            icon='fa fa-newspaper',
            name='новость',
            label='Новости',
        )

    fields = ['id', 'title', 'body', 'author', 'company', 'published_at']
    sortable_fields = ['id', 'published_at', 'title']
    searchable_fields = ['title', 'body']
    fields_default_sort = ['published_at']
