from sqlalchemy import Column, ForeignKey, Integer
from app.kernel.database import Base

class UserRoles(Base):
    __tablename__ = "user_roles"

    id = Column('id', Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    role_id = Column(ForeignKey("roles.id"), primary_key=True)
            
__all__ = ('UserRoles')