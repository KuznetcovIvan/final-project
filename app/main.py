from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin import init_admin
from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser
from app.core.scheduler import register_jobs, start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_first_superuser()
    start_scheduler()
    register_jobs()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_title, description=settings.description, lifespan=lifespan)
app.include_router(main_router)
init_admin(app)
