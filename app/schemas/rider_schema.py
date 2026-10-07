from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict



# CREATE RIDER REQUEST


class RiderCreateRequest(BaseModel):
    user_id: int

    phone: str = Field(min_length=10, max_length=20)

    vehicle_type: str | None = Field(default=None, max_length=30)

    vehicle_number: str | None = Field(default=None, max_length=50)



# UPDATE RIDER REQUEST


class RiderUpdateRequest(BaseModel):
    phone: str | None = Field(default=None,min_length=10,max_length=20 )

    vehicle_type: str | None = Field(default=None,max_length=30)

    vehicle_number: str | None = Field(default=None,max_length=50 )



# RIDER STATUS REQUEST


class RiderStatusRequest(BaseModel):
    is_online: bool
    is_available: bool


# RIDER RESPONSE


class RiderResponse(BaseModel):
    id: int
    user_id: int
    phone: str
    vehicle_type: str | None
    vehicle_number: str | None

    is_online: bool
    is_available: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime



# RIDER MESSAGE RESPONSE


class RiderMessageResponse(BaseModel):
    message: str

