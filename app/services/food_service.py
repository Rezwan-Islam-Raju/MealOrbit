from math import ceil

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Food, Restaurant, FoodCategory
from app.schemas.food_schema import FoodCreateRequest, FoodUpdateRequest


async def create_food_service(
    request: FoodCreateRequest,
    db: AsyncSession,
    user_id:int
):

    # Check restaurant
    restaurant_result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == request.restaurant_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active.is_(True)
        )
    )

    restaurant = restaurant_result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Restaurant not found"
        )

    # Check food category
    category_result = await db.execute(select(FoodCategory).where(
        FoodCategory.id == request.category_id,
            FoodCategory.is_active.is_(True)
        )
    )

    category = category_result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Clean name
    name = request.name.strip()

    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Food name cannot be empty"
        )

    # Validate price
    if request.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Food price must be greater than 0"
        )

    # Create food
    food = Food(
        restaurant_id=request.restaurant_id,
        category_id=request.category_id,
        name=name,
        description=request.description,
        price=request.price,
        is_available=request.is_available,
    )

    db.add(food)

    await db.commit()
    await db.refresh(food)

    return food


async def get_food_service(db: AsyncSession, user_id:int):
    food_result = await db.execute(select(Food).where(Food.is_available.is_(True)))

    food = food_result.scalars().all()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No available food found")

    return food


async def get_food_by_id_service(db: AsyncSession, food_id:int,user_id:int):
    food_result = await db.execute(select(Food).where(Food.id == food_id))

    food = food_result.scalars().one_or_none()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Food not found")

    return food



async def food_update_by_id_service(
    db: AsyncSession,
    request: FoodUpdateRequest,
    food_id: int,
    user_id: int
):
    # Find food and verify restaurant ownership
    result = await db.execute(
        select(Food)
        .join(Restaurant, Food.restaurant_id == Restaurant.id)
        .where(
            Food.id == food_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active.is_(True)
        )
    )

    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found or you are not the owner"
        )

    # Only update fields sent by the user
    # exclude_unset=True means user jegla pathabe segla hobe
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(food, key, value)

    await db.commit()
    await db.refresh(food)

    return food



async def food_delete_by_id_service(
    db: AsyncSession,
    user_id:int,
    food_id: int
):
    result = await db.execute(select(Food)
            .join(Restaurant, Food.restaurant_id == Restaurant.id)
            .where(Food.id == food_id,Restaurant.owner_id == user_id,
                   Restaurant.is_active.is_(True)
                   )
            )
    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found and you are not the owner"
        )

    # soft delete

    food.is_available= False
    await db.commit()

    return {"message":"Food deleted successfully"}



async def food_search_service(db: AsyncSession, query: str, user_id: int):
    result = await db.execute(
        select(Food).where(
            Food.name.ilike(f"%{query}%"),
            Food.is_available.is_(True)
        )
    )
    foods = result.scalars().all()

    return foods



async def food_filter_service(
        db:AsyncSession,
        category_id:int,
        restaurant_id:int,
        min_price:float,
        max_price:float,
        is_available:bool
):
    query =  select(Food)

    if category_id is not None:
        query = query.where(Food.category_id == category_id)

    if restaurant_id is not None:
        query = query.where(Food.restaurant_id == restaurant_id)

    if min_price is not None:
        query = query.where(Food.price >= min_price)

    if max_price is not None:
        query = query.where(Food.price <= max_price)

    if is_available is not None:
        query = query.where(Food.is_available==is_available)

    result = await db.execute(query)

    foods = result.scalars().all()

    return foods

async def food_update_availability_service(
    db: AsyncSession,
    food_id: int,
    user_id: int,
    is_available: bool
):
    result = await db.execute(
        select(Food)
        .join(
            Restaurant,
            Food.restaurant_id == Restaurant.id
        )
        .where(
            Food.id == food_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active.is_(True)
        )
    )

    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found or you are not the owner"
        )

    food.is_available = is_available

    await db.commit()
    await db.refresh(food)

    return food

async def get_foods_service(
        db:AsyncSession,
        page:int=1,
        limit:int=10,

):

    # offset means skip
    offset = (page-1)*limit


    # total foods
    # sqlachemy count user korar jonnno func use korte hoiche

    count_foods = await db.execute(select(func.count(Food.id))
                .where(Food.is_available.is_(True)
                       )
                )
    total = count_foods.scalar_one()

    # foods

    result = await db.execute(select(Food)
        .where(Food.is_available.is_(True))
        .order_by(Food.id.desc())
        .offset(offset)
        .limit(limit)
        )
    foods = result.scalars().all()

    total_pages = ceil(total/limit) if total>0 else 0

    return {
        "items": foods,
        "total":total,
        "page":page,
        "limit":limit,
        "total_pages":total_pages

    }