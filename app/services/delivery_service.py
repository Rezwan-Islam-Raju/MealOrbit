from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.celery_app import send_order_status_notification
from app.models import User
from app.models.delivery_model import Delivery, DeliveryStatusEnum
from app.models.order_model import Order, OrderStatus
from app.models.rider_model import Rider
from app.models.restaurants_model import Restaurant
from app.models.user_model import UserRoleEnum


# ASSIGN RIDER


async def assign_rider_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
    rider_id: int
):

    #  Get current user

    user_result = await db.execute(select(User).where( User.id == user_id,
            User.is_active.is_(True),
        )
    )

    current_user = user_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    #  Check permission

    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.RESTAURANT_OWNER
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only admin and restaurant owner "
                "can assign rider"
            ),
        )

    #  Get order
    result = await db.execute(select(Order)
        .join(
            Restaurant,
            Order.restaurant_id == Restaurant.id,
        )
        .where(
            Order.id == order_id,
            Restaurant.is_active.is_(True),
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    #  Restaurant owner ownership check

    if current_user.role == UserRoleEnum.RESTAURANT_OWNER:

        if order.restaurant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has no restaurant"
            )

        restaurant_result = await db.execute(
            select(Restaurant).where(
                Restaurant.id == order.restaurant_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
        )

        restaurant = restaurant_result.scalar_one_or_none()

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized to "
                    "assign rider for this restaurant"
                ),
            )

    #  Order must be READY

    if order.status != OrderStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Rider can only be assigned "
                "when order status is READY"
            ),
        )

    #  Check existing delivery

    delivery_result = await db.execute(select(Delivery).where(
            Delivery.order_id == order_id,
        )
    )

    existing_delivery = delivery_result.scalar_one_or_none()

    if existing_delivery:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery already exists for this order"
        )

    #  Find available rider

    rider_result = await db.execute(select(Rider).where(
            Rider.id == rider_id,
            Rider.is_active.is_(True),
            Rider.is_online.is_(True),
            Rider.is_available.is_(True)
        )
    )

    rider = rider_result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Available rider not found"
        )

    #  Create delivery

    delivery = Delivery(
        order_id=order.id,
        rider_id=rider.id,
        status=DeliveryStatusEnum.ASSIGNED,
    )

    db.add(delivery)

    #  Rider is no longer available

    rider.is_available = False

    #  Update order status

    order.status = OrderStatus.RIDER_ASSIGNED

    await db.commit()

    #  Refresh delivery

    await db.refresh(delivery)

    #  Send customer notification through Celery

#   send_order_status_notification.delay(
#      user_id=order.user_id,
#       order_id=order.id,
#        new_status=OrderStatus.RIDER_ASSIGNED.value
#    )

    return delivery


# GET MY DELIVERIES

async def get_my_delivery_service(
    db: AsyncSession,
    user_id: int,
):
    #  Get current user
    user_result = await db.execute(select(User).where(User.id == user_id ))

    current_user = user_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    #  Only Admin and Restaurant Owner
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.RESTAURANT_OWNER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only admin and restaurant owner "
                "can view deliveries"
            ),
        )

    #  Get deliveries
    result = await db.execute(select(Delivery)
        .join(
            Order,
            Delivery.order_id == Order.id
        )
        .join(
            Restaurant,
            Order.restaurant_id == Restaurant.id
        )
        .where(
            Restaurant.is_active.is_(True)
        )
        .order_by(
            Delivery.created_at.desc()
        )
    )

    deliveries = result.scalars().all()

    return deliveries

# GET DELIVERY BY ORDER

async def get_delivery_by_order_service(
    db: AsyncSession,
    user_id: int,
    order_id: int
):
    #  Current user
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )

    current_user = user_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    #  Permission check
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.RESTAURANT_OWNER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and restaurant owner can view delivery"
        )

    #  Get delivery
    query = (
        select(Delivery)
        .join(
            Order,
            Delivery.order_id == Order.id
        )
        .join(
            Restaurant,
            Order.restaurant_id == Restaurant.id
        )
        .where(
            Delivery.order_id == order_id,
            Restaurant.is_active.is_(True)
        )
    )

    #  Restaurant owner → own restaurant only
    if current_user.role == UserRoleEnum.RESTAURANT_OWNER:
        query = query.where(
            Restaurant.owner_id == user_id
        )

    result = await db.execute(query)

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found or you do not have permission"
        )

    return delivery


