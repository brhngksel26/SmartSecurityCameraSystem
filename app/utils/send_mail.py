from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.config import config


async def send_email(subject: str, recipients: List[str], body: str):

    configuration = ConnectionConfig(
        MAIL_USERNAME=config.MAIL_USERNAME,
        MAIL_PASSWORD=config.MAIL_PASSWORD,
        MAIL_FROM=config.MAIL_FROM,
        MAIL_PORT=config.MAIL_PORT,
        MAIL_SERVER=config.MAIL_SERVER,
        MAIL_TLS=config.MAIL_TLS,
        MAIL_SSL=config.MAIL_SSL,
        USE_CREDENTIALS=config.USE_CREDENTIALS,
        VALIDATE_CERTS=config.VALIDATE_CERTS,
    )
    message = MessageSchema(
        subject=subject, recipients=recipients, body=body, subtype="html"
    )

    mail = FastMail(configuration)
    await mail.send_message(message)
