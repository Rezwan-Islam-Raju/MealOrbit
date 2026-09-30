from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import User, Restaurant, Order
from app.models.notification_model import Notification, NotificationTypeEnum
from app.models.user_model import UserRoleEnum
from app.core.celery_app import send_notification_email
from app.schemas.notification_schema import NotificationCreateRequest




async def create_order_notification_service(
    db: AsyncSession,
    user_id: int,
    request: NotificationCreateRequest,
):
    # 1. Current logged-in user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2. Get order
    result = await db.execute(
        select(Order).where(
            Order.id == request.order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # 3. Permission check
    if current_user.role == UserRoleEnum.ADMIN:
        pass

    elif current_user.role == UserRoleEnum.RESTAURANT_OWNER:

        restaurant_result = await db.execute(
            select(Restaurant).where(
                Restaurant.id == order.restaurant_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True),
            )
        )

        restaurant = restaurant_result.scalar_one_or_none()

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized for this order",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and restaurant owner can create notifications",
        )

    # 4. Get customer from order
    customer_result = await db.execute(
        select(User).where(
            User.id == order.user_id
        )
    )

    customer = customer_result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # 5. Create notification
    notification = Notification(
        user_id=customer.id,
        title=request.title,
        message=request.message,
        notification_type=request.notification_type,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    # 6. Send email
    send_notification_email.delay(
        customer.email,
        request.title,
        request.message,
    )

    return notification


# GET NOTIFICATION
async def get_my_notification_service(
        db: AsyncSession,
        user_id: int
):
    result = await db.execute(select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc()))


    notification = result.scalars().all()
    return notification


# GET MY UNREAD NOTIFICATIONS

async def get_unread_notification_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .order_by(
            Notification.created_at.desc()
        )
    )

    result= result.scalars().all()
    return result

# GET UNREAD COUNT

async def get_unread_count_notification_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(
            func.count(Notification.id)
        )
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    )

    count = result.scalar() or 0

    return {
        "unread_count": count
    }


# MARK NOTIFICATION AS READ


async def mark_notifications_as_read_service(
        db: AsyncSession,
        user_id: int,
        notification_id: int
):
    result = await db.execute(
        select(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )

    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True

    await db.commit()
    await db.refresh(notification)
    return notification


# MARK ALL NOTIFICATIONS AS READ


async def mark_all_notification_as_read_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    )

    notifications = result.scalars().all()

    for notification in notifications:
        notification.is_read = True

    await db.commit()

    return {
        "message": "All notifications marked as read"
    }


# DELETE NOTIFICATION

async def delete_notification_service(
        db: AsyncSession,
        user_id: int,
        notification_id: int
):
    result = await db.execute(
        select(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )

    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.delete(notification)
    await db.commit()

    return {
        "message": "Notification deleted successfully"
    }