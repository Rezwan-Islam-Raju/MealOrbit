from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

from config.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer,primary_key=True,autoincrement=True,index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)

    token_hash = Column(String(255),nullable=False, unique=True, index=True)

    expires_at = Column(DateTime,nullable=False)

    is_revoked = Column(Boolean,default=False,nullable=False)

    created_at = Column(DateTime,default=datetime.now, nullable=False)

    revoked_at = Column(DateTime, nullable=True)