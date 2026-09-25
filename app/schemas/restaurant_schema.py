from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class StatusEnum(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    BUSY = "BUSY"


# ---------- Request Schemas ----------

class RestaurantCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    phone: str = Field(min_length=10, max_length=20)
    email: EmailStr
    address: str = Field(min_length=5, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    area: str = Field(min_length=2, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = Field(default=None, max_length=500)


class RestaurantStatusUpdateRequest(BaseModel):
    status: StatusEnum
    


# ---------- Response Schemas ----------

class RestaurantResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    phone: str
    email: EmailStr
    address: str
    city: str
    area: str
    latitude: float | None
    longitude: float | None
    image_url: str | None
    status: StatusEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

class RestaurantListResponse(BaseModel):
    id: int
    name: str
    description: str | None
    city: str
    area: str
    image_url: str | None
    status: StatusEnum
    is_active: bool



class MessageResponse(BaseModel):
    message: str
