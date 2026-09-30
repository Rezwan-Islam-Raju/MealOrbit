import json

from app.core.redis import redis_client
from config.database import async_session
from app.models.notification_model import NotificationTypeEnum
from app.schemas.notification_schema import NotificationCreateRequest
from app.services.notification_service import create_notification_service


async def notification_subscriber():

    pubsub = redis_client.pubsub()

    await pubsub.subscribe("notification_events")

    print("Subscribed to: notification_events")

    async for message in pubsub.listen():

        if message["type"] != "message":
            continue

        try:
            data = json.loads(message["data"])

            print("Notification event received:", data)

            notification_type = NotificationTypeEnum(
                data.get(
                    "notification_type",
                    "SYSTEM"
                )
            )

            request = NotificationCreateRequest(
                user_id=data["user_id"],
                title=data["title"],
                message=data["message"],
                notification_type=notification_type
            )

            async with async_session() as db:

                await create_notification_service(
                    request=request,
                    db=db
                )

            print("Notification saved to database")

        except Exception as e:

            print(
                "Notification subscriber error:",
                e
            )