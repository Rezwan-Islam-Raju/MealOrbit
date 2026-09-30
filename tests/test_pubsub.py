import asyncio

from app.core.pubsub import subscribe_channel


asyncio.run(
    subscribe_channel("test_channel")
)