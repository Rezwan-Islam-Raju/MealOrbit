from fastapi import Request, Depends

from fastapi import APIRouter

from app.core.rate_limit import rate_limit
from app.core.redis import redis_client

router = APIRouter()





@router.get("/test")
async def redis_test():

    await redis_client.set(
        "test_key",
        "Hello Redis",
    )

    value = await redis_client.get("test_key")

    return {
        "message": value
    }

@router.delete("/test")
async def redis_delete_test():
    await redis_client.delete("test_key")

    return {
        "message": "Redis key deleted"
    }



@router.get("/ttl-test")
async def redis_ttl_test():

    await redis_client.set(
        "temporary_key",
        "This data will expire",
        ex=60
    )

    ttl = await redis_client.ttl("temporary_key")

    return {
        "message": "Temporary data stored",
        "ttl": ttl
    }



@router.get("/keys")
async def redis_keys():

    keys = await redis_client.keys("*")

    return {
        "keys": [
            key.decode() if isinstance(key, bytes) else key
            for key in keys
        ]
    }


@router.get(
    "/rate-limit-test",
    dependencies=[Depends(rate_limit)]
)
async def rate_limit_test():
    return {
        "message": "Request successful"
    }