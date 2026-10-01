from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.rider_schema import (
    RiderResponse,
    RiderCreateRequest,
    RiderStatusRequest,
    RiderUpdateRequest,
)
from app.services.rider_service import (
    create_rider_service,
    get_my_rider_service,
    update_rider_status_service,
    update_rider_service,
    rider_deactivate_service,
)
from config.database import get_db


router = APIRouter()


#------------ CREATE RAIDER API --------

@router.post(
    "/",
    response_model=RiderResponse
)
async def create_rider(
    request: RiderCreateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await create_rider_service(
        db=db,
        user_id=user_id,
        request=request
    )

    return result

#--------- GET MY RIDER API ----------
@router.get(
    "/me",
    response_model=RiderResponse
)
async def get_my_rider(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await get_my_rider_service(
        db=db,
        user_id=user_id
    )

    return result


#------------- UPDATE RIDER API ----------

@router.patch(
    "/profile",
    response_model=RiderResponse
)
async def update_rider(
    request: RiderUpdateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await update_rider_service(
        db=db,
        user_id=user_id,
        request=request
    )

    return result


#---------- UPDATE RIDER STATUS  API -----------

@router.patch(
    "/status",
    response_model=RiderResponse
)
async def update_rider_status(
    request: RiderStatusRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await update_rider_status_service(
        db=db,
        user_id=user_id,
        is_online=request.is_online,
        is_available=request.is_available
    )

    return result


#--------- RIDER DEACTIVATE API --------------
@router.delete(
    "/me",
    response_model=RiderResponse
)
async def rider_deactivate(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await rider_deactivate_service(
        db=db,
        user_id=user_id
    )

    return result