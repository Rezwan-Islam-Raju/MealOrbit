from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Restaurant
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
        select(Cart)
        .where(Cart.user_id == user_id)
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



    for cart_item, food in rows:

        if not food.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{food.name} is currently unavailable"
            )



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


    subtotal = Decimal("0.00")

    for cart_item, food in rows:

        item_subtotal = (
            Decimal(str(food.price)) *
            cart_item.quantity
        )

        subtotal += item_subtotal



    discount = Decimal("0.00")
    coupon_id = None

    if cart.coupon_id:

        coupon_result = await db.execute(
            select(Coupon)
            .where(Coupon.id == cart.coupon_id)
        )

        coupon = coupon_result.scalar_one_or_none()

        if coupon and coupon.is_active:

            discount = Decimal(
                str(calculate_discount(coupon, float(subtotal)))
            )

            coupon_id = coupon.id



    tax = subtotal * TAX_RATE



    delivery_fee = DELIVERY_FEE



    total_amount = (
        subtotal
        + delivery_fee
        + tax
        - discount
    )



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



    for cart_item, food in rows:

        price = Decimal(str(food.price))

        item_subtotal = price * cart_item.quantity

        order_item = OrderItem(
            order_id=order.id,
            food_id=food.id,
            quantity=cart_item.quantity,

            # Current food price snapshot
            price=price,

            subtotal=item_subtotal
        )

        db.add(order_item)



    for cart_item, food in rows:
        await db.delete(cart_item)

    # Remove applied coupon from cart
    cart.coupon_id = None

    await db.commit()

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items) # selectionload hoilo asyncpg fast data er joono
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
    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .options(selectinload(Order.items))
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


async def cancel_order_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
):
    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .options(
            selectinload(Order.items)
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.status not in {
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled at this stage",
        )

    order.status = OrderStatus.CANCELLED

    await db.commit()

    # Reload order with items eagerly loaded
    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .options(
            selectinload(Order.items)
        )
    )

    order = result.scalar_one()

    return order


async def get_restaurant_orders_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Order)
        .join(
            Restaurant,
            Order.restaurant_id == Restaurant.id
        )
        .where(

            Restaurant.owner_id == user_id,
            Restaurant.is_active.is_(True),
        )
        .options(
            selectinload(Order.items)
        )
        .order_by(
            Order.created_at.desc()
        )
    )

    data= result.scalars().unique().all()

    return data


async def get_restaurant_order_by_id_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
):
    result = await db.execute(
        select(Order)
        .join(
            Restaurant,
            Order.restaurant_id == Restaurant.id
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

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order



async def update_restaurant_order_status_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
    new_status: OrderStatus,
):
    result = await db.execute(
        select(Order)
        .join(
            Restaurant,
            Order.restaurant_id == Restaurant.id
        )
        .where(
            Order.id == order_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active.is_(True),
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Allowed status transitions
    allowed_transitions = {
        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.CONFIRMED: {
            OrderStatus.PREPARING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.PREPARING: {
            OrderStatus.READY,
        },
    }

    allowed_statuses = allowed_transitions.get(
        order.status,
        set()
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

    order.status = new_status

    await db.commit()

    # Reload with items
    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id,
            Order.user_id == order.user_id,
        )
        .options(
            selectinload(Order.items)
        )
    )

    order = result.scalar_one()

    return order