import json

from app.core.redis import redis_client


async def invalidate_food_cache():

    pagination_keys = await redis_client.keys(
        "foods:pagination:*"
    )

    search_keys = await redis_client.keys(
        "foods:search:*"
    )

    filter_keys = await redis_client.keys(
        "foods:filter:*"
    )

    keys = pagination_keys + search_keys + filter_keys

    if keys:
        await redis_client.delete(*keys)


async def get_cache(key: str):
    data = await redis_client.get(key)

    if data is None:
        return None

    return json.loads(data)


async def set_cache(
    key: str,
    data,
    expire: int = 300
):
    await redis_client.set(
        key,
        json.dumps(data, default=str),
        ex=expire
    )


async def delete_cache(key: str):
    await redis_client.delete(key)