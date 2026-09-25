from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class DiscountTypeEnum(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"


class CouponCreateRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    discount_type: DiscountTypeEnum
    discount_value: float = Field(..., gt=0)
    min_order_amount: float = Field(default=0, ge=0)
    max_discount: float | None = Field(default=None, gt=0)
    usage_limit: int | None = Field(default=None, gt=0)
    expiry_date: datetime


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_type: DiscountTypeEnum
    discount_value: float
    min_order_amount: float
    max_discount: float | None
    usage_limit: int | None
    used_count: int
    expiry_date: datetime
    is_active: bool




class ApplyCouponRequest(BaseModel):
    code: str