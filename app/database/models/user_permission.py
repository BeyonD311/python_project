from sqlalchemy import Boolean, Column, ForeignKey, String, BigInteger
from app.kernel.database import Base

class UsersPermission(Base):

    __tablename__ = "users_permission"
    id = Column('id', BigInteger, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    role_id = Column(ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"))
    module_id = Column(ForeignKey("permissions.id", ondelete="CASCADE", onupdate="CASCADE")) 
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    method_access = Column(String(10), default='00000')
    
    def __repr__(self) -> str:
        return "<UsersPermission("\
            f"user_id={self.user_id}"\
            f"role_id={self.role_id}"\
            f"module_id={self.module_id}"\
            f"is_active={self.is_active}"\
            f"is_available={self.is_available}"\
            f"method_access={self.method_access}"\
            ")>" 
            