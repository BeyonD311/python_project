from sqlalchemy import String, BIGINT, Column
from app.kernel.database import Base


class ImagesModel(Base):

    __tablename__ = "images"

    id = Column(BIGINT, primary_key=True)
    path = Column(String)

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, path={self.path})>"