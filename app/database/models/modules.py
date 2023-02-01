from sqlalchemy import String, SMALLINT, Column
from app.kernel.database import Base

class Departments(Base):
    
    __tablename__ = "departments"

    id = Column(SMALLINT, primary_key=True)
    module_name = Column(String(40))
    name = Column(String(40))
    method_access = Column(String(10), default='0000')

    def __repr__(self) -> str:
        return f"<Departments(id={self.id}, " \
            f"module_name={self.module_name}"\
            f"name={self.name}"\
            f"methods_access={self.method_access})>"
