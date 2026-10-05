from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from config.database  import async_session
from app.core.pubsub import get_pubsub
from app.core.redis import redis_client
from app.models.delivery_model import Delivery


router = APIRouter()


@router.websocket("/{delivery_id}")
async def rider_location_websocket(
    websocket: WebSocket,
    delivery_id: int,
):
    await websocket.accept()

    pubsub = None

    try:

        print("STEP 1: WebSocket accepted")
        print("STEP 2: Delivery ID =", delivery_id)

        # Find delivery

        async with async_session() as db:

            result = await db.execute(
                select(Delivery).where(
                    Delivery.id == delivery_id
                )
            )

            delivery = result.scalar_one_or_none()

        print("STEP 3: Delivery =", delivery)

        if not delivery:

            await websocket.send_json({
                "error": "Delivery not found",
                "delivery_id": delivery_id
            })

            await websocket.close()

            return

        # Get rider ID

        rider_id = delivery.rider_id

        print("STEP 4: Rider ID =", rider_id)

        if not rider_id:

            await websocket.send_json({
                "error": "No rider assigned to this delivery",
                "delivery_id": delivery_id
            })

            await websocket.close()

            return

        # Get latest location

        key = f"rider:location:{rider_id}"

        print("STEP 5: Redis key =", key)

        latest_location = await redis_client.get(key)

        print(
            "STEP 6: Latest location =",
            latest_location
        )

        if latest_location:

            if isinstance(
                latest_location,
                bytes
            ):
                latest_location = latest_location.decode(
                    "utf-8"
                )

            await websocket.send_text(
                latest_location
            )

        else:

            await websocket.send_json({
                "message": "No location available yet",
                "delivery_id": delivery_id,
                "rider_id": rider_id
            })

        # Redis Pub/Sub channel

        channel = f"delivery_location:{delivery_id}"

        print(
            "STEP 7: Channel =",
            channel
        )

        pubsub = await get_pubsub()

        await pubsub.subscribe(channel)

        print(
            "STEP 8: Subscribed successfully"
        )

        # Listen for live location


        async for message in pubsub.listen():

            print(
                "Redis message =",
                message
            )

            if message["type"] != "message":
                continue

            data = message["data"]

            if isinstance(data, bytes):

                data = data.decode(
                    "utf-8"
                )

            await websocket.send_text(
                data
            )

    except WebSocketDisconnect:

        print(
            "WebSocket disconnected:",
            delivery_id
        )

    except Exception as e:

        print(
            "WEBSOCKET ERROR:",
            type(e).__name__,
            str(e)
        )

    finally:

        if pubsub:

            try:

                channel = f"delivery_location:{delivery_id}"

                await pubsub.unsubscribe(
                    channel
                )

                await pubsub.close()

                print(
                    "PubSub closed:",
                    channel
                )

            except Exception as e:

                print(
                    "PubSub close error:",
                    e
                )