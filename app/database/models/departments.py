from sqlalchemy import String, SMALLINT, Column
from app.kernel.database import Base

class DepartmentsModel(Base):
    
    __tablename__ = "departments"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(30))

    def __repr__(self) -> str:
        return f"<Departments(id={self.id}, " \
            f"name={self.name})>"

__all__ = ('Departments')