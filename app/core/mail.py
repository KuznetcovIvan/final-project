from fastapi_mail import FastMail

from app.core.config import settings

mail = FastMail(settings.mail_config)
