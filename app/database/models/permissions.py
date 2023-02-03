from sqlalchemy import String, SMALLINT, Column
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class PermissionsAccessModel(Base):
    
    __tablename__ = "permissions"

    id = Column(SMALLINT, primary_key=True)
    module_name = Column(String(40))
    name = Column(String(40))
    roles = relationship("RolesModel", secondary="roles_permission", back_populates="permissions")
    def __repr__(self) -> str:
        return f"<Departments(id={self.id}, " \
            f"module_name={self.module_name}"\
            f"name={self.name}"\
            f"methods_access={self.method_access})>"
