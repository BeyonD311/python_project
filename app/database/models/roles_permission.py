from sqlalchemy import Boolean, Column, ForeignKey, String, BigInteger
from app.kernel.database import Base

class RolesPermission(Base):

    __tablename__ = "roles_permission"
    id = Column('id', BigInteger, primary_key=True)
    role_id = Column(ForeignKey("roles.id"), primary_key=True)
    module_id = Column(ForeignKey("permissions.id"), primary_key=True)
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    method_access = Column(String(10), default='00000')
    
    def __repr__(self) -> str:
        return "<RolesPermission("\
            f"role_id={self.role_id}"\
            f"module_id={self.module_id}"\
            f"is_active={self.is_active}"\
            f"is_available={self.is_available}"\
            f"method_access={self.method_access}"\
            ")>"
            