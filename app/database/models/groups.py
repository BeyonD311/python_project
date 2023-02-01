from sqlalchemy import String, SMALLINT, Column
from app.kernel.database import Base

class Groups(Base):

    __tablename__ = "groups"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(40))

    def __repr__(self) -> str:
        return f"<Groups(id={self.id}, " \
            f"name={self.name})>"