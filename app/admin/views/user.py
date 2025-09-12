from fastapi_users.password import PasswordHelper

from app.admin.views.base import BaseModelView
from app.models.user import User
from app.schemas.user import UserCreate


class UserView(BaseModelView):
    def __init__(self):
        super().__init__(
            User,
            UserCreate,
            icon='fa fa-users',
            name='пользователя',
            label='Пользователи',
        )

    fields = ['id', 'email', 'hashed_password', 'is_superuser']

    sortable_fields = ['id', 'email']
    searchable_fields = ['email']
    fields_default_sort = searchable_fields

    async def validate(self, request, data):
        data['hashed_password'] = PasswordHelper().hash(data.get('hashed_password'))
        return data
