from sqlalchemy import ( Column,Integer,String,Text,Float,Boolean,DateTime,ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer,primary_key=True,index=True)

    restaurant_id = Column(Integer,ForeignKey("restaurants.id",ondelete="CASCADE"
        ),nullable=False,index=True)

    category_id = Column(Integer,ForeignKey("food_category.id",ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    name = Column(String(150),nullable=False,index=True)

    description = Column(Text,nullable=True)

    price = Column(Float,nullable=False)

    image_url = Column(String(500),nullable=True)

    is_available = Column(Boolean,nullable=False,default=True)

    created_at = Column(DateTime,server_default=func.now(),nullable=False)

    updated_at = Column( DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)

    restaurant = relationship("Restaurant",back_populates="foods")

    category = relationship("FoodCategory",back_populates="foods")

    reviews = relationship("Review",back_populates="food",
        cascade="all, delete-orphan")