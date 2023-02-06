from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from app.kernel.database import Base

class UserStatus(Base):
    __tablename__ = "user_status"

    id = Column('id', Integer, primary_key=True),
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    role_id = Column(ForeignKey("status.id"), primary_key=True)
    timestamp_at = Column(TIMESTAMP, nullable=True)
            
__all__ = ('UserStatus')