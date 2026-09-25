from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from config.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True,autoincrement=True,index=True)

    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True,)

    token_hash = Column(String(255),nullable=False,unique=True,index=True)

    expires_at = Column(DateTime,nullable=False)

    created_at = Column(DateTime,default=datetime.now,nullable=False)