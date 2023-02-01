from sqlalchemy import Boolean, Column, ForeignKey
from app.kernel.database import Base

class RolesPermission(Base):

    __tablename__ = "roles_permission"

    role_id = Column(ForeignKey("roles.id"))
    module_id = Column(ForeignKey("module_id"))
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return "<RolesPermission("\
            f"role_id={self.role_id}"\
            f"module_id={self.module_id}"\
            f"is_active={self.is_active}"\
            f"is_available={self.is_available}"\
            ")>"
            