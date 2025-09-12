from starlette_admin.contrib.sqla import ModelView

from app.models.company import Company, CompanyNews, Department, Invite, UserCompanyMembership


class CompanyView(ModelView):
    def __init__(self):
        super().__init__(Company)
        self.name = 'Компании'


class DepartmentView(ModelView):
    def __init__(self):
        super().__init__(Department)
        self.name = 'Отделы'


class MembershipView(ModelView):
    def __init__(self):
        super().__init__(UserCompanyMembership)
        self.name = 'Участники компаний'
        self.search_fields = ['user_id', 'company_id']
        self.sortable_fields = ['user_id', 'company_id', 'role']


class InviteView(ModelView):
    def __init__(self):
        super().__init__(Invite)
        self.name = 'Инвайты'


class NewsView(ModelView):
    def __init__(self):
        super().__init__(CompanyNews)
        self.name = 'Новости'
