from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.order_schema import OrderResponse, OrderStatusUpdateRequest
from app.services.order_service import create_order_from_cart_service, get_my_orders_service, \
    get_my_order_by_id_service, cancel_order_service, get_restaurant_orders_service, get_restaurant_order_by_id_service, \
    update_restaurant_order_status_service
from config.database import get_db


router = APIRouter()



@router.post(
    "/checkout",
    response_model=OrderResponse
)
async def checkout(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    order = await create_order_from_cart_service(
        db=db,
        user_id=user_id
    )

    return order


@router.get(
    "/my",
    response_model=list[OrderResponse],
)
async def get_my_orders(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await get_my_orders_service(
        db=db,
        user_id=user_id,
    )



@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
async def get_my_order(
    order_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await get_my_order_by_id_service(
        db=db,
        user_id=user_id,
        order_id=order_id,
    )
    return result



@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
async def cancel_order(
    order_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await cancel_order_service(
        db=db,
        user_id=user_id,
        order_id=order_id,
    )
    return result



@router.get(
    "/restaurant/my-orders",
    response_model=list[OrderResponse],
)

async def get_restaurant_orders(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await get_restaurant_orders_service(
        db=db,
        user_id=user_id,
    )
    return result


@router.get(
    "/restaurant/{order_id}",
    response_model=OrderResponse,
)
async def get_restaurant_order(
    order_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await get_restaurant_order_by_id_service(
        db=db,
        user_id=user_id,
        order_id=order_id,
    )
    return result



@router.patch(
    "/restaurant/{order_id}/status",
    response_model=OrderResponse,
)
async def update_restaurant_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await update_restaurant_order_status_service(
        db=db,
        user_id=user_id,
        order_id=order_id,
        new_status=request.status,
    )
    return result