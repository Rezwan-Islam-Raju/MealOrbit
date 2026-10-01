import enum
from datetime import datetime

from sqlalchemy import (Boolean,Column,DateTime,Enum,Float,ForeignKey,Integer,String,Text)
from sqlalchemy.orm import relationship

from config.database import Base


class StatusEnum(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    BUSY = "BUSY"


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer,primary_key=True,index=True)

    owner_id = Column(Integer,ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    name = Column(String(100),nullable=False,index=True)

    description = Column(Text,nullable=True)

    phone = Column( String(20),nullable=False)

    email = Column(String(255),nullable=True)

    address = Column(String(255),nullable=False)

    city = Column(String(100),nullable=False,index=True)

    area = Column(String(100),nullable=False,index=True)

    latitude = Column(Float,nullable=True)

    longitude = Column(Float,nullable=True)

    image_url = Column(String(500),nullable=True)

    status = Column(Enum(StatusEnum,name="restaurant_status"),nullable=False,
        default=StatusEnum.CLOSED,server_default="CLOSED",index=True)

    is_active = Column(Boolean,nullable=False,default=True,server_default="true",
        index=True)

    created_at = Column(DateTime,nullable=False,default=datetime.now)

    updated_at = Column(DateTime,nullable=False,default=datetime.now,
    onupdate=datetime.now)

    # Relationship with User
    owner = relationship("User",back_populates="restaurants")

    # Relationship with RestaurantHours
    hours = relationship("RestaurantHours",back_populates="restaurant",
    cascade="all, delete-orphan")
    foods = relationship("Food",back_populates="restaurant")