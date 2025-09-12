from starlette_admin.contrib.sqla import ModelView

from app.models.user import User


class UserView(ModelView):
    def __init__(self):
        super().__init__(User)
        self.name = 'Пользователи'
        self.search_fields = ['email']
        self.sortable_fields = ['id', 'email']
