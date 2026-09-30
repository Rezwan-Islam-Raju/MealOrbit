from fastapi import APIRouter
from fastapi.params import Depends

from sqlalchemy.ext.asyncio import AsyncSession


from app.core.rate_limit import rate_limit
from app.dependencies.auth_dependecy import require_user_id


from app.schemas.user_schema import UserProfileResponse, UserRegisterRequest, UserLoginResponse, UserLoginRequest, \
    UserEmailVerificationRequest, UserEmailVerificationResponse, UserRefreshTokenResponse, UserRefreshTokenRequest, \
    UserForgotPasswordResponse, UserForgotPasswordRequest, UserResetPasswordResponse, UserResetPasswordRequest, \
    UserChangePasswordResponse, UserChangePasswordRequest, UserLogoutRequest, UserLogoutResponse
from app.services.auth_service import register_user_service, email_verification_service, login_user_service, \
    forgot_password_service, password_reset_service, change_password_service, logout_user_service
from app.services.refresh_token_service import refresh_access_token_service
from config.config import verify_password, encode_access_token, encode_refresh_token, generate_refresh_token
from config.database import get_db

router = APIRouter()



# ---------Register API--------


@router.post("/register",response_model=UserProfileResponse)
async def register(request:UserRegisterRequest,db:AsyncSession=Depends(get_db)):

    result = await register_user_service(
        db=db,
        request=request
    )
    return result



# -------- Email Verification API --------



@router.post(
    "/verify-email",
    response_model=UserEmailVerificationResponse,
    dependencies=[
        Depends(rate_limit(limit=5, window=60))
    ]
)
async def verify_email(
    request: UserEmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await email_verification_service(
        db=db,
        token=request.token
    )

    return result

# --------- Login API ---------

@router.post(
    "/login",
    response_model=UserLoginResponse,
    dependencies=[
        Depends(rate_limit(limit=5, window=60))
    ]
)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await login_user_service(
        db=db,
        request=request,
    )

    return result


#--------Refresh Token--------

@router.post(
    "/refresh-token",
    response_model=UserRefreshTokenResponse,
)
async def refresh_token(
    request: UserRefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await refresh_access_token_service(
        db=db,
        refresh_token=request.refresh_token,
    )

    return result


#-----Forgot Password-----

@router.post("/forgot-password",
             response_model=UserForgotPasswordResponse,
             dependencies=[Depends(rate_limit(limit=3, window=60))]
)
async def forgot_password(
    request: UserForgotPasswordRequest,db:AsyncSession = Depends(get_db)
):
    result = await forgot_password_service(
        db=db,
        request=request
    )
    return result


#-----Password Reset ----

@router.post("/password-reset",response_model=UserResetPasswordResponse)
async def password_reset(
    request: UserResetPasswordRequest,db:AsyncSession = Depends(get_db)
):
    result= await password_reset_service(
        db=db,
        request=request
    )
    return result

#---- change password ----

@router.patch("/change-password",response_model=UserChangePasswordResponse)
async def change_password(request: UserChangePasswordRequest,user_id:int=Depends(require_user_id),db:AsyncSession = Depends(get_db)):
    data= await change_password_service(
        db=db,
        request=request,
        user_id=user_id
    )
    return data

#-----Logout------



@router.post(
    "/logout",
    response_model=UserLogoutResponse,
)
async def logout_user(
    request: UserLogoutRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await logout_user_service(
        db=db,
        request=request,
        user_id=user_id,
    )

    return result