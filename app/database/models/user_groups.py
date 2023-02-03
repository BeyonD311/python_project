from sqlalchemy import Column, BIGINT, SMALLINT, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class UserGroupsModel(Base):

    __tablename__ = "user_groups"
    id = Column('id', Integer, primary_key=True),
    user_id = Column(BIGINT, ForeignKey("users.id"), primary_key=True)
    group_id = Column(SMALLINT, ForeignKey("groups.id"), primary_key=True)  
