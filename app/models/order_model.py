import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    RIDER_ASSIGNED = "RIDER_ASSIGNED"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",
        ondelete="RESTRICT"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id",
        ondelete="RESTRICT"), nullable=False, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id",
        ondelete="SET NULL"), nullable=True, index=True)
    subtotal = Column(Numeric(10, 2),
        nullable=False)
    delivery_fee = Column(Numeric(10, 2),
        nullable=False, default=0)
    tax = Column(Numeric(10, 2),
        nullable=False, default=0)
    discount = Column(Numeric(10, 2),
        nullable=False, default=0)
    total_amount = Column(Numeric(10, 2),
        nullable=False)
    status = Column(Enum(OrderStatus), nullable=False,
        default=OrderStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True),
        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
        server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    items = relationship("OrderItem", back_populates="order",
                         cascade="all, delete-orphan")
    user = relationship("User")
    restaurant = relationship("Restaurant")
    coupon = relationship("Coupon")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    reviews = relationship("Review", back_populates="order",
                           cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id",
        ondelete="CASCADE"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id",
        ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)

    # Food price at the time of order
    price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    food = relationship("Food")
