from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.order_model import OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    food_id: int
    quantity: int
    price: Decimal
    subtotal: Decimal




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


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


class OrderMessageResponse(BaseModel):
    message: str


