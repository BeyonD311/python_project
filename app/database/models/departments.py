from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import String, INTEGER, Column, Boolean, TIMESTAMP
from app.kernel.database import Base

class DepartmentsModel(Base):
    
    __tablename__ = "departments"

    id = Column(INTEGER, primary_key=True)
    name = Column(String(30))
    parent_department_id = Column(INTEGER, nullable=True)
    is_active = Column(Boolean, default=True)
    is_parent = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP,server_default=func.now())
    updated_at = Column(TIMESTAMP,server_default=func.now(),onupdate=func.now())
    users = relationship("UserModel", secondary='employees', back_populates="deparment")
    employees = relationship("EmployeesModel", back_populates="department", cascade="delete")
    def __repr__(self) -> str:
        return f"<Departments(id={self.id}, " \
            f"parent_department_id={self.parent_department_id}"\
            f"is_parent={self.is_parent}"\
            f"is_active={self.is_active}"\
            f"name={self.name})>"

__all__ = ('Departments')  