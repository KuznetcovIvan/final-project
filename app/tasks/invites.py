from app.core.db import AsyncSessionLocal
from app.crud.company import invites_crud


async def cleanup_expired_invites_task() -> None:
    async with AsyncSessionLocal() as session:
        await invites_crud.cleanup_expired_invites(session)
