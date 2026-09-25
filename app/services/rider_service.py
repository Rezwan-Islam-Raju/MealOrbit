from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rider_model import Rider
from app.models.user_model import User
from app.schemas.rider_schema import RiderCreateRequest, RiderUpdateRequest


async def create_rider_service(
    db: AsyncSession,
    user_id: int,
    request: RiderCreateRequest,
):
    # Check user
    result = await db.execute(
        select(User).where(User.id == user_id,User.is_active.is_(True)))

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check existing rider
    result = await db.execute(select(Rider).where(Rider.user_id == user_id))

    existing_rider = result.scalar_one_or_none()

    if existing_rider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rider profile already exists",
        )

    rider = Rider(
        user_id=user_id,
        phone=request.phone.strip(),
        vehicle_type=(request.vehicle_type.strip()
            if request.vehicle_type
            else None
        ),
        vehicle_number=(
            request.vehicle_number.strip()
            if request.vehicle_number
            else None
        ),
        is_online=False,
        is_available=True,
        is_active=True,
    )

    db.add(rider)

    await db.commit()
    await db.refresh(rider)

    return rider



async def get_my_rider_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True),
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider profile not found",
        )

    return rider



async def update_rider_service(
    db: AsyncSession,
    user_id: int,
    request: RiderUpdateRequest,
):
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True),
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider profile not found",
        )

    if request.phone is not None:
        rider.phone = request.phone.strip()

    if request.vehicle_type is not None:
        rider.vehicle_type = request.vehicle_type.strip()

    if request.vehicle_number is not None:
        rider.vehicle_number = request.vehicle_number.strip()

    await db.commit()
    await db.refresh(rider)

    return rider


async def update_rider_status_service(
    db: AsyncSession,
    user_id: int,
    is_online: bool,
    is_available: bool,
):
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True),
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider profile not found",
        )

    rider.is_online = is_online
    rider.is_available = is_available

    await db.commit()
    await db.refresh(rider)

    return rider


async def rider_deactivate_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True),
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider not found",
        )

    # Soft deactivate
    rider.is_active = False

    # Deactivated rider should not remain online/available
    rider.is_online = False
    rider.is_available = False

    await db.commit()
    await db.refresh(rider)

    return rider