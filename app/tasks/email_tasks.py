from app.core.celery_app import celery_app
from app.utils.email import send_email


@celery_app.task
def send_email_task(
    to_email: str,
    subject: str,
    body: str,
):
    send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )

    return {
        "message": "Email sent successfully",
        "to": to_email,
    }