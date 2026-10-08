from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.models import User
from app.models.user_model import UserRoleEnum
from app.schemas.admin_schema import AdminUserResponse
from app.services.admin_service import AdminUserService
from config.database import get_db

router = APIRouter()



# Admin Permission


async def require_admin(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role != UserRoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user



# View All Users

@router.get(
    "/users",
    response_model=list[AdminUserResponse]
)
async def get_all_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    users = await AdminUserService.get_all_users(db)

    return users


# Admin Role

@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: UserRoleEnum,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Admin cannot change admin role
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot change his own role"
        )

    user = await AdminUserService.change_user_role(
        db=db,
        user_id=user_id,
        new_role=new_role
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User role updated successfully",
        "user_id": user.id,
        "role": user.role,
    }




# Block User


@router.patch("/users/{user_id}/block")
async def block_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot block himself"
        )

    user = await AdminUserService.block_user(
        db=db,
        user_id=user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User blocked successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }



# Unblock User


@router.patch("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user = await AdminUserService.unblock_user(
        db=db,
        user_id=user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User unblocked successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }



# Delete User


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete himself"
        )

    user = await AdminUserService.delete_user(
        db=db,
        user_id=user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }