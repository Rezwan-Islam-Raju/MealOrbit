from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurant_hours_model import RestaurantHours
from app.models.restaurants_model import Restaurant
from app.schemas.restaurant_hours_schema import RestaurantHoursCreateRequest, RestaurantHoursUpdateRequest


async def create_restaurant_hours_service(
    db: AsyncSession,
    restaurant_id: int,
    user_id: int,
    request: RestaurantHoursCreateRequest,
):

    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active == True,
        )
    )

    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    existing_result = await db.execute(
        select(RestaurantHours).where(RestaurantHours.restaurant_id == restaurant_id,
            RestaurantHours.day_of_week == request.day_of_week,
        )
    )

    existing_hours = existing_result.scalar_one_or_none()

    if existing_hours:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant hours for this day already exist",
        )

    if not request.is_closed:
        if request.opening_time is None or request.closing_time is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opening and closing time are required",
            )

        if request.opening_time >= request.closing_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opening time must be before closing time",
            )

    restaurant_hours = RestaurantHours(
        restaurant_id=restaurant_id,
        day_of_week=request.day_of_week,
        opening_time=request.opening_time,
        closing_time=request.closing_time,
        is_closed=request.is_closed,
    )

    db.add(restaurant_hours)

    await db.commit()
    await db.refresh(restaurant_hours)

    return restaurant_hours


async def get_restaurant_hours_service(
    db: AsyncSession,
    restaurant_id: int,
):

    result = await db.execute(
        select(RestaurantHours)
        .where(
            RestaurantHours.restaurant_id == restaurant_id
        )
        .order_by(RestaurantHours.day_of_week)
    )

    return result.scalars().all()



async def update_restaurant_hours_service(
    db: AsyncSession,
    restaurant_id: int,
    hour_id: int,
    user_id: int,
    request: RestaurantHoursUpdateRequest,
):

    result = await db.execute(
        select(RestaurantHours)
        .join(Restaurant)
        .where(
            RestaurantHours.id == hour_id,
            RestaurantHours.restaurant_id == restaurant_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active == True,
        )
    )

    hours = result.scalar_one_or_none()

    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant hours not found",
        )

    if request.opening_time is not None:
        hours.opening_time = request.opening_time

    if request.closing_time is not None:
        hours.closing_time = request.closing_time

    if request.is_closed is not None:
        hours.is_closed = request.is_closed

    if not hours.is_closed:

        if hours.opening_time is None or hours.closing_time is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opening and closing time are required",
            )

        if hours.opening_time >= hours.closing_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opening time must be before closing time",
            )

    await db.commit()
    await db.refresh(hours)

    return hours



async def delete_restaurant_hours_service(
    db: AsyncSession,
    restaurant_id: int,
    hour_id: int,
    user_id: int,
):

    result = await db.execute(
        select(RestaurantHours)
        .join(Restaurant)
        .where(
            RestaurantHours.id == hour_id,
            RestaurantHours.restaurant_id == restaurant_id,
            Restaurant.owner_id == user_id,
            Restaurant.is_active == True,
        )
    )

    hours = result.scalar_one_or_none()

    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant hours not found",
        )

    await db.delete(hours)
    await db.commit()

    return {
        "message": "Restaurant hours deleted successfully"
    }