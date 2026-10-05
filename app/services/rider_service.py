from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rider_model import Rider
from app.models.user_model import User, UserRoleEnum
from app.schemas.rider_schema import RiderCreateRequest, RiderUpdateRequest


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

    # Check Phone

    existing_phone = await db.execute(
        select(Rider).where(
            Rider.phone == request.phone
        )
    )

    if existing_phone.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already exists"
        )

    # Check Vehicle Number

    existing_vehicle = await db.execute(
        select(Rider).where(
            Rider.vehicle_number == request.vehicle_number
        )
    )

    if existing_vehicle.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle number already exists"
        )

    # Create Rider

    rider = Rider(
        phone=request.phone,
        vehicle_type=request.vehicle_type,
        vehicle_number=request.vehicle_number
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



async def update_rider_service(
    db: AsyncSession,
    user_id: int,
    request: RiderUpdateRequest
):
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
    is_available: bool
):
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


async def rider_deactivate_service(
    db: AsyncSession,
    user_id: int
):
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

    # Soft deactivate
    rider.is_active = False

    # Deactivated rider should not remain online/available
    rider.is_online = False
    rider.is_available = False

    await db.commit()
    await db.refresh(rider)

    return rider