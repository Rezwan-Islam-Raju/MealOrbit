from sqlalchemy.orm import relationship
from config.database import Base

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime,
   func
)


class Review(Base):

    __tablename__ = "reviews"

    id = Column(Integer,primary_key=True,autoincrement=True)

    # Customer who wrote the review
    user_id = Column(Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,index=True)

    # Food being reviewed
    food_id = Column(Integer,
        ForeignKey("foods.id", ondelete="CASCADE"),
        nullable=False,index=True)

    # Order related to this review
    order_id = Column(Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,index=True)

    # Rating: 1 - 5
    rating = Column(Integer,nullable=False )

    # Optional review comment
    comment = Column( Text,nullable=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now(),
        nullable=False)

    updated_at = Column(DateTime(timezone=True),server_default=func.now(),
        onupdate=func.now(),nullable=False)

    # Relationships
    user = relationship("User",back_populates="reviews")

    food = relationship("Food",back_populates="reviews")

    order = relationship("Order",back_populates="reviews")


