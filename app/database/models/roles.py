from sqlalchemy import String, SMALLINT, Column, Boolean
from app.kernel.database import Base

class Roles(Base):

    __tablename__ = "roles"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(40))
    is_active = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Roles(id={self.id}, " \
            f"name={self.name}, " \
            f"is_active={self.is_active})>"