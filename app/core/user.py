from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import JWT_LIFETIME, MIN_LEN_PASSWORD, TOKEN_URL
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate

PASSWORD_TOO_SHORT = 'Пароль должен содержать не менее {} символов'
PASSWORD_CONTAINS_EMAIL = 'Пароль не должен содержать e-mail'


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=JWT_LIFETIME)


auth_backend = AuthenticationBackend(
    name='jwt', transport=BearerTransport(tokenUrl=TOKEN_URL), get_strategy=get_jwt_strategy
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        if len(password) < MIN_LEN_PASSWORD:
            raise InvalidPasswordException(reason=PASSWORD_TOO_SHORT.format(MIN_LEN_PASSWORD))
        if user.email in password:
            raise InvalidPasswordException(reason=PASSWORD_CONTAINS_EMAIL)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
