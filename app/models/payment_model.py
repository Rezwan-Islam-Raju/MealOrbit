from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from config.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id",
            ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)
    transaction_id = Column(String(100), nullable=False,
            unique=True, index=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False,
            default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False,
            default=datetime.now, onupdate=datetime.now)

    order = relationship("Order", back_populates="payments")
