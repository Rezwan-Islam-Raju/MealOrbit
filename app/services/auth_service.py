from datetime import datetime, timedelta, timezone


from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.password_reset_token_model import PasswordResetToken
from app.models.refresh_token_model import RefreshToken
from app.models.user_model import User
from app.models.user_activation_token_model import UserActivationToken

from app.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserLoginResponse, UserForgotPasswordRequest, UserForgotPasswordResponse, UserResetPasswordRequest,
    UserResetPasswordResponse, UserChangePasswordRequest, UserChangePasswordResponse, UserLogoutResponse,
    UserLogoutRequest,
)

from config.config import (
    hash_password,
    verify_password,
    generate_activation_token,
    hash_activation_token, hash_refresh_token, generate_refresh_token, encode_access_token, generate_reset_token,
    hash_reset_token,
)



#--------Register---------

async def register_user_service(
    db: AsyncSession,
    request: UserRegisterRequest
):
    # Check email
    result = await db.execute(
        select(User).where(User.email == request.email.strip())
    )

    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check phone
    result = await db.execute(
        select(User).where(User.phone == request.phone)
    )

    existing_phone = result.scalar_one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )

    # Create user
    new_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email.strip(),
        phone=request.phone,
        password=hash_password(request.password),
        is_active=True,
        is_verified=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(new_user)

    try:
        # Save user first
        await db.commit()
        await db.refresh(new_user)

        # Generate activation token
        raw_token = generate_activation_token()
        hashed_token = hash_activation_token(raw_token)

        # Token expires in 5 minutes

        token_expires_at = datetime.now() + timedelta(minutes=5)

        # Create activation token
        db_token = UserActivationToken(
            user_id=new_user.id,
            token_hash=hashed_token,
            expires_at=token_expires_at,
        )

        db.add(db_token)

        # Save activation token
        await db.commit()

        # For testing
        activation_link = raw_token

        print(
            f"ACTIVATION LINK FOR {new_user.email}: "
            f"{activation_link}"
        )

        return new_user

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error"
        )

    except Exception as e:
        await db.rollback()

        print(f"DATABASE ERROR: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


#------Email Verification --------

async def email_verification_service(
    token: str,
    db: AsyncSession,
):
    hashing_token = hash_activation_token(token)

    # Find activation token
    result = await db.execute(
        select(UserActivationToken).where(
            UserActivationToken.token_hash == hashing_token
        )
    )

    activation_token = result.scalar_one_or_none()

    # Token not found
    if not activation_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation token not found"
        )

    # Check token expiry
    if activation_token.expires_at < datetime.now():

        # Delete expired token
        await db.delete(activation_token)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation token expired"
        )

    # Find User
    result = await db.execute(
        select(User).where(
            User.id == activation_token.user_id
        )
    )

    user = result.scalar_one_or_none()

    # User not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )

    # Verify user
    user.is_verified = True
    user.updated_at = datetime.now()

    # Delete used token
    await db.delete(activation_token)

    await db.commit()

    return {
        "message": "Email verified successfully"
    }

#-----Login------

async def login_user_service(
    db: AsyncSession,
    request: UserLoginRequest,
):
    # Find user
    result = await db.execute(
        select(User).where(
            User.email == request.email.strip()
        )
    )

    user = result.scalar_one_or_none()

    # Check user and password
    if not user or not verify_password(
        request.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check account active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Check email verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first",
        )

    # Generate access token
    access_token = encode_access_token(
        user.id,
        user.email,
    )

    # Generate raw refresh token
    raw_refresh_token = generate_refresh_token()

    # Hash refresh token
    refresh_token_hash = hash_refresh_token(
        raw_refresh_token
    )

    # Refresh token expires in 7 days
    expires_at = (
        datetime.now() + timedelta(days=7)
    )

    # Create refresh token record
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
        is_revoked=False,
        created_at=datetime.now(),
    )

    # Add refresh token to database
    db.add(db_refresh_token)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create refresh token",
        )

    # Return tokens
    return UserLoginResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
    )

