from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.celery_app import send_order_confirmation_email, send_order_status_notification
from app.core.pubsub import publish_message
from app.models import Restaurant, Payment
from app.models.user_model import User, UserRoleEnum
from app.models.order_model import Order, OrderItem, OrderStatus
from app.models.cart_model import Cart, CartItem
from app.models.food_model import Food
from app.models.coupon_model import Coupon
from app.services.coupon_service import calculate_discount


DELIVERY_FEE = Decimal("60.00")
TAX_RATE = Decimal("0.05")



async def create_order_from_cart_service(
    db: AsyncSession,
    user_id: int
):
    cart_result = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )

    cart = cart_result.scalar_one_or_none()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    result = await db.execute(
        select(CartItem, Food)
        .join(Food, CartItem.food_id == Food.id)
        .where(CartItem.cart_id == cart.id)
    )

    rows = result.all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # Check food availability
    for cart_item, food in rows:

        if not food.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{food.name} is currently unavailable"
            )

    # Check same restaurant
    restaurant_ids = {
        food.restaurant_id
        for cart_item, food in rows
    }

    if len(restaurant_ids) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart items must belong to the same restaurant"
        )

    restaurant_id = restaurant_ids.pop()

    # Calculate subtotal
    subtotal = Decimal("0.00")

    for cart_item, food in rows:

        item_subtotal = (
            Decimal(str(food.price))
            * cart_item.quantity
        )

        subtotal += item_subtotal

    # Coupon
    discount = Decimal("0.00")
    coupon_id = None

    if cart.coupon_id:

        coupon_result = await db.execute(
            select(Coupon).where(
                Coupon.id == cart.coupon_id
            )
        )

        coupon = coupon_result.scalar_one_or_none()

        if coupon and coupon.is_active:

            discount = Decimal(
                str(
                    calculate_discount(
                        coupon,
                        float(subtotal)
                    )
                )
            )

            coupon_id = coupon.id

    # Tax
    tax = subtotal * TAX_RATE

    # Delivery fee
    delivery_fee = DELIVERY_FEE

    # Total
    total_amount = (
        subtotal
        + delivery_fee
        + tax
        - discount
    )

    # Create order
    order = Order(
        user_id=user_id,
        restaurant_id=restaurant_id,
        coupon_id=coupon_id,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax=tax,
        discount=discount,
        total_amount=total_amount,
        status=OrderStatus.PENDING
    )

    db.add(order)

    await db.flush()

    # Create order items
    for cart_item, food in rows:

        price = Decimal(str(food.price))

        item_subtotal = price * cart_item.quantity

        order_item = OrderItem(
            order_id=order.id,
            food_id=food.id,
            quantity=cart_item.quantity,
            price=price,
            subtotal=item_subtotal
        )

        db.add(order_item)

    # Prepare data for Celery
    # order_items_data = [
    #     {
    #         "food_name": food.name,
    #         "quantity": cart_item.quantity,
    #     }
    #     for cart_item, food in rows
    # ]

    # Remove cart items
    for cart_item, food in rows:
        await db.delete(cart_item)

    # Remove coupon from cart
    cart.coupon_id = None

    # Commit order
    await db.commit()

    # Redis Pub/Sub notification
#    await publish_message(
#        "notification_events",
#       {
#           "user_id": order.user_id,
#           "title": "Order Placed",
#            "message": (
#                f"Your order #{order.id} "
#               f"has been placed successfully."
#            ),
#            "notification_type": "ORDER"
#        }
#    )

    # Get customer email
#   customer_result = await db.execute(
#      select(User).where(
#           User.id == order.user_id
#      )
#    )

#    customer = customer_result.scalar_one_or_none()

#    if customer:

#        send_order_confirmation_email.delay(
#           customer_email=customer.email,
#            order_id=order.id,
#           order_items=order_items_data
#       )

    # Reload order with items
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
        )
        .where(Order.id == order.id)
    )

    order = result.scalar_one()

    return order



async def get_my_orders_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )

    orders = result.scalars().unique().all()

    return orders


