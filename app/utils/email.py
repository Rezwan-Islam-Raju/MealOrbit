import smtplib
from email.message import EmailMessage

from config.config import settings


def send_email(
    to_email: str,
    subject: str,
    body: str
):

    message = EmailMessage()

    message["From"] = settings.SMTP_FROM
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=30
    ) as server:

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(
            settings.SMTP_USER,
            settings.SMTP_PASSWORD
        )

        server.send_message(message)