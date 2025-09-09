from fastapi_mail import MessageSchema

from app.core.config import settings
from app.core.mail import mail

INVITE_LINK_TEMPLATE = f'{settings.app_host}/api/v1/companies/invites/accept?code={{code}}'
SUBJECT = f'Приглашение в {settings.app_title}'
BODY_TEMPLATE = f"""
<h3>Вас пригласили в {settings.app_title}</h3>
<p>Код приглашения: <b>{{code}}</b></p>
<p>Для вступления в компанию перейдите по ссылке:</p>
<a href="{{invite_link}}">Присоединиться</a>
"""


async def send_invite_email(email: str, code: str) -> None:
    await mail.send_message(
        MessageSchema(
            subject=SUBJECT,
            recipients=[email],
            body=BODY_TEMPLATE.format(code=code, invite_link=INVITE_LINK_TEMPLATE.format(code=code)),
            subtype='html',
        )
    )
