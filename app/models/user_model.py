import enum
from datetime import datetime


from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum
from sqlalchemy.orm import relationship

from config.database import Base


class UserRoleEnum(enum.Enum):
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    RIDER = "rider"
    ADMIN = "admin"





class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)

    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)

    phone = Column(String(20), unique=True, nullable=True)

    password = Column(String(255), nullable=False)

    profile_image = Column(String(500), nullable=True)



    role = Column(Enum(
            UserRoleEnum,values_callable=lambda enum_class: [
            member.value for member in enum_class]),
        default=UserRoleEnum.CUSTOMER,nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    is_verified = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships

    restaurants = relationship("Restaurant",back_populates="owner")

    reviews = relationship("Review",back_populates="user",cascade="all, delete-orphan")

    notifications = relationship("Notification",
    back_populates="user", cascade="all, delete-orphan")
