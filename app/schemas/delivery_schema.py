from datetime import datetime

from pydantic import BaseModel

from app.models.delivery_model import DeliveryStatusEnum


class DeliveryStatusUpdateRequest(BaseModel):
    status: DeliveryStatusEnum


class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    rider_id: int | None
    status: DeliveryStatusEnum

    assigned_at: datetime
    accepted_at: datetime | None
    picked_up_at: datetime | None
    delivered_at: datetime | None

    created_at: datetime
    updated_at: datetime

