from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order_model import OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    food_id: int
    quantity: int
    price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    coupon_id: int | None

    subtotal: Decimal
    delivery_fee: Decimal
    tax: Decimal
    discount: Decimal
    total_amount: Decimal

    status: OrderStatus

    items: list[OrderItemResponse]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


class OrderMessageResponse(BaseModel):
    message: str


