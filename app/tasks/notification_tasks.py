import asyncio

from app.core.celery_app import celery_app
from config.database import async_session
from app.models.notification_model import Notification, NotificationTypeEnum


async def _create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
):
    async with async_session() as db:

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationTypeEnum(notification_type),
            is_read=False,
        )

        db.add(notification)

        await db.commit()
        await db.refresh(notification)

        return notification.id


@celery_app.task
def create_notification_task(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
):
    notification_id = asyncio.run(
        _create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
        )
    )

    return {
        "message": "Notification created successfully",
        "notification_id": notification_id,
        "user_id": user_id,
    }