import asyncio

from app.core.notification_subscriber import notification_subscriber


asyncio.run(
    notification_subscriber()
)