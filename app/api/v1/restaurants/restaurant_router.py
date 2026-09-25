from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.restaurant_schema import (
    RestaurantResponse,
    RestaurantCreateRequest,
    RestaurantStatusUpdateRequest,
    MessageResponse
)
from app.services.restaurant_service import (
    create_restaurant_service,
    get_restaurant_service,
    get_my_restaurants_service,
    update_restaurant_service,
    delete_restaurant_service,
    get_restaurants_service
)
from config.database import get_db

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

# Create Restaurant
@router.post("/", response_model=RestaurantResponse)
async def create_restaurant(
        request: RestaurantCreateRequest,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    result = await create_restaurant_service(
        db=db,
        user_id=user_id,
        request=request,
    )
    return result

# Get All Restaurants
@router.get("/", response_model=list[RestaurantResponse])
async def get_all_restaurants(db: AsyncSession = Depends(get_db)):
    result = await get_restaurants_service(db=db)
    return result

# Get My Restaurants
@router.get("/my", response_model=list[RestaurantResponse])
async def get_my_restaurants(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await get_my_restaurants_service(db=db, user_id=user_id)
    return result

# Get Single Restaurant
@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant_by_id(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_restaurant_service(db=db, restaurant_id=restaurant_id)
    return result

# Update Restaurant Status
@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
        restaurant_id: int,
        request: RestaurantStatusUpdateRequest,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(require_user_id)
):
    result = await update_restaurant_service(
        db=db,
        restaurant_id=restaurant_id,
        user_id=user_id,
        request=request,
    )
    return result

# Delete Restaurant
@router.delete("/{restaurant_id}", response_model=MessageResponse)
async def delete_restaurant(
    restaurant_id: int,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await delete_restaurant_service(
        db=db,
        restaurant_id=restaurant_id,
        user_id=user_id,
    )
    return result
