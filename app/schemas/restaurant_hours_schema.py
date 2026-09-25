from datetime import time

from pydantic import BaseModel, Field


# ---------- Request Schemas ----------

class RestaurantHoursCreateRequest(BaseModel):
    day_of_week: int = Field(ge=0, le=6)

    opening_time: time | None = None
    closing_time: time | None = None

    is_closed: bool = False


class RestaurantHoursUpdateRequest(BaseModel):
    opening_time: time | None = None
    closing_time: time | None = None

    is_closed: bool | None = None


# ---------- Response Schemas ----------

class RestaurantHoursResponse(BaseModel):
    id: int
    restaurant_id: int
    day_of_week: int

    opening_time: time | None
    closing_time: time | None

    is_closed: bool

    created_at: object
    updated_at: object

