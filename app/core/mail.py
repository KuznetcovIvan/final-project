from fastapi_mail import ConnectionConfig, FastMail

from app.core.config import settings

mail = FastMail(ConnectionConfig(**settings.mail_config))
