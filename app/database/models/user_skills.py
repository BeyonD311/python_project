from sqlalchemy import Boolean, Column, ForeignKey, Integer
from app.kernel.database import Base

class UserSkillsModel(Base):
    __tablename__ = "user_skills"

    id = Column('id', Integer, primary_key=True),
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    role_id = Column(ForeignKey("skills.id"), primary_key=True)
            
__all__ = ('UserSkillsModel')