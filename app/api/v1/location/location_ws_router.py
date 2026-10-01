from fastapi import  WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect

from app.core.pubsub import get_pubsub

router = APIRouter()



#---------- RIDER LOCATION WEBSOCKET API -----------

@router.websocket("/{delivery_id}")
async def rider_location_websocket(
    websocket: WebSocket,
    delivery_id: int,
):
    await websocket.accept()

    channel = f"delivery_location:{delivery_id}"

    pubsub = await get_pubsub()
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            await websocket.send_text(
                message["data"]
            )

    except WebSocketDisconnect:
        pass

    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()