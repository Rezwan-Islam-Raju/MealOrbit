from fastapi import HTTPException, Request
from starlette import status

from app.core.redis import redis_client


def rate_limit(
    limit: int = 10,
    window: int = 60
):
    async def limiter(request: Request):

        client_ip = request.client.host

        key = f"rate_limit:{request.url.path}:{client_ip}"

        current_count = await redis_client.incr(key)

        if current_count == 1:
            await redis_client.expire(
                key,
                window
            )

        if current_count > limit:
            ttl = await redis_client.ttl(key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Try again in {ttl} seconds."
            )

    return limiter