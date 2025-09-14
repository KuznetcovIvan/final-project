from fastapi_users.password import PasswordHelper
from sqlalchemy import select
from starlette_admin.exceptions import FormValidationError

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
        errors = {}
        email = data.get('email')
        if not email:
            errors['email'] = 'Укажите email'
        else:
            session = request.state.session
            user_id = request.path_params.get('pk')
            query = select(User.id).where(User.email == email)
            if user_id:
                query = query.where(User.id != int(user_id))
            if await session.scalar(query):
                errors['email'] = 'Пользователь с таким email уже существует'
        if not errors:
            data['hashed_password'] = PasswordHelper().hash(data.get('hashed_password'))
        if errors:
            raise FormValidationError(errors)
        return data
