from sqlalchemy import String, Column, SMALLINT
from app.kernel.database import Base

class StatusModel(Base):
    __tablename__ = "status_users"

    id = Column(SMALLINT, primary_key=True, autoincrement='ignore_fk')
    name = Column(String)
    color = Column(String, default=None)
    
    def __repr__(self) -> str:
        return f"<Status(id={self.id},name={self.name},color={self.color})>"

__all__ = ('StatusModel')