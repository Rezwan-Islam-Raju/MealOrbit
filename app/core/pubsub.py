import json

from app.core.redis import redis_client


async def publish_message(
    channel: str,
    message: dict
):
    await redis_client.publish(
        channel,
        json.dumps(message)
    )


async def get_pubsub():
    return redis_client.pubsub()



async def subscribe_channel(
    channel: str
):
    pubsub = redis_client.pubsub()

    await pubsub.subscribe(channel)

    print(f"Subscribed to: {channel}")

    async for message in pubsub.listen():

        if message["type"] != "message":
            continue

        data = json.loads(message["data"])

        print(
            "Received message:",
            data
        )