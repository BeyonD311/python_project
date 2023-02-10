from sqlalchemy import String, Column, SMALLINT
from app.kernel.database import Base

class StatusModel(Base):
    __tablename__ = "status_users"

    id = Column(SMALLINT, primary_key=True, autoincrement='ignore_fk')
    name = Column(String)
            
__all__ = ('StatusModel')