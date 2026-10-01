from datetime import datetime

from pydantic import BaseModel

from app.models.notification_model import NotificationTypeEnum


class NotificationCreateRequest(BaseModel):
    order_id: int
    title: str
    message: str
    notification_type: NotificationTypeEnum = NotificationTypeEnum.SYSTEM

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: NotificationTypeEnum
    is_read: bool
    created_at: datetime
    updated_at: datetime


class NotificationMessageResponse(BaseModel):
    message: str

class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
