import json

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pubsub import publish_message
from app.core.redis import redis_client
from app.models.delivery_model import Delivery
from app.models.rider_model import Rider


async def update_rider_location_service(
    db: AsyncSession,
    user_id: int,
    delivery_id: int,
    latitude: float,
    longitude: float
):
    # Find logged-in rider
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider not found"
        )

    # Check delivery belongs to this rider
    result = await db.execute(
        select(Delivery).where(
            Delivery.id == delivery_id,
            Delivery.rider_id == rider.id
        )
    )

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found for this rider"
        )

    # Location update not allowed after delivery
    if delivery.status.value in (
        "DELIVERED",
        "CANCELLED",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location update is not allowed for this delivery"
        )

    location = {
        "rider_id": rider.id,
        "delivery_id": delivery.id,
        "latitude": latitude,
        "longitude": longitude
    }

    # Save latest location
    key = f"rider:location:{rider.id}"

    await redis_client.set(
        key,
        json.dumps(location),
        ex=300
    )

    # Send live location through Redis Pub/Sub
    await publish_message(
        f"delivery_location:{delivery.id}",
        location
    )

    return location