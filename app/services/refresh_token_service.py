from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import (
    encode_access_token,
    hash_refresh_token,
)

from app.models.refresh_token_model import RefreshToken
from app.models.user_model import User


async def refresh_access_token_service(
    db: AsyncSession,
    refresh_token: str,
):
    # 1. Hash incoming refresh token
    token_hash = hash_refresh_token(refresh_token)

    # 2. Find refresh token in database
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    stored_token = result.scalar_one_or_none()

    # 3. Check token exists
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # 4. Check if token is revoked
    if stored_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    # 5. Check token expiry
    if stored_token.expires_at < datetime.now():
        stored_token.is_revoked = True
        stored_token.revoked_at = datetime.now()

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # 6. Find user
    result = await db.execute(
        select(User).where(
            User.id == stored_token.user_id
        )
    )

    user = result.scalar_one_or_none()

    # 7. Check user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 8. Check user active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # 9. Generate new access token
    access_token = encode_access_token(
        user.id,
        user.email,
    )

    # 10. Return new access token
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }