from fastapi import APIRouter

from app.api.endpoints.company import router as company_router

main_router_v1 = APIRouter(prefix='/v1')
main_router_v1.include_router(company_router, tags=['Компании'])
