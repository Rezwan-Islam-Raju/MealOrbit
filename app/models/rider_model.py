from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


class Rider(Base):
    __tablename__ = "riders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,unique=True,index=True)

    phone = Column(String(20), nullable=False)
    vehicle_type = Column(String(30), nullable=True)
    vehicle_number = Column(String(50), nullable=True)

    is_online = Column(Boolean,nullable=False,default=False)

    is_available = Column( Boolean,nullable=False,default=True)

    is_active = Column(Boolean,nullable=False,default=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),
        nullable=False)

    user = relationship("User")

    deliveries = relationship("Delivery",back_populates="rider")