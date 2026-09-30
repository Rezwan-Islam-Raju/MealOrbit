from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.dependencies.auth_dependecy import require_user_id

from app.schemas.notification_schema import NotificationResponse, NotificationCreateRequest, \
    NotificationMessageResponse, NotificationUnreadCountResponse
from app.services.notification_service import \
    delete_notification_service, mark_notifications_as_read_service, \
    mark_all_notification_as_read_service, get_unread_count_notification_service, create_order_notification_service, \
    get_my_notification_service, get_unread_notification_service
from config.database import get_db

router = APIRouter()




# CREATE NOTIFICATION
@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    request: NotificationCreateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    notification = await create_order_notification_service(
        db=db,
        user_id=user_id,
        request=request,
    )

    return notification

# GET MY NOTIFICATIONS

@router.get("/my",response_model=list[NotificationResponse])
async def get_my_notifications(
        user_id:int = Depends(require_user_id),
        db:AsyncSession = Depends(get_db)
):
    result = await get_my_notification_service(
        db=db,
        user_id=user_id

    )
    return result

# GET UNREAD NOTIFICATIONS

@router.get("/unread",
       response_model = list[NotificationResponse],
)
async def get_unread_notifications(
        user_id:int = Depends(require_user_id),
        db:AsyncSession = Depends(get_db)
):
    result = await get_unread_notification_service(
        db=db,
        user_id=user_id
    )
    return result

# GET UNREAD COUNT

@router.get(
    "/unread/count",
    response_model = NotificationUnreadCountResponse
)
async def get_unread_count_notifications(
        user_id:int = Depends(require_user_id),
        db:AsyncSession = Depends(get_db)
):
    result = await get_unread_count_notification_service(
        db=db,
        user_id=user_id

    )
    return result

# MARK AS READ

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id),
):
    result= await mark_notifications_as_read_service(
        db=db,
        user_id=user_id,
        notification_id=notification_id,
    )
    return result



# MARK ALL AS READ

@router.patch(
    "/read-all",
    response_model=NotificationMessageResponse,
)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id),
):
    result= await mark_all_notification_as_read_service(
        db=db,
        user_id=user_id,
    )
    return result



# DELETE NOTIFICATION

@router.delete(
    "/{notification_id}",
    response_model=NotificationMessageResponse,
)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id),
):
    result= await delete_notification_service(
        db=db,
        user_id=user_id,
        notification_id=notification_id,
    )
    return result