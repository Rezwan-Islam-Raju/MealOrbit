from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=8, max_length=100)

class UserProfileResponse(BaseModel):
    id:int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

class UserLoginResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"

class UserLogoutRequest(BaseModel):
    refresh_token: str


class UserLogoutResponse(BaseModel):
    message: str

class UserRefreshTokenRequest(BaseModel):
    refresh_token: str


class UserRefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserEmailVerificationRequest(BaseModel):
    token: str


class UserEmailVerificationResponse(BaseModel):
    message: str


class UserResendVerificationRequest(BaseModel):
    email: EmailStr


class UserResendVerificationResponse(BaseModel):
    message: str


class UserForgotPasswordRequest(BaseModel):
    email: EmailStr


class UserForgotPasswordResponse(BaseModel):
    message: str


class UserResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)


class UserResetPasswordResponse(BaseModel):
    message: str


class UserChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=100)
    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)


class UserChangePasswordResponse(BaseModel):
    message: str





