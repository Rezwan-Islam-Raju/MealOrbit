from fastapi import APIRouter
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.food_schema import FoodResponse, FoodCreateRequest, FoodUpdateRequest, FoodAvailabilityRequest, \
    FoodPaginationResponse
from app.services.food_service import create_food_service, get_food_service, get_food_by_id_service, \
    food_update_by_id_service, food_delete_by_id_service, food_search_service, food_filter_service, \
     get_foods_service, food_update_availability_service
from config.database import get_db

router = APIRouter()


@router.post("/",response_model=FoodResponse)
async def create_food(
    request:FoodCreateRequest,
    user_id:int=Depends(require_user_id),
    db:AsyncSession=Depends(get_db)
):


    food= await create_food_service(
        db=db,
        user_id=user_id,
        request=request,
    )
    return food



@router.get("/",response_model=list[FoodResponse])
async def get_foods(user_id:int=Depends(require_user_id),db:AsyncSession=Depends(get_db)):

    foods= await get_food_service(
        db=db,
        user_id=user_id,

    )
    return foods


@router.get("/search", response_model=list[FoodResponse])
async def get_foods_search(
    query: str,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await food_search_service(
        db=db,
        query=query,
        user_id=user_id
    )
    return result




@router.get("/filter",response_model=list[FoodResponse])
async def filter_food(
        category_id:int,
        restaurant_id:int,
        min_price:float,
        max_price:float,
        is_available:bool,
        db:AsyncSession=Depends(get_db)
):
    foods = await food_filter_service(
        db=db,
        category_id=category_id,
        restaurant_id=restaurant_id,
        min_price=min_price,
        max_price=max_price,
        is_available=is_available

    )
    return foods


@router.get("/pagination",response_model=FoodPaginationResponse)
async def get_food_pagination(
        page:int =Query(1,ge=1),
        limit:int =Query(10,ge=1,le=100),
        db:AsyncSession=Depends(get_db)
):
    result = await get_foods_service(
        db=db,
        page=page,
        limit=limit
    )
    return result


@router.get("/{food_id}",response_model=FoodResponse)
async def get_food_by_id(
food_id:int,db:AsyncSession=Depends(get_db),
user_id:int=Depends(require_user_id)
):
    food= await get_food_by_id_service(
        db=db,
        user_id=user_id,
        food_id = food_id
    )
    return food

@router.patch("/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: int,
    request: FoodUpdateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await food_update_by_id_service(
        db=db,
        food_id=food_id,
        user_id=user_id,
        request=request
    )

    return result

@router.delete("/{food_id}")
async def delete_food(food_id:int,user_id:int=Depends(require_user_id),db:AsyncSession=Depends(get_db)):

    result= await food_delete_by_id_service(
          db=db,
          food_id=food_id,
          user_id=user_id
    )
    return result




# sudhu restaurant owner er joonno

@router.patch("/{food_id}/availability", response_model=FoodResponse)
async def update_food_availability(
    food_id: int,
    request: FoodAvailabilityRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result= await food_update_availability_service(
        db=db,
        food_id=food_id,
        is_available=request.is_available,
        user_id=user_id
    )

    return result



