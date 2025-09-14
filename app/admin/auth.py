from fastapi_users.password import PasswordHelper
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider, FormValidationError, LoginFailed

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.user import User

ADMIN_TITLE = f'{settings.app_title} Admin'
FAIL_MESSAGE = 'Not allowed'

password_helper = PasswordHelper()


class SuperuserAuth(AuthProvider):
    async def login(
        self, username: str, password: str, remember_me: bool, request: Request, response: Response
    ) -> Response:
        if not username or not password:
            raise FormValidationError({'username': 'required', 'password': 'required'})
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == username))
            if not user or not user.hashed_password:
                raise LoginFailed(FAIL_MESSAGE)
            ok, new_hash = password_helper.verify_and_update(password, user.hashed_password)
            if not (ok and user.is_superuser):
                raise LoginFailed(FAIL_MESSAGE)
            if new_hash:
                user.hashed_password = new_hash
                await session.commit()
        request.session.update({'uid': user.id, 'email': user.email, 'is_superuser': True})
        return response

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    async def is_authenticated(self, request: Request) -> bool:
        return bool(request.session.get('is_superuser'))

    def get_admin_user(self, request: Request) -> AdminUser | None:
        if request.session.get('is_superuser'):
            return AdminUser(username=request.session.get('email'))
        return None

    def get_admin_config(self, request: Request) -> AdminConfig:
        return AdminConfig(app_title=ADMIN_TITLE)
