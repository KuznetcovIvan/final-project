import contextlib
from asyncio import to_thread
from logging.config import dictConfig

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr
from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from uvicorn.config import LOGGING_CONFIG

from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.core.db import engine, get_async_session
from app.core.user import get_user_db, get_user_manager
from app.schemas.user import UserCreate

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(email: EmailStr, password: str, is_superuser: bool = False):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(UserCreate(email=email, password=password, is_superuser=is_superuser))
    except UserAlreadyExists:
        pass


async def create_first_superuser():
    if settings.first_superuser_email is not None and settings.first_superuser_password is not None:
        await create_user(
            email=settings.first_superuser_email, password=settings.first_superuser_password, is_superuser=True
        )


def migrate_exists(connection: Connection):
    return inspect(connection).has_table('alembic_version')


async def run_first_migration():
    if not settings.run_first_migration:
        return
    async with engine.begin() as connection:
        if not await connection.run_sync(migrate_exists):
            await to_thread(command.upgrade, Config('alembic.ini'), 'head')
            dictConfig(LOGGING_CONFIG)


async def init_db():
    await run_first_migration()
    await create_first_superuser()
