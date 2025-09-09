from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.tasks.setup import register_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    register_jobs()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_title, description=settings.description, lifespan=lifespan)

app.include_router(main_router)
