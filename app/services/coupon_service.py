from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coupon_model import Coupon, DiscountType
from app.models.user_model import User, UserRoleEnum
from app.schemas.coupon_schema import CouponCreateRequest



# ADMIN ONLY - CREATE COUPON


async def create_coupon_service(
    db: AsyncSession,
    request: CouponCreateRequest,
    admin_id: int
):
    # Check user
    result = await db.execute(select(User).where( User.id == admin_id,
            User.is_active.is_(True)
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check admin role
    if user.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create coupons"
        )

    # Clean coupon code
    code = request.code.strip().upper()

    # Check duplicate coupon
    existing = await db.execute(
        select(Coupon).where(
            Coupon.code == code
        )
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )

    # Create coupon
    coupon_data = request.model_dump()

    # Make sure cleaned code is saved
    coupon_data["code"] = code

    coupon = Coupon(**coupon_data)

    db.add(coupon)

    await db.commit()
    await db.refresh(coupon)

    return coupon


# GET ACTIVE COUPONS


async def get_coupons_service(
    db: AsyncSession
):
    result = await db.execute(select(Coupon).where(Coupon.is_active.is_(True)))

    return result.scalars().all()


# CUSTOMER - VALIDATE / USE COUPON


async def validate_coupon(
    db: AsyncSession,
    code: str,
    subtotal: float
):
    code = code.strip().upper()

    result = await db.execute(select(Coupon).where(
            Coupon.code == code,
            Coupon.is_active.is_(True)
        )
    )

    coupon = result.scalar_one_or_none()

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    # Expiry check
    now = datetime.now(timezone.utc)

    if coupon.expiry_date < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon has expired"
        )

    # Usage limit
    if (
        coupon.usage_limit is not None
        and coupon.used_count >= coupon.usage_limit
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon usage limit reached"
        )

    # Minimum order amount
    if subtotal < coupon.min_order_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Minimum order amount is "
                f"{coupon.min_order_amount}"
            )
        )

    return coupon


# CALCULATE DISCOUNT

def calculate_discount(
    coupon: Coupon,
    subtotal: float
):
    if coupon.discount_type == DiscountType.PERCENTAGE:

        discount = subtotal * (
            coupon.discount_value / 100
        )

        if coupon.max_discount is not None:
            discount = min(
                discount,
                coupon.max_discount
            )

    else:
        discount = coupon.discount_value

    # Discount cannot exceed subtotal
    result = min(
        discount,
        subtotal
    )

    return result