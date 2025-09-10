from http import HTTPStatus
from random import choices

from fastapi import HTTPException
from fastapi_mail import MessageSchema
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import INVITE_CODE_CHARS, INVITE_CODE_LENGTH, MAX_INVITE_CODE_ATTEMPTS
from app.core.mail import mail
from app.crud.company import invites_crud

INVITE_LINK_TEMPLATE = f'{settings.app_host}/api/v1/companies/invites/accept?code={{code}}'
SUBJECT = f'Приглашение в {settings.app_title}'
BODY_TEMPLATE = f"""
<h3>Вас пригласили в {settings.app_title}</h3>
<p>Код приглашения: <b>{{code}}</b></p>
<p>Для вступления в компанию перейдите по ссылке:</p>
<a href="{{invite_link}}">Присоединиться</a>
"""
CODE_GENERATION_FAILED = 'Не удалось сгенерировать код приглашения!'


async def send_invite_email(email: str, code: str) -> None:
    await mail.send_message(
        MessageSchema(
            subject=SUBJECT,
            recipients=[email],
            body=BODY_TEMPLATE.format(code=code, invite_link=INVITE_LINK_TEMPLATE.format(code=code)),
            subtype='html',
        )
    )


async def generate_invite_code(session: AsyncSession) -> str:
    for _ in range(MAX_INVITE_CODE_ATTEMPTS):
        code = ''.join(choices(INVITE_CODE_CHARS, k=INVITE_CODE_LENGTH))
        if await invites_crud.get_by_attribute('code', code, session) is None:
            return code
    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=CODE_GENERATION_FAILED)
