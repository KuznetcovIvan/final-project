from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_can_evaluate_task, check_user_in_company
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.motivation import rating_crud
from app.models.user import User
from app.schemas.motivation import RatingCreate, RatingRead, RatingsSummary

EVALUATE_EXISTS = 'Задача с id={} уже оценена!'


router = APIRouter(tags=['Мотивация'])


@router.post('/{company_id}/tasks/{task_id}/evaluate', response_model=RatingRead)
async def evaluate_task(
    company_id: int,
    task_id: int,
    obj_in: RatingCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    task = await check_can_evaluate_task(user, company_id, task_id, session)
    try:
        rating = await rating_crud.create_for_task(task, obj_in, session)
        return rating
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=EVALUATE_EXISTS.format(task_id))


@router.get('/{company_id}/ratings', response_model=RatingsSummary)
async def get_user_and_department_ratings(
    company_id: int,
    year: int = Query(ge=1000, le=9999),
    quarter: int = Query(ge=1, le=4),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    membership = await check_user_in_company(user.id, company_id, session)
    ratings, user_avg, department_avg = await rating_crud.summary(membership, session, year, quarter)
    return RatingsSummary(items=ratings, user_avg=user_avg, department_avg=department_avg)
