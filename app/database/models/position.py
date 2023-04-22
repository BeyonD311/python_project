from sqlalchemy import String, SMALLINT, Column
from app.kernel.database import Base

class PositionModel(Base):

    __tablename__ = "position"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(40))

    def __repr__(self) -> str:
        return f"<Position(id={self.id}, " \
            f"name={self.name})>"