from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import SMALLINT
from sqlalchemy import Boolean
from sqlalchemy import Time
from app.kernel.database import Base

class StatusModel(Base):
    __tablename__ = "status_users"

    id = Column(SMALLINT, primary_key=True, autoincrement='ignore_fk')
    name = Column(String)
    color = Column(String, default=None)
    code = Column(String)
    behavior = Column(String)
    alter_name = Column(String)
    life_time = Column(Time, nullable=True)
    # is_active = Column(Boolean) 

    def __repr__(self) -> str:
        return f"<Status("\
        f"id={self.id},"\
        f"name={self.name},"\
        f"color={self.color}"\
        f"code={self.code}"\
        f"behavior={self.behavior}"\
        f"alter_name={self.alter_name}"\
        f"life_time={self.life_time}"\
        f")>"

__all__ = ('StatusModel') 