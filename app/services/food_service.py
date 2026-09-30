import json
from math import ceil

from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.cache import invalidate_food_cache
from app.core.redis import redis_client
from app.models import Food, Restaurant, FoodCategory
from app.models.user_model import User, UserRoleEnum
from app.schemas.food_schema import FoodCreateRequest, FoodUpdateRequest


async def create_food_service(
    request: FoodCreateRequest,
    db: AsyncSession,
    user_id: int
):
    # Get current user
    user_result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True)
        )
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check restaurant access
    if user.role == UserRoleEnum.ADMIN:
        restaurant_result = await db.execute(
            select(Restaurant).where(
                Restaurant.id == request.restaurant_id,
                Restaurant.is_active.is_(True)
            )
        )

    elif user.role == UserRoleEnum.RESTAURANT_OWNER:
        restaurant_result = await db.execute(
            select(Restaurant).where(
                Restaurant.id == request.restaurant_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or restaurant owner can create food"
        )

    restaurant = restaurant_result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    # Check food category
    category_result = await db.execute(
        select(FoodCategory).where(
            FoodCategory.id == request.category_id,
            FoodCategory.is_active.is_(True)
        )
    )

    category = category_result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Clean food name
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        is_available=request.is_available
    )

    db.add(food)

    await db.commit()
    await db.refresh(food)

    # Invalidate food cache
    await invalidate_food_cache()

    return food



async def get_food_service(db: AsyncSession):
    food_result = await db.execute(select(Food).where(Food.is_available.is_(True)))

    food = food_result.scalars().all()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No available food found"
                            )

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
    # Get current user
    user_result = await db.execute(select(User).where(User.id == user_id))

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get food
    food_result = await db.execute( select(Food).where(Food.id == food_id))

    food = food_result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )

    # Admin can update any food
    if user.role != "admin":

        # Non-admin must be restaurant owner
        restaurant_result = await db.execute(
            select(Restaurant).where(
                Restaurant.id == food.restaurant_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
        )

        restaurant = restaurant_result.scalar_one_or_none()

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this food"
            )

    # Update food
    update_data = request.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(food, key, value)

    await db.commit()
    await db.refresh(food)

    await invalidate_food_cache()

    return food



async def food_delete_by_id_service(
    db: AsyncSession,
    user_id: int,
    food_id: int
):
    #  Current user found
    user_result = await db.execute(select(User).where(User.id == user_id))

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    #  Food found
    food_result = await db.execute(select(Food).where( Food.id == food_id))

    food = food_result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )

    #  If the user is not an admin, check restaurant ownership
    if user.role != "admin":

        restaurant_result = await db.execute(
            select(Restaurant).where(
                Restaurant.id == food.restaurant_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
        )

        restaurant = restaurant_result.scalar_one_or_none()

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this food"
            )

    #  Soft delete
    food.is_available = False

    await db.commit()

    #  Redis cache invalidate
    await invalidate_food_cache()

    return {
        "message": "Food deleted successfully"
    }


async def food_search_service(
    db: AsyncSession,
    query: str
):
    query = query.strip().lower()

    if not query:
        return []

    # Redis key
    cache_key = f"foods:search:{query}"

    # Redis HIT check
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # PostgreSQL query
    result = await db.execute(
        select(Food).where(
            Food.name.ilike(f"%{query}%"),
            Food.is_available.is_(True)
        )
    )
    foods = result.scalars().all()

    # Convert SQLAlchemy objects to JSON
    response = [
        {
            "id": food.id,
            "restaurant_id": food.restaurant_id,
            "category_id": food.category_id,
            "name": food.name,
            "description": food.description,
            "price": food.price,
            "is_available": food.is_available,
        }
        for food in foods
    ]

    # Save in Redis for 60 seconds
    await redis_client.set(
        cache_key,
        json.dumps(response),
        ex=60
    )
    return response



async def food_filter_service(
    db: AsyncSession,
    category_id: int | None = None,
    restaurant_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    is_available: bool | None = None
):
    # Redis cache key
    cache_key = (
        f"foods:filter:"
        f"category:{category_id}:"
        f"restaurant:{restaurant_id}:"
        f"min:{min_price}:"
        f"max:{max_price}:"
        f"available:{is_available}"
    )

    # Redis HIT
    cached_data = await redis_client.get(cache_key)

    if cached_data:

        return json.loads(cached_data)

    # PostgreSQL query
    query = select(Food)

    if category_id is not None:
        query = query.where(Food.category_id == category_id)

    if restaurant_id is not None:
        query = query.where(Food.restaurant_id == restaurant_id)

    if min_price is not None:
        query = query.where(Food.price >= min_price)

    if max_price is not None:
        query = query.where(Food.price <= max_price)

    if is_available is not None:
        query = query.where(Food.is_available == is_available)

    result = await db.execute(query)

    foods = result.scalars().all()

    # Convert SQLAlchemy objects to JSON
    response = [
        {
            "id": food.id,
            "restaurant_id": food.restaurant_id,
            "category_id": food.category_id,
            "name": food.name,
            "description": food.description,
            "price": food.price,
            "is_available": food.is_available,
        }
        for food in foods
    ]

    # Save in Redis
    await redis_client.set(
        cache_key,
        json.dumps(response),
        ex=60
    )
    return response


async def food_update_availability_service(
    db: AsyncSession,
    food_id: int,
    user_id: int,
    is_available: bool
):
    # 1. Get current user
    user_result = await db.execute(select(User).where( User.id == user_id))

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2. Get food
    food_result = await db.execute(
        select(Food).where(
            Food.id == food_id
        )
    )

    food = food_result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )

    # 3. If the user is not an admin, check restaurant ownership
    if user.role != "admin":

        restaurant_result = await db.execute(select(Restaurant).where(
                Restaurant.id == food.restaurant_id,
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
        )

        restaurant = restaurant_result.scalar_one_or_none()

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update food availability"
            )

    # 4. Update availability
    food.is_available = is_available

    await db.commit()
    await db.refresh(food)

    # 5. Invalidate Redis food cache
    await invalidate_food_cache()

    return food


async def get_foods_service(
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
):
    # Redis cache key
    cache_key = f"foods:pagination:page:{page}:limit:{limit}"

    #  Check Redis

    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    #  Redis MISS
    #  PostgreSQL query

    offset = (page - 1) * limit

    # Total foods
    count_foods = await db.execute(select(func.count(Food.id))
        .where(
            Food.is_available.is_(True)
        )
    )

    total = count_foods.scalar_one()

    # Foods
    result = await db.execute(select(Food)
        .where(
            Food.is_available.is_(True)
        )
        .order_by(Food.id.desc())
        .offset(offset)
        .limit(limit)
    )

    foods = result.scalars().all()

    total_pages = ceil(total / limit) if total > 0 else 0

    #  Convert SQLAlchemy
    #  JSON serializable data

    response = {
        "items": [
            {
                "id": food.id,
                "restaurant_id": food.restaurant_id,
                "category_id": food.category_id,
                "name": food.name,
                "description": food.description,
                "price": food.price,
                "image_url": food.image_url,
                "is_available": food.is_available,
            }
            for food in foods
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }

    #  Save response in Redis

    await redis_client.set(
        cache_key,
        json.dumps(response),
        ex=60
    )

    return response
