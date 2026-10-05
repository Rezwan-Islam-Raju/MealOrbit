from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurants_model import Restaurant, StatusEnum
from app.models.user_model import UserRoleEnum, User
from app.schemas.restaurant_schema import (
    RestaurantCreateRequest,
    RestaurantStatusUpdateRequest,
)



async def create_restaurant_service(
    db: AsyncSession,
    user_id: int,
    request: RestaurantCreateRequest
):
    # Check user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Only admin can create restaurant
    if user.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin can create a restaurant"
        )

    restaurant_name = request.name.strip()

    # Check duplicate restaurant name
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.name.ilike(restaurant_name)
        )
    )

    existing_restaurant = result.scalar_one_or_none()

    if existing_restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant with this name already exists"
        )

    # Create restaurant
    restaurant = Restaurant(
        owner_id=user_id,
        name=restaurant_name,
        description=request.description,
        phone=request.phone,
        email=request.email,
        address=request.address,
        city=request.city,
        area=request.area,
        latitude=request.latitude,
        longitude=request.longitude,
        image_url=request.image_url,
        status=StatusEnum.CLOSED,
        is_active=True
    )

    db.add(restaurant)

    await db.commit()
    await db.refresh(restaurant)

    return restaurant

async def get_restaurant_service(
    db: AsyncSession,
    restaurant_id: int
):
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True)
        )
    )

    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant not found"
        )

    return restaurant


async def get_restaurants_service(
    db: AsyncSession
):
    result = await db.execute(
        select(Restaurant)
        .where(
            Restaurant.is_active.is_(True),
        )
        .order_by(
            Restaurant.id.desc()
        )
    )

    restaurants = result.scalars().all()

    return restaurants


async def get_my_restaurants_service(
    db: AsyncSession,
    user_id: int
):
    # Get current user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # ADMIN →  active restaurant
    if user.role == UserRoleEnum.ADMIN:
        result = await db.execute(
            select(Restaurant)
            .where(
                Restaurant.is_active.is_(True)
            )
            .order_by(Restaurant.id.desc())
        )

        return result.scalars().all()

    # RESTAURANT_OWNER →  restaurant
    if user.role == UserRoleEnum.RESTAURANT_OWNER:
        result = await db.execute(
            select(Restaurant)
            .where(
                Restaurant.owner_id == user_id,
                Restaurant.is_active.is_(True)
            )
            .order_by(Restaurant.id.desc())
        )

        return result.scalars().all()

    # Other roles
    raise HTTPException(
        status_code=403,
        detail="Only admin or restaurant owner can access restaurants"
    )

async def update_restaurant_service(
    db: AsyncSession,
    restaurant_id: int,
    user_id: int,
    request: RestaurantStatusUpdateRequest
):
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True)
        )
    )

    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant not found"
        )

    # Owner check
    if restaurant.owner_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this restaurant"
        )

    updated_data = request.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(restaurant, field, value)

    await db.commit()
    await db.refresh(restaurant)

    return restaurant


async def update_restaurant_status_service(
    db: AsyncSession,
    restaurant_id: int,
    user_id: int,
    request: RestaurantStatusUpdateRequest
):
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True)
        )
    )

    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant not found"
        )

    # Owner check
    if restaurant.owner_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this restaurant"
        )

    restaurant.status = request.status

    await db.commit()
    await db.refresh(restaurant)

    return restaurant


async def delete_restaurant_service(
    db: AsyncSession,
    restaurant_id: int,
    user_id: int
):
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True)
        )
    )

    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant not found"
        )

    # Owner check
    if restaurant.owner_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this restaurant"
        )

    # Soft delete
    restaurant.is_active = False

    await db.commit()

    return {
        "message": "Restaurant deleted successfully"
    }