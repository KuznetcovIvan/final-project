from enum import StrEnum

from fastapi import APIRouter

from app.core.constants import AUTH_PREFIX
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


class UserTags(StrEnum):
    AUTH = 'Аутентификация'
    USERS = 'Пользователи'


router.include_router(fastapi_users.get_auth_router(auth_backend), prefix=AUTH_PREFIX, tags=[UserTags.AUTH])
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix='/auth', tags=[UserTags.AUTH])
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix='/users', tags=[UserTags.USERS])
