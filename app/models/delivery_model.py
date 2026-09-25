import enum

from sqlalchemy import (Column,DateTime,Enum,ForeignKey,Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


class DeliveryStatusEnum(enum.Enum):
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer,primary_key=True,index=True)

    order_id = Column(Integer,ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,unique=True,index=True)

    rider_id = Column(Integer,ForeignKey("riders.id", ondelete="SET NULL"),
        nullable=True,index=True)

    status = Column(Enum(DeliveryStatusEnum),nullable=False,default=DeliveryStatusEnum.ASSIGNED)

    assigned_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    accepted_at = Column(DateTime(timezone=True),nullable=True)

    picked_up_at = Column(DateTime(timezone=True),nullable=True)

    delivered_at = Column(DateTime(timezone=True),nullable=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    updated_at = Column(DateTime(timezone=True),server_default=func.now(),
        onupdate=func.now(),nullable=False)

    rider = relationship("Rider",back_populates="deliveries")

    order = relationship("Order",back_populates="delivery")