#-----Forget Password-------


async def forgot_password_service(db: AsyncSession,request:UserForgotPasswordRequest):

    # Find user by email

    result = await db.execute(select(User).where(User.email==request.email))

    user= result.scalar_one_or_none()

    if not user:
      return UserForgotPasswordResponse(
          message="If this email is registered, a password reset link has been sent."
      )

    # Generate raw reset token

    raw_token= generate_reset_token()

    # Hash reset token

    hash_token=hash_reset_token(raw_token)

    # Token expires is 30 minutes

    expires_at = (datetime.now() + timedelta(minutes=30))

    # Create password reset token

    reset_token=PasswordResetToken(
        user_id=user.id,
        token_hash=hash_token,
        expires_at=expires_at,
        created_at=datetime.now()


    )
    # Save token
    db.add(reset_token)

    await db.commit()

    # Testing only

    print(f"Password reset link token for {user.email}: {raw_token}")

    return UserForgotPasswordResponse(
        message="If this email is registered, a password reset link has been sent."
    )


#-----Password reset-------


async def password_reset_service(request:UserResetPasswordRequest,db:AsyncSession):

    # Check password reset confirmation

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Hash incoming reset token

    token_hash = hash_reset_token(request.token)

    # Find reset token
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token_hash==token_hash))
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(status_code=400,detail="Invalid or expired password reset token")


    # Check token expire

    if reset_token.expires_at < datetime.now():
        await db.delete(reset_token)
        await db.commit()
        raise HTTPException(status_code=400,detail="Password reset token expired")

    # Find user

    result = await db.execute(select(User).where(User.id==reset_token.user_id))

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400,detail="User not found")

    # Hash new password

    user.password = hash_password(request.new_password)
    user.updated_at = datetime.now()

    # Delete used reset token

    await db.delete(reset_token)

    #  Revoke all existing refresh tokens

    result = await db.execute(select(RefreshToken).where(RefreshToken.user_id==user.id),RefreshToken.is_revoked==False)

    refresh_tokens = result.scalars().all()

    for refresh_token in refresh_tokens:
        refresh_token.is_revoked = True
        refresh_token.revoked_at = datetime.now()

    # save Everything

    await db.commit()

    return UserResetPasswordResponse(
       message= "Password Reset Successfully"
    )


# ----Change Password-----

async def change_password_service(request:UserChangePasswordRequest,db:AsyncSession,user_id:int):

    # Check new password confirmation

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")

    # Find user

    result = await db.execute(select(User).where(User.id==user_id))

    user= result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400,detail="User not found")

    # check verify password

    if not verify_password(
        request.current_password,
        user.password

    ):
        raise HTTPException(status_code=400,detail="Current password is incorrect")

    # Check new password is different

    if request.current_password == request.new_password:
        raise HTTPException(status_code=400,detail="New password must be different form current password")

    # Hash new password

    user.password= hash_password(request.new_password)

    user.updated_at = datetime.now()

    # Revoke all existing refresh tokens

    result = await db.execute(select(RefreshToken).where(RefreshToken.user_id==user_id),RefreshToken.is_revoked==False)

    refresh_tokens = result.scalars().all()

    for refresh_token in refresh_tokens:
        refresh_token.is_revoked = True
        refresh_token.revoked_at = datetime.now()

    # save everything

    await db.commit()

    return UserChangePasswordResponse(
        message= "Password Changed Successfully"
    )


# -------- Logout --------
async def logout_user_service(
    db: AsyncSession,
    request: UserLogoutRequest,
    user_id: int,
):
    token_hash = hash_refresh_token(
        request.refresh_token
    )

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
        )
    )

    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token already revoked",
        )

    refresh_token.is_revoked = True
    refresh_token.revoked_at = datetime.now()

    await db.commit()

    return UserLogoutResponse(
        message="Logout Successfully"
    )

