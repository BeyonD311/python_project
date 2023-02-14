from app.kernel.database import Base
from typing import List
from sqlalchemy import Column, String, ForeignKey, BIGINT, INTEGER, Boolean
from sqlalchemy.orm import relationship, Mapped


class EmployeesModel(Base):
    __tablename__ = "employees"

    id = Column(BIGINT, primary_key=True, autoincrement='ignore_fk')
    name = Column(String)
    department_id = Column(INTEGER, ForeignKey("departments.id"))
    user_id = Column(BIGINT, ForeignKey("users.id"))
    head_of_depatment = Column(Boolean, default=False)
    deputy_head = Column(Boolean, default=False)

    #relationship

    user = relationship("UserModel", uselist=False, back_populates="employee")
    department = relationship("DepartmentsModel", back_populates="employees")
    
    def __repr__(self) -> str:
        return  f"<Employees("\
                f"id={self.id}"\
                f"name={self.name}"\
                f"department_id={self.department_id}"\
                f"user_id={self.user_id}"\
                f"head_of_depatment={self.head_of_depatment}"\
                f"deputy_head={self.deputy_head}"\
                f")>"
    