from fastapi import APIRouter

from app.api.endpoints.company import router as company_router
from app.api.endpoints.meeting import router as meeting_router
from app.api.endpoints.motivation import router as motivation_router
from app.api.endpoints.task import router as task_router
from app.api.endpoints.user import router as user_router

company_router.include_router(task_router)
company_router.include_router(motivation_router)
company_router.include_router(meeting_router)

router_v1 = APIRouter(prefix='/v1')
router_v1.include_router(user_router)
router_v1.include_router(company_router)

main_router = APIRouter(prefix='/api')
main_router.include_router(router_v1)
