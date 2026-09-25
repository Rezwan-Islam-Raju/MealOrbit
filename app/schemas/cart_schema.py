from datetime import datetime
from pydantic import BaseModel,Field


class CartItemCreateRequest(BaseModel):
    food_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    id: int
    food_id: int
    food_name: str
    food_price: float
    quantity: int
    subtotal: float




class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total_items: int
    subtotal: float
    coupon_code: str | None
    discount_amount: float
    grand_total: float
    created_at: datetime
    updated_at: datetime

