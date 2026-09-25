from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.cart_schema import CartResponse, CartItemCreateRequest, CartItemUpdateRequest
from app.schemas.coupon_schema import ApplyCouponRequest
from app.services.cart_service import (
    add_to_cart_service,
    get_cart_service,
    update_cart_item_service,
    remove_cart_item_service,
    clear_cart_service,
    apply_coupon_service,
    remove_coupon_service,
)
from config.database import get_db

router = APIRouter()


@router.get("/", response_model=CartResponse)
async def get_cart(
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await get_cart_service(
        db=db,
        user_id=user_id
    )
    return result


@router.post("/items", response_model=CartResponse)
async def add_to_cart(
        request: CartItemCreateRequest,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await add_to_cart_service(
        db=db,
        user_id=user_id,
        request=request
    )
    return result


@router.patch("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
        item_id: int,
        request: CartItemUpdateRequest,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await update_cart_item_service(
        db=db,
        user_id=user_id,
        item_id=item_id,
        request=request
    )
    return result


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(
        item_id: int,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await remove_cart_item_service(
        db=db,
        user_id=user_id,
        item_id=item_id
    )
    return result


@router.post("/apply-coupon", response_model=CartResponse)
async def apply_coupon(
        request: ApplyCouponRequest,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await apply_coupon_service(
        db=db,
        user_id=user_id,
        code=request.code
    )
    return result


@router.delete("/remove-coupon", response_model=CartResponse)
async def remove_coupon(
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await remove_coupon_service(
        db=db,
        user_id=user_id
    )
    return result


@router.delete("/", response_model=CartResponse)
async def clear_cart(
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db),
):
    result = await clear_cart_service(
        db=db,
        user_id=user_id
    )
    return result