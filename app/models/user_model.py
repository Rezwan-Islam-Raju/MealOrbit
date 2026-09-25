from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship

from config.database import Base





class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True,index=True)
    first_name=Column(String(50),nullable=False)
    last_name=Column(String(50),nullable=False)
    email = Column(String(50),nullable=False,unique=True,index=True)
    phone = Column(String(20),nullable=False,unique=True,index=True)
    password = Column(String(250),nullable=False)
    role = Column(String(50),default="customer",nullable=False)
    is_active = Column(Boolean,default=True,nullable=False)
    is_verified = Column(Boolean,default=False,nullable=False)
    created_at = Column(DateTime,default=datetime.now,nullable=False)
    updated_at = Column(DateTime,default=datetime.now,nullable=False,onupdate=datetime.now)
    # Restaurant relationship
    restaurants = relationship("Restaurant", back_populates="owner")