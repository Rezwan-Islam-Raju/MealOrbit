from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from config.database import get_db


from app.schemas.delivery_schema import DeliveryResponse

from app.services.delivery_service import (
    assign_rider_service,
    get_my_delivery_service,
    get_delivery_by_order_service,
    accept_delivery_service,
    pickup_delivery_service,
    out_for_delivery_service,
    complete_delivery_service,
    cancel_delivery_service,
)


router = APIRouter()




#---------- ASSIGN RIDER AND RESTAURANT Owner API -----------

@router.post(
    "/assign/{order_id}/{rider_id}",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED
)
async def assign_rider(
    order_id: int,
    rider_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await assign_rider_service(
        db=db,
        user_id=user_id,
        order_id=order_id,
        rider_id=rider_id
    )
    return result


#--------- GET MY DELIVERIES AND RIDER API -----------

@router.get(
    "/my",
    response_model=list[DeliveryResponse]
)
async def get_my_deliveries(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await get_my_delivery_service(
        db=db,
        user_id=user_id
    )
    return result



#----------- GET DELIVERY BY ORDER API ----------

@router.get("/order/{order_id}")
async def get_delivery_by_order(
    order_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await get_delivery_by_order_service(
        db=db,
        user_id=user_id,
        order_id=order_id
    )
    return result


#----------- ACCEPT DELIVERY BY RIDER API ----------

@router.patch(
    "/{delivery_id}/accept",
    response_model=DeliveryResponse
)
async def accept_delivery(
    delivery_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await accept_delivery_service(
        db=db,
        user_id=user_id,
        delivery_id=delivery_id
    )
    return result

#---------- PICKUP ORDER BY RIDER API -----------


@router.patch(
    "/{delivery_id}/pickup",
    response_model=DeliveryResponse
)
async def pickup_delivery(
    delivery_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await pickup_delivery_service(
        db=db,
        user_id=user_id,
        delivery_id=delivery_id
    )
    return result



#---------- OUT FOR DELIVERY BY RIDER API ----------

@router.patch(
    "/{delivery_id}/out-for-delivery",
    response_model=DeliveryResponse
)
async def out_for_delivery(
    delivery_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await out_for_delivery_service(
        db=db,
        user_id=user_id,
        delivery_id=delivery_id
    )



#-------- COMPLETE DELIVERY BY RIDER API ----------

@router.patch(
    "/{delivery_id}/complete",
    response_model=DeliveryResponse,
)
async def complete_delivery(
    delivery_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await complete_delivery_service(
        db=db,
        user_id=user_id,
        delivery_id=delivery_id
    )
    return result



#-------- CANCEL DELIVERY BY RIDER API ----------

@router.patch(
    "/{delivery_id}/cancel",
    response_model=DeliveryResponse,
)
async def cancel_delivery(
    delivery_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await cancel_delivery_service(
        db=db,
        user_id=user_id,
        delivery_id=delivery_id,
    )
    return result