async def get_my_order_by_id_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
):
    result = await db.execute(select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .options(selectinload(Order.items))
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Order not found" )
    return order


async def cancel_order_service(
    db: AsyncSession,
    user_id: int,
    order_id: int
):
    result = await db.execute(select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .options(
            selectinload(Order.items)
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

    if order.status not in {
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled at this stage"
        )

    order.status = OrderStatus.CANCELLED

    await db.commit()

#    await publish_message(
#        "notification_events",
#        {
#            "user_id": order.user_id,
#            "title": "Order Cancelled",
#            "message": (
#               f"Your order #{order.id} "
#               f"has been cancelled successfully."
#            ),
#            "notification_type": "ORDER"
#        }
#   )
    # Reload order with items
    result = await db.execute(select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .options(
            selectinload(Order.items)
        )
    )

    order = result.scalar_one()

    return order


async def get_restaurant_orders_service(
    db: AsyncSession,
    user_id: int
):
    #  Get current user
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    #  Admin → can see orders from all restaurants
    if user.role == UserRoleEnum.ADMIN:
        result = await db.execute(
            select(Order)
            .join(
                Restaurant,
                Order.restaurant_id == Restaurant.id
            )
            .where(
                Restaurant.is_active.is_(True)
            )
            .options(
                selectinload(Order.items)
            )
            .order_by(
                Order.created_at.desc()
            )
        )

    #    Restaurant owner → can see all orders
    #    from their own restaurant only
    elif user.role == UserRoleEnum.RESTAURANT_OWNER:
        result = await db.execute(
            select(Order)
            .join(
                Restaurant,
                Order.restaurant_id == Restaurant.id
            )
            .where(
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
            .options(
                selectinload(Order.items)
            )
            .order_by(
                Order.created_at.desc()
            )
        )

    #  Other roles → forbidden
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view restaurant orders",
        )

    orders = result.scalars().unique().all()

    return orders



async def get_restaurant_order_by_id_service(
    db: AsyncSession,
    user_id: int,
    order_id: int
):
    #  Get current user
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    #  Admin can view any restaurant order
    if user.role == UserRoleEnum.ADMIN:

        result = await db.execute(
            select(Order)
            .join(
                Restaurant,
                Order.restaurant_id == Restaurant.id
            )
            .where(
                Order.id == order_id,
                Restaurant.is_active.is_(True)
            )
            .options(
                selectinload(Order.items)
            )
        )

    #  Restaurant owner can view only their own restaurant order
    elif user.role == UserRoleEnum.RESTAURANT_OWNER:

        result = await db.execute(
            select(Order)
            .join(
                Restaurant,
                Order.restaurant_id == Restaurant.id,
            )
            .where(
                Order.id == order_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True),
            )
            .options(
                selectinload(Order.items)
            )
        )

    #  Other roles are not allowed
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view restaurant orders"
        )

    #  Order not found / not owned by restaurant owner
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order



async def update_restaurant_order_status_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
    new_status: OrderStatus
):


    # Get current user

    user_result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True)
        )
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


    # Authorization
    # Only Admin and Restaurant Owner
    # can update order status

    if user.role not in {
        UserRoleEnum.ADMIN,
        UserRoleEnum.RESTAURANT_OWNER
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized "
                "to update order status"
            ),
        )


    # Get order

    # Admin can update any order
    if user.role == UserRoleEnum.ADMIN:

        result = await db.execute(
            select(Order)
            .where(
                Order.id == order_id
            )
            .options(
                selectinload(Order.user),
                selectinload(Order.restaurant),
                selectinload(Order.items)
            )
        )

    # Restaurant owner can update
    # only their own restaurant's order
    else:

        result = await db.execute(
            select(Order)
            .join(
                Restaurant,
                Order.restaurant_id == Restaurant.id
            )
            .where(
                Order.id == order_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
            .options(
                selectinload(Order.user),
                selectinload(Order.restaurant),
                selectinload(Order.items)
            )
        )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Allowed status transitions
    allowed_transitions = {

        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED
        },

        OrderStatus.CONFIRMED: {
            OrderStatus.PREPARING
        },

        OrderStatus.PREPARING: {
            OrderStatus.READY
        },
    }

    # Check status transition

    allowed_statuses = allowed_transitions.get(
        order.status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot change order status "
                f"from {order.status.value} "
                f"to {new_status.value}"
            ),
        )

    # Payment check
    # Payment must be paid before
    # restaurant starts preparing the order

    if new_status == OrderStatus.PREPARING:

        payment_result = await db.execute(
            select(Payment).where(
                Payment.order_id == order.id,
                Payment.status == "paid"
            )
        )

        payment = payment_result.scalar_one_or_none()

        if not payment:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Payment must be successful "
                    "before preparing the order"
                ),
            )


    # Update order status

    order.status = new_status

    await db.commit()


    # Send notification through Celery


#   send_order_status_notification.delay(
#       user_id=order.user_id,
#       order_id=order.id,
#       new_status=new_status.value
#  )

    # Reload order with relationships

    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id
        )
        .options(
            selectinload(Order.user),
            selectinload(Order.restaurant),
            selectinload(Order.items)
        )
    )

    order = result.scalar_one()

    return order

