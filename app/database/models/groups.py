from sqlalchemy import String, SMALLINT, Column
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class GroupsModel(Base):

    __tablename__ = "groups"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(40))

    users = relationship("UserModel", secondary='user_groups', back_populates="group_user")

    def __repr__(self) -> str:
        return f"<Groups(id={self.id}, " \
            f"name={self.name})>"