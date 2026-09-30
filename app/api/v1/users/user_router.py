from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from config.database import get_db

from app.schemas.user_schema import (
    UserProfileAllResponse,
    UserUpdateProfileRequest,
    UserUpdateProfileResponse,
    UserProfileImageResponse,
    UserUpdatePhoneRequest,
    UserUpdatePhoneResponse,
    UserDeactivateResponse, UserDeleteProfileImageResponse
)

from app.services.user_service import (
    profile_all_service,
    update_profile_service,
    upload_profile_image_service,
    delete_profile_image_service,
    update_phone_service,
    deactivate_account_service
)


router = APIRouter()



@router.get(
    "/profile/all",
    response_model=UserProfileAllResponse
)
async def get_profile(
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    result= await profile_all_service(
        db=db,
        user_id=user_id
    )
    return result


@router.patch(
    "/profile",
    response_model=UserUpdateProfileResponse
)
async def update_profile(
        data: UserUpdateProfileRequest,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    await update_profile_service(
        db=db,
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone
    )

    return {
        "message": "Profile updated successfully"
    }


@router.post(
    "/profile-image",
    response_model=UserProfileImageResponse
)
async def upload_profile_image(
        file: UploadFile = File(...),
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    result= await upload_profile_image_service(
        db=db,
        user_id=user_id,
        file=file
    )
    return result


@router.delete(
    "/profile-image",
    response_model=UserDeleteProfileImageResponse
)
async def delete_profile_image(
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    result= await delete_profile_image_service(
        db=db,
        user_id=user_id
    )
    return result


@router.patch(
    "/phone",
    response_model=UserUpdatePhoneResponse
)
async def update_phone(
        data: UserUpdatePhoneRequest,
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    await update_phone_service(
        db=db,
        user_id=user_id,
        phone=data.phone
    )

    return {
        "message": "Phone number updated successfully"
    }


@router.delete(
    "/account",
    response_model=UserDeactivateResponse
)
async def deactivate_account(
        user_id: int = Depends(require_user_id),
        db: AsyncSession = Depends(get_db)
):
    result= await deactivate_account_service(
        db=db,
        user_id=user_id
    )
    return result