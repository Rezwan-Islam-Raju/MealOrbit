from datetime import datetime

from pydantic import BaseModel, Field


class PaymentCreateRequest(BaseModel):
    order_id: int = Field(gt=0)

    payment_method: str = Field(
        min_length=2,
        max_length=30,
    )


class PaymentCreateResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    transaction_id: str
    payment_url: str
    status: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime



class PaymentMessageResponse(BaseModel):
    message: str

class PaymentSuccessRequest(BaseModel):
    tran_id: str
    val_id: str
    status: str