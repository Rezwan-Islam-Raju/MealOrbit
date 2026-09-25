from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart_model import Cart, CartItem
from app.models.food_model import Food
from app.models.coupon_model import Coupon
from app.schemas.cart_schema import CartItemCreateRequest, CartItemUpdateRequest
from app.services.coupon_service import validate_coupon, calculate_discount


async def get_or_create_cart(
        db: AsyncSession,
        user_id: int
):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalar_one_or_none()

    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    return cart


async def build_cart_response_data(
        db: AsyncSession,
        cart: Cart
):
    result = await db.execute(
        select(CartItem, Food)
        .join(Food, CartItem.food_id == Food.id)
        .where(CartItem.cart_id == cart.id)
    )
    rows = result.all()

    items = []
    subtotal = 0.0

    for cart_item, food in rows:
        item_subtotal = food.price * cart_item.quantity
        subtotal += item_subtotal
        items.append({
            "id": cart_item.id,
            "food_id": food.id,
            "food_name": food.name,
            "food_price": food.price,
            "quantity": cart_item.quantity,
            "subtotal": item_subtotal,
        })

    discount_amount = 0.0
    coupon_code = None

    if cart.coupon_id:
        coupon_result = await db.execute(select(Coupon).where(Coupon.id == cart.coupon_id))
        coupon = coupon_result.scalar_one_or_none()
        if coupon:
            discount_amount = calculate_discount(coupon, subtotal)
            coupon_code = coupon.code

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items,
        "total_items": len(items),
        "subtotal": subtotal,
        "coupon_code": coupon_code,
        "discount_amount": discount_amount,
        "grand_total": subtotal - discount_amount,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
    }


async def add_to_cart_service(
        db: AsyncSession,
        user_id: int,
        request: CartItemCreateRequest
):
    food_result = await db.execute(
        select(Food)
        .where(Food.id == request.food_id, Food.is_available.is_(True))
    )
    food = food_result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found or unavailable"
        )

    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )

    item_result = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id, CartItem.food_id == request.food_id)
    )
    existing_item = item_result.scalar_one_or_none()

    if existing_item:
        existing_item.quantity += request.quantity
    else:
        existing_item = CartItem(
            cart_id=cart.id,
            food_id=request.food_id,
            quantity=request.quantity
        )
        db.add(existing_item)

    await db.commit()
    result= await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result


async def get_cart_service(
        db: AsyncSession,
        user_id: int
):
    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )
    result= await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result


async def update_cart_item_service(
        db: AsyncSession,
        user_id: int,
        item_id: int,
        request: CartItemUpdateRequest
):
    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )

    item_result = await db.execute(
        select(CartItem)
        .where(CartItem.id == item_id, CartItem.cart_id == cart.id)
    )
    item = item_result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    item.quantity = request.quantity
    await db.commit()
    result= await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result


async def remove_cart_item_service(
        db: AsyncSession,
        user_id: int,
        item_id: int
):
    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )

    item_result = await db.execute(
        select(CartItem)
        .where(CartItem.id == item_id, CartItem.cart_id == cart.id)
    )
    item = item_result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    await db.delete(item)
    await db.commit()
    result= await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result

async def clear_cart_service(
        db: AsyncSession,
        user_id: int
):
    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )

    item_result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id))
    items = item_result.scalars().all()

    for item in items:
        await db.delete(item)

    await db.commit()
    result= await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result

async def apply_coupon_service(
        db: AsyncSession,
        user_id: int,
        code: str
):
    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )
    cart_data = await build_cart_response_data(
        db=db,
        cart=cart
    )

    if cart_data["total_items"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    coupon = await validate_coupon(
        db=db, code=code,
        subtotal=cart_data["subtotal"]
    )

    cart.coupon_id = coupon.id
    await db.commit()
    await db.refresh(cart)

    result = await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result


async def remove_coupon_service(
        db: AsyncSession,
        user_id: int
):
    cart = await get_or_create_cart(
        db=db,
        user_id=user_id
    )
    cart.coupon_id = None
    await db.commit()
    await db.refresh(cart)

    result = await build_cart_response_data(
        db=db,
        cart=cart
    )
    return result