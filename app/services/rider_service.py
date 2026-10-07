from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rider_model import Rider
from app.models.user_model import User, UserRoleEnum
from app.schemas.rider_schema import (
    RiderCreateRequest,
    RiderUpdateRequest
)


# CREATE RIDER SERVICE


async def create_rider_service(
    db: AsyncSession,
    admin_id: int,
    request: RiderCreateRequest
):
    # Check Admin User
    result = await db.execute(
        select(User).where(
            User.id == admin_id,
            User.is_active.is_(True)
        )
    )

    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )

    # Admin Role Check
    if admin.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create rider"
        )

    # Check Rider User
    result = await db.execute(
        select(User).where(
            User.id == request.user_id,
            User.is_active.is_(True)
        )
    )

    rider_user = result.scalar_one_or_none()

    if not rider_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider user not found"
        )

    # Check if User is already a Rider
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == request.user_id
        )
    )

    existing_rider = result.scalar_one_or_none()

    if existing_rider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is already registered as a rider"
        )

    # Check Phone
    result = await db.execute(
        select(Rider).where(
            Rider.phone == request.phone
        )
    )

    existing_phone = result.scalar_one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already exists"
        )

    # Check Vehicle Number
    if request.vehicle_number:
        result = await db.execute(
            select(Rider).where(
                Rider.vehicle_number == request.vehicle_number
            )
        )

        existing_vehicle = result.scalar_one_or_none()

        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle number already exists"
            )

    # Create Rider
    rider = Rider(
        user_id=request.user_id,
        phone=request.phone,
        vehicle_type=request.vehicle_type,
        vehicle_number=request.vehicle_number
    )

    db.add(rider)

    await db.commit()
    await db.refresh(rider)

    return rider


# GET RIDER SERVICE


async def get_rider_service(
    db: AsyncSession,
    user_id: int,
    rider_id: int
):
    # Check User
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True)
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Role Check
    if user.role not in {
        UserRoleEnum.ADMIN,
        UserRoleEnum.RESTAURANT_OWNER
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and restaurant owner can view rider"
        )

    # Get Rider
    result = await db.execute(
        select(Rider).where(
            Rider.id == rider_id,
            Rider.is_active.is_(True)
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider profile not found"
        )

    return rider



# UPDATE RIDER PROFILE SERVICE


async def update_rider_service(
    db: AsyncSession,
    user_id: int,
    request: RiderUpdateRequest
):
    # Get Rider by logged-in User
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider profile not found"
        )

    # Update Phone
    if request.phone is not None:

        result = await db.execute(
            select(Rider).where(
                Rider.phone == request.phone,
                Rider.id != rider.id
            )
        )

        existing_phone = result.scalar_one_or_none()

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists"
            )

        rider.phone = request.phone.strip()

    # Update Vehicle Type
    if request.vehicle_type is not None:
        rider.vehicle_type = request.vehicle_type.strip()

    # Update Vehicle Number
    if request.vehicle_number is not None:

        result = await db.execute(
            select(Rider).where(
                Rider.vehicle_number == request.vehicle_number,
                Rider.id != rider.id
            )
        )

        existing_vehicle = result.scalar_one_or_none()

        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle number already exists"
            )

        rider.vehicle_number = request.vehicle_number.strip()

    await db.commit()
    await db.refresh(rider)

    return rider



# UPDATE RIDER STATUS SERVICE


async def update_rider_status_service(
    db: AsyncSession,
    user_id: int,
    is_online: bool,
    is_available: bool
):
    # Get Rider by logged-in User
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider profile not found"
        )

    rider.is_online = is_online
    rider.is_available = is_available

    await db.commit()
    await db.refresh(rider)

    return rider



# DEACTIVATE RIDER SERVICE


async def rider_deactivate_service(
    db: AsyncSession,
    user_id: int
):
    # Get Rider by logged-in User
    result = await db.execute(
        select(Rider).where(
            Rider.user_id == user_id,
            Rider.is_active.is_(True)
        )
    )

    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider not found"
        )

    # Soft Deactivate
    rider.is_active = False

    # Deactivated Rider cannot be online or available
    rider.is_online = False
    rider.is_available = False

    await db.commit()
    await db.refresh(rider)

    return rider
