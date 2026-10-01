from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.location_schema import RiderLocationResponse, RiderLocationRequest
from app.services.location_service import update_rider_location_service
from config.database import get_db

router = APIRouter()


#--------- UPDATE RIDER LOCATION API ------
@router.post(
    "/",
    response_model=RiderLocationResponse
)
async def update_rider_location(
    request: RiderLocationRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result= await update_rider_location_service(
        db=db,
        user_id=user_id,
        delivery_id=request.delivery_id,
        latitude=request.latitude,
        longitude=request.longitude
    )
    return result