from sqlalchemy import (Column, Integer, String, Text, Boolean, DateTime, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


class FoodCategory(Base):
    __tablename__ = "food_category"

    id = Column(Integer,primary_key=True,index=True)

    restaurant_id = Column(Integer,ForeignKey(
        "restaurants.id",
         ondelete="CASCADE"),
        nullable=False,index=True)
    name = Column(String(100),nullable=False,unique=True,index=True)

    description = Column(Text,nullable=True)

    img_url = Column(String(500),nullable=False)

    is_active = Column(Boolean,default=True,nullable=False)

    created_at = Column(DateTime,server_default=func.now(),nullable=False)

    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)

    restaurant = relationship(
        "Restaurant", back_populates="food_categories")

    foods = relationship("Food",back_populates="category")