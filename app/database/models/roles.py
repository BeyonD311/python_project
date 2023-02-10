from sqlalchemy import String, SMALLINT, Column, Boolean
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class RolesModel(Base):

    __tablename__ = "roles"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(40))
    is_active = Column(Boolean, default=True)
    users = relationship("UserModel", secondary="user_roles", back_populates = "roles")
    permissions = relationship("PermissionsAccessModel", secondary="roles_permission", back_populates = "roles")
    permission_model = relationship("RolesPermission", cascade="save-update, merge," "delete, delete-orphan")
    def __repr__(self) -> str:
        return f"<Roles(id={self.id}, " \
            f"name={self.name}, " \
            f"is_active={self.is_active}"\
            f"permissions={self.permissions}"\
            f"permission_model={self.permission_model})>"

__all__ = ("RolesModel")