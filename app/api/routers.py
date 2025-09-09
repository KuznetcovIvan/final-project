from fastapi import APIRouter

from app.api.endpoints.company import router as company_router
from app.api.endpoints.task import router as task_router
from app.api.endpoints.user import router as user_router

router_v1 = APIRouter(prefix='/v1')
router_v1.include_router(user_router)
router_v1.include_router(company_router)
router_v1.include_router(task_router)


main_router = APIRouter(prefix='/api')
main_router.include_router(router_v1)
