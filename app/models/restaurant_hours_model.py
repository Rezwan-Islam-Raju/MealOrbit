from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Time, Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


class RestaurantHours(Base):
    __tablename__ = "restaurant_hours"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_id = Column(Integer,ForeignKey("restaurants.id", ondelete="CASCADE"),
                nullable=False,index=True )

    day_of_week = Column(Integer, nullable=False)

    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)

    is_closed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),
        nullable=False
    )

    restaurant = relationship("Restaurant",back_populates="hours")