from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import SMALLINT
from sqlalchemy import Boolean
from app.kernel.database import Base

class StatusModel(Base):
    __tablename__ = "status_users"

    id = Column(SMALLINT, primary_key=True, autoincrement='ignore_fk')
    name = Column(String)
    color = Column(String, default=None)
    code = Column(String)
    # is_active = Column(Boolean) 

    def __repr__(self) -> str:
        return f"<Status("\
        f"id={self.id},"\
        f"name={self.name},"\
        f"color={self.color}"\
        # f"is_active={self.is_active}"\
        f")>"

__all__ = ('StatusModel') 