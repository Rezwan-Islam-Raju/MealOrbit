from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.user_model import UserRoleEnum


class AdminUserService:

    @staticmethod
    async def get_all_users(
        db: AsyncSession,
    ):
        result = await db.execute(select(User).order_by(User.id.desc()))

        result= result.scalars().all()
        return result

    @staticmethod
    async def change_user_role(
            db: AsyncSession,
            user_id: int,
            new_role: UserRoleEnum
    ):
        result = await db.execute(select(User).where(User.id == user_id) )

        user = result.scalar_one_or_none()

        if not user:
            return None

        user.role = new_role

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def block_user(db: AsyncSession,user_id: int):
        result = await db.execute(select(User).where(User.id == user_id) )

        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = False

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def unblock_user(db: AsyncSession,user_id: int ):
        result = await db.execute(select(User).where(User.id == user_id) )

        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = True

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete_user(db: AsyncSession,user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if not user:
            return None

        await db.delete(user)
        await db.commit()

        return user