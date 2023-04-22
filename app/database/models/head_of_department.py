from app.kernel.database import  Base
from sqlalchemy import Column
from sqlalchemy import BIGINT
from sqlalchemy import INTEGER
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.orm import relationship

class HeadOfDepartment(Base):

    __tablename__ = "head_of_departments"

    id = Column(BIGINT, primary_key=True, autoincrement='ignore_fk')
    department_id = Column(INTEGER, ForeignKey("departments.id"))
    head_of_department_id = Column(BIGINT, ForeignKey("users.id"), nullable=True)
    deputy_head_id = Column(BIGINT, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True) 
    created_at = Column(TIMESTAMP,server_default=func.now())
    department = relationship("DepartmentsModel") 
    

    def __repr__(self) -> str:
        return f"<HeadOfDepartment(id={self.id}"\
               f"department_id={self.department_id}"\
               f"head_of_department_id={self.head_of_department_id}"\
               f"deputy_head_id={self.deputy_head_id}"\
               f"is_active={self.is_active}"\
               f"created_at={self.created_at}"\
               f")>"