import enum

from sqlalchemy import Column, Integer, ForeignKey, String, Text, Enum, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from config.database import Base




class NotificationTypeEnum(enum.Enum):

    ORDER = "ORDER"
    PAYMENT = "PAYMENT"
    RIDER = "RIDER"
    RESTAURANT = "RESTAURANT"
    PROMOTION = "PROMOTION"
    SYSTEM = "SYSTEM"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer,primary_key=True, autoincrement=True,nullable=False,
                index=True)

    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),
                     nullable=False,index=True)

    title = Column(String(255),nullable=False)

    message = Column(Text,nullable=False)

    notification_type = Column(Enum(NotificationTypeEnum),nullable=False,
        default=NotificationTypeEnum.SYSTEM)


    is_read = Column(Boolean,default=False,nullable=False)

    created_at = Column(DateTime(timezone=True),
    server_default=func.now(),nullable=False)

    updated_at = Column(DateTime(timezone=True),server_default=func.now(),
               onupdate=func.now(),nullable=False)



    # relationship

    user = relationship("User", back_populates="notifications")

