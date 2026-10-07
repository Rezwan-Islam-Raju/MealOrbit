from app.core.celery_app import celery_app
from app.utils.email_service import send_email


@celery_app.task
def send_password_reset_success_email(
    to_email: str,
    user_name: str
):
    subject = "Password Reset Successful"

    body = f"""
Hello {user_name},

Your password has been reset successfully.

If you did not make this change, please contact support immediately.

Regards,
Food Delivery Team

"""

    send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )

    return {
        "message": "Password reset success email sent",
        "to": to_email,
    }