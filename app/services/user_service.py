import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import User




async def profile_all_service(
        db: AsyncSession,
        user_id: int
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def update_profile_service(
        db: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        phone: str | None = None
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    if email is not None:
        user.email = email

    if phone is not None:
        existing_result = await db.execute(
            select(User).where(
                User.phone == phone,
                User.id != user_id
            )
        )

        existing_user = existing_result.scalars().first()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already exists"
            )

        user.phone = phone

    await db.commit()
    await db.refresh(user)

    return user


async def upload_profile_image_service(
        db: AsyncSession,
        user_id: int,
        file: UploadFile
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Allowed image types
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG and WEBP images are allowed"
        )

    # Upload directory
    upload_dir = "uploads/profiles"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    extension = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        upload_dir,
        filename
    )

    # Save file
    contents = await file.read()

    # 5 MB limit
    max_size = 5 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size must be less than 5 MB"
        )

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Delete old image
    if user.profile_image:
        old_file_path = user.profile_image

        if os.path.exists(old_file_path):

            os.remove(old_file_path)

    # Save path in database
    user.profile_image = file_path.replace("\\", "/")

    await db.commit()
    await db.refresh(user)

    return user



async def delete_profile_image_service(
        db: AsyncSession,
        user_id: int
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.profile_image is None:
        return {
            "message": "Profile image not found"
        }

    user.profile_image = None

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Profile image deleted successfully"
    }



async def update_phone_service(
        db: AsyncSession,
        user_id: int,
        phone: str
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_result = await db.execute(
        select(User).where(
            User.phone == phone,
            User.id != user_id
        )
    )

    existing_user = existing_result.scalars().first()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already exists"
        )

    user.phone = phone

    await db.commit()
    await db.refresh(user)

    return user


async def deactivate_account_service(
        db: AsyncSession,
        user_id: int
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already deactivated"
        )

    user.is_active = False

    await db.commit()

    return {
        "message": "Account deactivated successfully"
    }