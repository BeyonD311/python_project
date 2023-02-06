from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class Status(Base):
    __tablename__ = "status"

    id = Column('id', Integer, primary_key=True),
    name = Column(String)
    users = relationship("UserModel", secondary="user_status", back_populates = "roles")
            
__all__ = ('UserRoles')