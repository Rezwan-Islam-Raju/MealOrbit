from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.restaurant_hours_schema import RestaurantHoursUpdateRequest, RestaurantHoursResponse, \
    RestaurantHoursCreateRequest
from app.services.restaurant_hours_service import delete_restaurant_hours_service, update_restaurant_hours_service, \
    create_restaurant_hours_service, get_restaurant_hours_service
from config.database import get_db

router = APIRouter(tags=["Restaurant-Hours"])

#-------- Create Restaurant Hours API ------
@router.post(
    "/{restaurant_id}/hours",
    response_model=RestaurantHoursResponse,
)
async def create_restaurant_hours(
    restaurant_id: int,
    request: RestaurantHoursCreateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await create_restaurant_hours_service(
        db=db,
        restaurant_id=restaurant_id,
        user_id=user_id,
        request=request,
    )
    return result


#--------Get Restaurant Hours-----

@router.get("/{restaurant_id}",response_model=list[RestaurantHoursResponse])
async def get_restaurant_hours(restaurant_id: int,db: AsyncSession = Depends(get_db)):

    result= await get_restaurant_hours_service(
        db=db,
        restaurant_id=restaurant_id,
    )
    return result

#--------- Update Restaurant Hours -------
@router.put(
    "/{restaurant_id}/hours/{hour_id}",
    response_model=RestaurantHoursResponse,
)
async def update_restaurant_hours(
    restaurant_id: int,
    hour_id: int,
    request: RestaurantHoursUpdateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await update_restaurant_hours_service(
        db=db,
        restaurant_id=restaurant_id,
        hour_id=hour_id,
        user_id=user_id,
        request=request,
    )
    return result

#------ Delete Restaurant Hours API ---------
@router.delete(
    "/{restaurant_id}/hours/{hour_id}"
)
async def delete_restaurant_hours(
    restaurant_id: int,
    hour_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    data = await delete_restaurant_hours_service(
        db=db,
        restaurant_id=restaurant_id,
        hour_id=hour_id,
        user_id=user_id,
    )
    return data