# ACCEPT DELIVERY

async def accept_delivery_service(
    db: AsyncSession,
    user_id: int,
    delivery_id: int
):

    result = await db.execute(
        select(Delivery)
        .join(
            Rider,
            Delivery.rider_id == Rider.id
        )
        .where(
            Delivery.id == delivery_id,
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )

    # Status check
    if delivery.status != DeliveryStatusEnum.ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only ASSIGNED delivery "
                "can be accepted"
            ),
        )

    # Accept delivery
    delivery.status = DeliveryStatusEnum.ACCEPTED
    delivery.accepted_at = datetime.now(timezone.utc)

    await db.commit()

    await db.refresh(delivery)

    return delivery


# PICK UP ORDER

async def pickup_delivery_service(
    db: AsyncSession,
    user_id: int,
    delivery_id: int,
):

    result = await db.execute(
        select(Delivery)
        .join(
            Rider,
            Delivery.rider_id == Rider.id
        )
        .where(
            Delivery.id == delivery_id,
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )

    # Status check
    if delivery.status != DeliveryStatusEnum.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only ACCEPTED delivery "
                "can be picked up"
            ),
        )

    # Update delivery
    delivery.status = DeliveryStatusEnum.PICKED_UP
    delivery.picked_up_at = datetime.now(timezone.utc)

    # Find order
    result = await db.execute(
        select(Order).where(
            Order.id == delivery.order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Update order status
    order.status = OrderStatus.PICKED_UP

    await db.commit()

    await db.refresh(delivery)

    return delivery

# OUT FOR DELIVERY

async def out_for_delivery_service(
    db: AsyncSession,
    user_id: int,
    delivery_id: int
):

    result = await db.execute(
        select(Delivery)
        .join(
            Rider,
            Delivery.rider_id == Rider.id
        )
        .where(
            Delivery.id == delivery_id,
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )

    # Status check
    if delivery.status != DeliveryStatusEnum.PICKED_UP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only PICKED_UP delivery "
                "can go out for delivery"
            ),
        )

    # Update delivery
    delivery.status = DeliveryStatusEnum.OUT_FOR_DELIVERY

    # Find order
    result = await db.execute(
        select(Order).where(
            Order.id == delivery.order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Update order status
    order.status = OrderStatus.OUT_FOR_DELIVERY

    await db.commit()

    await db.refresh(delivery)

    return delivery



# COMPLETE DELIVERY

async def complete_delivery_service(
    db: AsyncSession,
    user_id: int,
    delivery_id: int,
):

    result = await db.execute(
        select(Delivery)
        .join(
            Rider,
            Delivery.rider_id == Rider.id
        )
        .where(
            Delivery.id == delivery_id,
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )

    # Status check
    if delivery.status != DeliveryStatusEnum.OUT_FOR_DELIVERY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only OUT_FOR_DELIVERY delivery "
                "can be completed"
            ),
        )

    # Update delivery
    delivery.status = DeliveryStatusEnum.DELIVERED
    delivery.delivered_at = datetime.now(timezone.utc)

    # Find order
    result = await db.execute(
        select(Order).where(
            Order.id == delivery.order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Update order status
    order.status = OrderStatus.DELIVERED

    # Rider becomes available again
    rider = await db.get(
        Rider,
        delivery.rider_id
    )

    if rider:
        rider.is_available = True

    await db.commit()

    await db.refresh(delivery)

    return delivery


# CANCEL DELIVERY

async def cancel_delivery_service(
    db: AsyncSession,
    user_id: int,
    delivery_id: int
):

    result = await db.execute(
        select(Delivery)
        .join(
            Rider,
            Delivery.rider_id == Rider.id
        )
        .where(
            Delivery.id == delivery_id,
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    delivery = result.scalar_one_or_none()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )

    # Cannot cancel completed/cancelled delivery
    if delivery.status in (
        DeliveryStatusEnum.DELIVERED,
        DeliveryStatusEnum.CANCELLED,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery cannot be cancelled"
        )

    # Update delivery
    delivery.status = DeliveryStatusEnum.CANCELLED

    # Update order status
    order = await db.get(
        Order,
        delivery.order_id
    )

    if order:
        order.status = OrderStatus.CANCELLED

    # Make rider available again
    rider = await db.get(
        Rider,
        delivery.rider_id
    )

    if rider:
        rider.is_available = True

    await db.commit()

    await db.refresh(delivery)

    return delivery